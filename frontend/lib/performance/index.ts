// Image Optimization
export { compressImage, generateBlurPlaceholder } from './imageCompression';
export { cdnImageLoader, CDN_CACHE_CONFIG } from './cdnImageLoader';
export { generateWidthSrcSet, generateDensitySrcSet, SIZES_PRESETS } from './srcSetGenerator';

// Font & CSS
export { CSS_STRATEGY } from './criticalCSS';
export { SUSPENSE_CONFIG } from './suspenseBoundaries';

// Code Splitting
export { createDynamicImport } from './dynamicImports';
export { ROUTE_BUNDLE_TARGETS } from './routeSplitting';
export { TREE_SHAKING_CONFIG } from './treeShaking';
export { MODULE_REPLACEMENTS, isOptimizedImport } from './moduleAliases';
export { PACKAGE_SIZE_LIMITS, LODASH_ALLOWED_IMPORTS, DATE_FNS_ALLOWED_IMPORTS } from './packageOptimization';

// Static Generation & ISR
export { REVALIDATE_TIMES, PAGE_STRATEGIES, type GenerationStrategy, type PageConfig } from './staticConfig';
export { getProductStaticParams, getCategoryStaticParams, getCollectionStaticParams, getBlogStaticParams, getHomepageData } from './staticGeneration';
export { onHoverPrefetch, PREFETCH_CONFIG, RESOURCE_HINTS, type ResourceHint } from './prefetch';
export { buildCache, getCachedCategories, getCachedSiteConfig } from './buildTimeCache';

// Caching & CDN
export { CACHE_POLICIES, generateETag, applyCacheHeaders } from './httpCacheHeaders';
export { CDN_CONFIG, purgeCDNCache } from './cdnConfig';
export { SW_CONFIG, registerServiceWorker } from './serviceWorkerConfig';
export { BUILD_VERSION, versionedUrl, VERSION_MANIFEST } from './cacheBusting';
export { getCached, setCached, removeCached, clearCache, CACHE_KEYS } from './localStorageCache';

// Monitoring & Testing
export { initWebVitals, onWebVital, WEB_VITAL_THRESHOLDS, PAGE_TARGETS, type WebVitalMetric } from './webVitals';
export { reportToAnalytics } from './analyticsIntegration';
export { ALL_PERFORMANCE_TESTS, HOMEPAGE_TEST, PRODUCT_PAGE_TEST, CATEGORY_PAGE_TEST, MOBILE_TEST } from './performanceTests';
