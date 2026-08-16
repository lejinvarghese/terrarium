/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false, // Required for Arwes
  images: {
    domains: ["localhost", "mutatedterrarium.com"],
  },
  experimental: {
    optimizePackageImports: ["@arwes/react"],
  },
  // Allow Cloudflare tunnel domain in development
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "Access-Control-Allow-Origin", value: "*" },
          {
            key: "Access-Control-Allow-Methods",
            value: "GET,POST,PUT,DELETE,OPTIONS",
          },
          { key: "Access-Control-Allow-Headers", value: "Content-Type" },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
