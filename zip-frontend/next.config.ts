import type { NextConfig } from "next";
import webpack from "webpack";

const nextConfig: NextConfig = {
  output: "standalone",
  reactStrictMode: true,
  swcMinify: true,
  webpack: (config) => {
    config.plugins.push(
      new webpack.IgnorePlugin({
        resourceRegExp: /^@react-native-async-storage\/async-storage$|^pino-pretty$/,
      })
    );
    return config;
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          {
            key: "X-Frame-Options",
            value: "DENY"
          },
          {
            key: "X-Content-Type-Options",
            value: "nosniff"
          },
          {
            key: "Referrer-Policy",
            value: "strict-origin-when-cross-origin"
          },
          {
            key: "Strict-Transport-Security",
            value: "max-age=31536000; includeSubDomains; preload"
          },
          {
            key: "Content-Security-Policy",
            value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob: https:; connect-src 'self' https: wss:; frame-ancestors 'none';"
          },
          {
            key: "X-XSS-Protection",
            value: "1; mode=block"
          },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()"
          }
        ]
      }
    ];
  }
};

export default nextConfig;
