import asyncio
import os
import tempfile
import urllib.parse
import socket
import ipaddress
from typing import List, Optional
from urllib.parse import parse_qs, urlparse
import httpx
from app.models.search import ResultCategory, SearchResult
import numpy as np


def is_safe_url(url: str) -> bool:
    """Validate that the URL is public and not a local/private network resource (prevents SSRF)."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False

        host = parsed.hostname
        if not host:
            return False

        # Preemptively check loopback and typical internal domains
        host_lower = host.lower()
        if host_lower in ("localhost", "127.0.0.1", "[::1]", "localhost.localdomain"):
            return False

        # Attempt to resolve the host to check the destination IP
        try:
            ip = socket.gethostbyname(host)
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
                return False
        except Exception:
            # If resolution failed, verify if the host string itself represents a private IP address
            try:
                ip_obj = ipaddress.ip_address(host)
                if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
                    return False
            except ValueError:
                # Not a literal IP address and hostname couldn't resolve; we let httpx fail natively
                pass

        return True
    except Exception:
        return False


class FaceMatcher:
    """
    Uses DeepFace to verify that search results match the uploaded photo.
    """

    async def filter_by_face(
        self,
        results: List[SearchResult],
        photo_bytes: bytes
    ) -> List[SearchResult]:
        """
        Compare uploaded face data against result thumbnails.
        For video results, check multiple YouTube thumbnail frames.
        """
        if not photo_bytes:
            return results

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(photo_bytes)
            reference_path = f.name

        try:
            filtered = []
            for result in results:
                # Task 6 update: If result category is video, use custom YouTube multi-frame checker
                if result.category == ResultCategory.VIDEO or result.category == "video":
                    video_id = self.extract_youtube_video_id(result.url)
                    if video_id:
                        matched = await self.check_video_for_face(video_id, photo_bytes)
                        result.face_matched = matched
                        if matched:
                            result.relevance_score = min(result.relevance_score + 0.15, 1.0)
                        filtered.append(result)
                        continue  # skip the normal thumbnail check for videos

                if not result.thumbnail:
                    filtered.append(result)
                    continue

                matched = None
                thumbnail_path = await self._download_image(result.thumbnail)
                if thumbnail_path:
                    try:
                        matched = await asyncio.get_running_loop().run_in_executor(
                            None,
                            self._compare_faces,
                            reference_path,
                            thumbnail_path
                        )
                    finally:
                        try:
                            os.unlink(thumbnail_path)
                        except Exception:
                            pass

                result.face_matched = matched

                if matched is True:
                    result.relevance_score = min(result.relevance_score + 0.15, 1.0)
                elif matched is False:
                    result.relevance_score = max(result.relevance_score - 0.3, 0.0)

                filtered.append(result)

            filtered.sort(
                key=lambda r: (
                    2 if r.face_matched is True else (1 if r.face_matched is None else 0),
                    r.relevance_score
                ),
                reverse=True
            )
            return filtered

        finally:
            try:
                os.unlink(reference_path)
            except Exception:
                pass

    def extract_youtube_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URLs.
        Handle these formats:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        Use urllib.parse.urlparse and urllib.parse.parse_qs
        Return the video ID string or None if not found
        """
        if not url:
            return None

        try:
            parsed = urlparse(url)
            hostname = (parsed.netloc or "").lower()

            if "youtu.be" in hostname:
                video_id = parsed.path.strip("/").split("/")[0]
                return video_id or None

            if "youtube.com" in hostname:
                query_params = parse_qs(parsed.query)
                video_id = query_params.get("v", [None])[0]
                if video_id:
                    return video_id

                path_parts = [part for part in parsed.path.split("/") if part]
                if len(path_parts) >= 2 and path_parts[0] in {"embed", "shorts", "live"}:
                    return path_parts[1]
        except Exception as e:
            print(f"[FaceMatcher] Error extracting video ID: {e}")

        return None

    async def check_video_for_face(self, video_id: str, photo_bytes: bytes) -> bool:
        """
        Check if a person's face appears in a YouTube video by checking thumbnails.
        Download these thumbnail URLs in order, stop at first successful download:
        - https://img.youtube.com/vi/{video_id}/maxresdefault.jpg
        - https://img.youtube.com/vi/{video_id}/hqdefault.jpg
        - https://img.youtube.com/vi/{video_id}/mqdefault.jpg
        Save uploaded photo to temp file.
        For each downloaded thumbnail, run self._compare_faces(reference_path, thumbnail_path)
        If ANY thumbnail matches, return True immediately.
        Clean up all temp files.
        Return False if no match found.
        """
        if not video_id or not photo_bytes:
            return False

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(photo_bytes)
            reference_path = f.name

        thumbnail_urls = [
            f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
            f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
            f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
        ]

        try:
            downloaded_path = None
            for thumbnail_url in thumbnail_urls:
                path = await self._download_image(thumbnail_url)
                if path:
                    downloaded_path = path
                    break

            if downloaded_path:
                try:
                    matched = await asyncio.get_running_loop().run_in_executor(
                        None,
                        self._compare_faces,
                        reference_path,
                        downloaded_path
                    )
                finally:
                    try:
                        os.unlink(downloaded_path)
                    except Exception:
                        pass

                if matched:
                    return True

            return False
        finally:
            try:
                os.unlink(reference_path)
            except Exception:
                pass

    def _get_insight_app(self):
        if not hasattr(self, '_insight_app'):
            try:
                from insightface.app import FaceAnalysis
                self._insight_app = FaceAnalysis(name='buffalo_l')
                self._insight_app.prepare(ctx_id=0, det_size=(640, 640))
            except ImportError:
                print("[FaceMatcher] InsightFace not available, using DeepFace only")
                self._insight_app = None
        return self._insight_app

    def _compare_faces_insight(self, img1_path: str, img2_path: str) -> bool:
        try:
            import insightface
            from insightface.app import FaceAnalysis
            import numpy as np
            app = self._get_insight_app()
            if app is None:
                return False
            import cv2
            img1 = cv2.imread(img1_path)
            img2 = cv2.imread(img2_path)
            if img1 is None or img2 is None:
                return False
            faces1 = app.get(img1)
            faces2 = app.get(img2)
            if not faces1 or not faces2:
                return False
            import numpy as np
            emb1 = faces1[0].normed_embedding
            emb2 = faces2[0].normed_embedding
            similarity = float(np.dot(emb1, emb2))
            return similarity > 0.4
        except Exception as e:
            print(f"[InsightFace] Error: {e}")
            return False

    def _compare_faces(self, img1_path: str, img2_path: str) -> bool:
        try:
            return self._compare_faces_insight(img1_path, img2_path)
        except Exception:
            pass
        try:
            from deepface import DeepFace
            result = DeepFace.verify(
                img1_path=img1_path,
                img2_path=img2_path,
                model_name="VGG-Face",
                enforce_detection=False
            )
            return result.get("verified", False)
        except Exception as e:
            print(f"[FaceMatcher] Both methods failed: {e}")
            return False

    async def _download_image(self, url: str) -> Optional[str]:
        """Download image from URL to temp file. Returns file path or None."""
        if not is_safe_url(url):
            print(f"[FaceMatcher] SSRF blocked attempt to download unsafe URL: {url}")
            return None

        try:
            async with httpx.AsyncClient(timeout=8) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    suffix = ".jpg"
                    if "png" in url:
                        suffix = ".png"
                    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
                        f.write(resp.content)
                        return f.name
        except Exception as e:
            print(f"[FaceMatcher] Image download failed: {e}")
        return None
