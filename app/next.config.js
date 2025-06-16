/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  images: {
    unoptimized: true,
  },
  basePath: process.env.NODE_ENV === 'production' ? '/mapbench.live' : '',
  assetPrefix: process.env.NODE_ENV === 'production' ? '/mapbench.live' : '',
  trailingSlash: true,
}

module.exports = nextConfig