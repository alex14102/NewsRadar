/** @type {import('next').NextConfig} */
const isGHPages = process.env.GITHUB_PAGES === "true";

const nextConfig = {
  ...(isGHPages
    ? {
        output: "export",
        basePath: "/NewsRadar",
        assetPrefix: "/NewsRadar",
      }
    : {
        async rewrites() {
          return [
            {
              source: "/api/:path*",
              destination: "http://localhost:8000/api/:path*",
            },
          ];
        },
      }),
  images: {
    unoptimized: true,
    remotePatterns: [
      { protocol: "https", hostname: "**" },
      { protocol: "http", hostname: "**" },
    ],
  },
};

export default nextConfig;
