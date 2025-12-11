/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false, // Required for Arwes
  images: {
    domains: ['localhost'],
  },
  experimental: {
    optimizePackageImports: ['@arwes/react'],
  },
}

module.exports = nextConfig
