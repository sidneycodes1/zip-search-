import asyncio
import json
import re
import tempfile
import os
import sys
from typing import List, Optional
from app.models.search import SearchResult, ResultCategory


class SocialSearchService:
    """
    Wraps the Maigret CLI tool (https://github.com/soxoj/maigret)
    to find social media profiles across 3000+ sites.

    Install: pip install maigret
    """

    async def search(self, name: str, description: Optional[str] = None) -> List[SearchResult]:
        """
        Derives likely usernames from the person's name and searches
        social platforms for matching profiles.
        """
        usernames = self._derive_usernames(name)
        results = []

        for username in usernames[:3]:  # Limit to 3 variants to avoid timeout
            profile_results = await self._run_maigret(username)
            results.extend(profile_results)

        # Deduplicate by URL
        seen_urls = set()
        deduped = []
        for r in results:
            if r.url not in seen_urls:
                seen_urls.add(r.url)
                deduped.append(r)

        return deduped

    def _derive_usernames(self, name: str) -> List[str]:
        """
        Generate likely username variants from a full name.
        e.g. "John Doe" → ["johndoe", "john.doe", "john_doe", "jdoe"]
        """
        # Clean name: keep only letters, numbers, spaces
        cleaned_name = re.sub(r"[^a-zA-Z0-9\s]", "", name)
        parts = cleaned_name.lower().split()
        if not parts:
            return []

        if len(parts) < 2:
            base_variants = [parts[0]]
        else:
            first, last = parts[0], parts[-1]
            base_variants = [
                f"{first}{last}",
                f"{first}.{last}",
                f"{first}_{last}",
                f"{first[0]}{last}",
            ]

        # Strictly sanitize variants to avoid argument injection (no leading hyphens, only valid username chars)
        sanitized = []
        for v in base_variants:
            # Must start with alphanumeric and only contain alphanumeric, dot, underscore, hyphen
            if re.match(r"^[a-zA-Z0-9][a-zA-Z0-9\._-]{0,31}$", v):
                sanitized.append(v)

        return sanitized

    async def _run_maigret(self, username: str) -> List[SearchResult]:
        """Run maigret CLI as subprocess and parse JSON output."""
        # Double check to prevent empty or invalid usernames passing through to CLI
        if not username or not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9\._-]{0,31}$", username):
            return []

        results = []

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, f"{username}.json")

            cmd = [
                sys.executable,
                "-m", "maigret",
                username,
                "--json", output_file,
                "--timeout", "10",
                "--no-color",
                "-q"  # quiet mode
            ]

            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await asyncio.wait_for(proc.communicate(), timeout=20)

                if os.path.exists(output_file):
                    with open(output_file) as f:
                        data = json.load(f)

                    for site, info in data.items():
                         if info.get("status") == "Claimed":
                            url = info.get("url_user", "")
                            if url:
                                results.append(SearchResult(
                                    title=f"{username} on {site}",
                                    url=url,
                                    source=site,
                                    category=ResultCategory.SOCIAL,
                                    relevance_score=0.7
                                ))

            except asyncio.TimeoutError:
                print(f"[SocialService] Maigret timed out for {username}")
            except FileNotFoundError:
                print("[SocialService] Maigret not installed. Run: pip install maigret")
            except Exception as e:
                print(f"[SocialService] Error: {e}")

        return results
