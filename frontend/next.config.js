const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Tell Next.js this project's root is the frontend folder, not the monorepo root.
  // This prevents the wrong package-lock.json from being picked up, which causes
  // "Loading chunk ... failed" errors due to mismatched asset paths.
  outputFileTracingRoot: path.join(__dirname),
};

module.exports = nextConfig;
