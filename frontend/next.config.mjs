/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: process.env.BACKEND_INTERNAL_URL || 'http://145.223.22.175:8008/api/v1/:path*',
      },
    ];
  },
};

export default nextConfig;
