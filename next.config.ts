import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ['lucide-react'],
  // Ensure we can access the filesystem in server components
  serverExternalPackages: ['gray-matter'],
};

export default nextConfig;
