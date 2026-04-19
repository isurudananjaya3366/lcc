/**
 * Webpack Chunking Configuration
 *
 * Applied via next.config.js webpack() callback.
 * Separates vendor and common code into cacheable chunks.
 */

import type { Configuration } from 'webpack';

export function configureChunking(config: Configuration): Configuration {
  if (!config.optimization) config.optimization = {};

  config.optimization.splitChunks = {
    chunks: 'all',
    minSize: 20_000,
    maxSize: 244_000,
    minChunks: 1,
    maxAsyncRequests: 30,
    maxInitialRequests: 30,
    cacheGroups: {
      // Vendor chunk — large stable libraries
      vendor: {
        test: /[\\/]node_modules[\\/](react|react-dom|next|@tanstack)[\\/]/,
        name: 'vendor',
        chunks: 'all',
        priority: 20,
        reuseExistingChunk: true,
      },

      // UI framework chunk
      ui: {
        test: /[\\/]node_modules[\\/](@radix-ui|lucide-react|class-variance-authority|clsx)[\\/]/,
        name: 'ui-vendor',
        chunks: 'all',
        priority: 15,
        reuseExistingChunk: true,
      },

      // Common chunk — shared across 2+ routes
      common: {
        name: 'common',
        minChunks: 2,
        chunks: 'all',
        priority: 10,
        reuseExistingChunk: true,
      },
    },
  };

  return config;
}
