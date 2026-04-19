# Session Status - LankaCommerce Cloud POS

> **Last Updated:** Session 69/70 — SP11 DEEP AUDITED (0 gaps) + SP12 DEEP AUDITED (1 gap) + SP13 Performance Optimization DEEP AUDITED (94 tasks, 3 gaps fixed [dynamicImports.ts→.tsx, lazyComponents.ts→.tsx, webpack chunking wired into next.config.js], SP13_PERFORMANCE_OPTIMIZATION_AUDIT_REPORT.md)
> **Purpose:** Complete handoff document for the next chat session. This file contains ALL context needed to continue work without the previous chat's memory.

---

## CRITICAL BACKGROUND: The Document Misunderstanding Issue

### What Happened

The project follows a `Document-Series/` folder structure with Phases and SubPhases (SP01-SP12+). Each document describes specific tasks to implement.

**The Problem:** A previous chat session (Session 1) implemented SP03 through SP07 as **config functions** (simple Python functions that return configuration dictionaries) instead of **real Django code**. This resulted in ~620 config functions with 4956 passing tests -- but NO actual working Django code.

**The Fix (Session 2):** Created REAL implementations for SP03-SP07 alongside the config functions. Config functions and their tests were KEPT untouched.

**Session 3:** Completed all remaining SP07 tasks, implemented full SP08 (Celery Task Queue), SP09 (Caching Layer), fixed all 40 failing tenant tests, added model CRUD tests, wired Users API URLs.

---

## Current Progress

```
...
Phase-08_Webstore-Ecommerce-Platform/SubPhase-03_Storefront-Catalog (ALL 96 tasks complete, DEEP AUDITED, 5 audit fixes, 70 impl files: 6 routes + 2 lib/store files + 62 components — Group A: Catalog Shell (8 catalog components + lib/store/categories.ts + lib/store/collections.ts) + Group B: Product Cards (12 components + GridConfig.ts CREATED + CardVariantSelect.tsx CREATED + QuickView wired) + Group C: Filter Sidebar (13 filter components) + Group D: Toolbar & Pagination (8 components) + Group E: Category & Collection (11 components) + Group F: Empty States & Quick View (8 components, QuickViewContent real data fixed), 0 TS errors, SP03_STOREFRONT_CATALOG_AUDIT_REPORT.md, 6 groups A-F)
Phase-08_Webstore-Ecommerce-Platform/SubPhase-04_Product-Detail-Page (ALL 94 tasks complete, DEEP AUDITED, 9 audit fixes, 61 components + 5 routes + backend store API created at api/v1/store/ [products list/detail/related/reviews + categories, AllowAny], 0 TS errors in product detail files, SP04_AUDIT_REPORT.md, 6 groups A-F)
Phase-08_Webstore-Ecommerce-Platform/SubPhase-05_Search-Functionality (ALL 92 tasks complete, DEEP AUDITED, 4 audit fixes [SearchInput forwardRef, SearchForm autocomplete integration, LoadMoreButton created, layout aside removed], 45 search files: SearchInput + Autocomplete + RecentSearches + SearchResults + SearchFilters + EdgeCases + hooks + services + routes, 0 TS errors entire frontend, SP05_AUDIT_REPORT.md, 6 groups A-F)
Phase-08_Webstore-Ecommerce-Platform/SubPhase-06_Shopping-Cart (ALL 96 tasks complete, DEEP AUDITED, 3 audit fixes [MiniCartItemRemove.tsx created, StoreHeader wired to CartIconButton+Zustand, MiniCartItemCard fixed to use MiniCartItemRemove], 43 cart files: stores/store/cart.ts [Zustand+Immer+Persist] + MiniCart [9 components] + CartPage [12 components] + QuantitySelector [5] + CartItem [5] + Coupon [4] + CartSummary [4] + hooks + services + 3 routes, 0 TS errors entire frontend, SP06_AUDIT_REPORT.md, 6 groups A-F)
Phase-08_Webstore-Ecommerce-Platform/SubPhase-07_Checkout-Flow (ALL 98 tasks complete, DEEP AUDITED, 5 TS fixes [StepProgress optional chaining, InformationStep/ShippingStep zodResolver type compat, checkoutSchemas enum fix, usePreFillInfo type widening], 65+ checkout files: stores/store/checkout.ts [Zustand+Immer+Persist] + CheckoutLayout [7] + Information [11] + Shipping [17] + Payment [14] + Review [11] + Confirmation [5] + OrderSidebar [9] + orderService + 6 routes + useCheckoutNavigation + checkoutSchemas + data/srilanka [4 files] + checkout.types.ts, Sri Lanka localized: +94 phone, Province→District→City cascade, LKR ₨, PayHere/KOKO/MintPay/COD, 0 checkout TS errors, SP07_AUDIT_REPORT.md, 6 groups A-F)
Phase-08_Webstore-Ecommerce-Platform/SubPhase-08_Customer-Authentication (ALL 94 tasks complete, DEEP AUDITED, 3 audit gaps fixed [AppleButton.tsx created, GuestGuard applied to LoginPage+RegisterPage, Social/index.ts + auth/index.ts exports updated], 37+ auth files: stores/store/auth.ts [useStoreAuthStore Zustand+Persist] + Login [7] + Register [7] + ForgotPassword [5] + ResetPassword [4] + Social [6 incl AppleButton] + Root guards+utils [8] + services/storefront/authService.ts + tokenService.ts + hooks/useAuth.ts + useTokenRefresh.ts + types/storefront/auth.types.ts + 5 validations, JWT cookie auth, RememberMe 30d, OTP WhatsApp flow, session expiry warning, cart merge on login, 0 TS errors entire frontend, 0 Django issues, SP08_AUDIT_REPORT.md, 6 groups A-F)
Phase-08_Webstore-Ecommerce-Platform/SubPhase-09_Customer-Portal (ALL 96 tasks complete, DEEP AUDITED, 8 audit gaps fixed [OrdersHeader created, OrderStatusSection created, AddressesHeader created, WishlistHeader created, ReviewsHeader created, usePortal.ts hook created, ContactSupport phone env-var fixed, barrel exports updated], 71 portal files: Layout [5] + Dashboard [6] + Orders [23 incl 2 new] + Addresses [9 incl 1 new] + Wishlist [6 incl 1 new] + Reviews [8 incl 1 new] + Settings [5] + portalService.ts + usePortal.ts [NEW] + portal.types.ts + addressSchema + profileSchema + PortalTestIds, auth-protected, SR Lanka locale, wishlist→cart integration, 0 TS errors entire frontend, 0 Django issues, SP09_CUSTOMER_PORTAL_AUDIT_REPORT.md, 6 groups A-F)
Phase-08_Webstore-Ecommerce-Platform/SubPhase-11_Static-Pages-CMS (ALL 94 tasks complete, DEEP AUDITED, 0 gaps found, 69+ cms files: Layout [5: PageLayout+PageHeader+PageContentArea+PageLoading+PageNotFound] + About [6: Hero+Story+Mission+Values+Team+AboutPage] + Content [12: RichContent+RichTextRenderer+BlockRenderer+ProseStyles+CodeBlock+ImageBlock+ImageCaption+VideoBlock+QuoteBlock+ListBlock+TableBlock+ContentSpacing] + Template [6: StaticPageTemplate+PageBreadcrumb+PageTitle+PageLastUpdated+RelatedPages+PageSidebar] + Contact [5: ContactPage+ContactInfo+WhatsAppContact+ContactForm+FormSuccess] + FAQ [5: FAQPage+FAQSearch+FAQCategories+FAQAccordion+FAQItem] + Policy [7: PolicyTemplate+TableOfContents+AnchorHeading+TermsPage+PrivacyPage+ReturnsPage+ShippingPage] + Blog [13: BlogListPage+BlogDetailPage+BlogHeader+BlogCategories+BlogGrid+BlogPostCard+BlogPagination+PostFeaturedImage+PostMeta+PostHeader+PostContent+PostShareButtons+RelatedPosts] + cmsService.ts + cms.types.ts + contactSchema.ts + CMSTestIds.ts + 10 routes [about+contact+faq+terms+privacy+returns+shipping+blog+blog/[slug]+[slug]], generateMetadata, +94 WhatsApp, LKR rates, 0 TS errors, 0 Django issues, SP11_STATIC_PAGES_CMS_AUDIT_REPORT.md, 6 groups A-F)
Phase-08_Webstore-Ecommerce-Platform/SubPhase-12_SEO-Implementation (ALL 92 tasks complete, DEEP AUDITED, 1 gap fixed [sitemap.ts missing category+collection URLs — added categoryPages [6 slugs: spices/tea/handcrafts/home-decor/food-beverages/health-wellness at /products?category=slug, priority 0.75] + collectionPages [5 slugs: new-arrivals/best-sellers/featured/sale/gifts at /collections/slug, priority 0.7]], lib/seo/ [10 files: types+config+base+metadata+openGraph+twitterCard+jsonLd+schemas+canonical+index] + components/seo/ [JsonLdScript+SEOPreview+GooglePreview+SocialPreview+TitleLengthCheck+DescriptionLengthCheck+SEOTestIds+index barrel] + app/sitemap.ts [static+product+category+collection+blog URLs, priority/changefreq/lastmod] + app/robots.ts [wildcard+Googlebot+Googlebot-Image rules, disallow /account/+/cart+/checkout/+/api/+/_next/+/admin/], constructMetadata() central helper, 9 JSON-LD generators [Org+WebSite+SearchAction+Product+Breadcrumb+Article+FAQ+ContactPage+LocalBusiness+CollectionPage], 8 canonical helpers [getCanonicalUrl+getHomepageCanonical+getProductCanonical+getCategoryCanonical+getBlogCanonical+getPaginationCanonical+getFilterCanonical+getAlternateLinks], SEO_TEST_IDS constants, seoConfig [Ceylon Store, store.lk, en_US, @ceylonstore], OG 1200x630, Twitter summary_large_image, LKR currency in product schema, Colombo GeoCoordinates in LocalBusiness, 0 TS errors, 0 Django issues, SP12_SEO_IMPLEMENTATION_AUDIT_REPORT.md, 6 groups A-F)
Phase-08_Webstore-Ecommerce-Platform/SubPhase-10_Theme-Engine (ALL 92 tasks complete, DEEP AUDITED, 0 gaps found, 70+ theme files: Provider [ThemeProvider+ThemeContext+CSSVariablesInjector] + Colors [18 components: ColorPicker+Presets+ContrastCheck+GeneratePalette+ApplyColors+Previews+HexInput+ColorReset] + Typography [15 components: FontSelector+GoogleFonts+FontLoader+FontPreview+ApplyFonts+ResetTypography+FontList+FontFallbacks] + Logo [15 components: LogoUpload+FaviconUpload+MobileLogo+HeroImage+HeroCTAButton+ImageCropper+ImageOptimization+BannerSection+DeleteImage] + Homepage [14 components: HomepageBuilder+SectionList+DragHandle+SectionConfigs+AddSection+SaveSectionOrder+HomepagePreview+types.ts] + Preview [10 components: ThemePreviewPanel+PreviewFrame+Desktop/Mobile+PreviewRefresh+SaveTheme+PublishTheme+DraftMode+UndoChanges] + stores/store/theme.ts [Zustand] + hooks/useTheme + services/themeService + types/theme.types.ts + lib/theme [validation+cache+defaultTheme] + styles/theme [defaults.ts+variables.css], 0 TS errors, 6 groups A-F, SP08_SP10_THEME_ENGINE_AUDIT_REPORT.md)
Phase-08_Webstore-Ecommerce-Platform/SubPhase-13_Performance-Optimization (ALL 94 tasks complete, DEEP AUDITED, 3 gaps fixed [dynamicImports.ts→.tsx renamed, lazyComponents.ts→.tsx renamed, webpack chunking callback wired into next.config.js for vendor+ui-vendor+common cacheGroups], 50+ performance files: next.config.js [AVIF/WebP formats, deviceSizes, imageSizes, 30d minimumCacheTTL, remotePatterns, webpack splitChunks callback] + OptimizedImage+ImageSkeleton+ImageFallback + config/images.config.ts [PRODUCT_IMAGE_SIZES+THUMBNAIL_SIZES+HERO_IMAGE_CONFIG] + styles/fonts/ [Inter+Playfair Display next/font, fontVariables.css] + Skeleton [BaseSkeleton+ProductSkeleton+GridSkeleton+ContentSkeleton] + LoadingSpinner+PageTransition + lib/performance/ [29 files: webVitals+dynamicImports+lazyComponents+prefetch+staticGeneration+staticConfig+buildTimeCache+webpackChunking+routeSplitting+treeShaking+moduleAliases+packageOptimization+imageCompression+cdnImageLoader+srcSetGenerator+criticalCSS+suspenseBoundaries+iconOptimization+httpCacheHeaders+cdnConfig+serviceWorkerConfig+cacheBusting+localStorageCache+analyticsIntegration+performanceTests+monitoringTestIds+cacheTestIds+staticTestIds+index] + config/cache.config.ts [STALE_TIMES+CACHE_TIMES+INVALIDATION_MAP] + config/performance.config.ts [PERFORMANCE_BUDGETS] + app/api/revalidate/route.ts [on-demand ISR] + app/(storefront)/loading.tsx + scripts/analyze-bundle.js+lighthouse-ci.js + .lighthouserc.js, 0 TS errors, 0 Django issues, SP13_PERFORMANCE_OPTIMIZATION_AUDIT_REPORT.md, 6 groups A-F)
```

### Next Document to Implement

```
Phase-08_Webstore-Ecommerce-Platform/SubPhase-14_Marketing-Features (Next SubPhase)
```

---

## IMPORTANT: Docker-Only Development

We use Docker for **literally everything**. There is NO local SQLite database usage.

- **Development DB:** Docker PostgreSQL 15-alpine (lcc-postgres container, port 5432)
- **Test DB:** `lankacommerce_test` database on the same Docker PostgreSQL instance
- **Connection Pooling:** PgBouncer (lcc-pgbouncer container, port 6432) -- used by backend app, NOT by tests
- **Cache/Broker:** Docker Redis 7-alpine (lcc-redis container, port 6379)
- **Test Settings:** `config.settings.test_pg` -- uses `django_tenants.postgresql_backend` connecting to Docker `db` service
- **pytest.ini:** `DJANGO_SETTINGS_MODULE = config.settings.test_pg`

### Docker Containers (all running)

| Container     | Image               | Port | Status  |
| ------------- | ------------------- | ---- | ------- |
| lcc-postgres  | postgres:15-alpine  | 5432 | Healthy |
| lcc-pgbouncer | edoburu/pgbouncer   | 6432 | Healthy |
| lcc-redis     | redis:7-alpine      | 6379 | Healthy |
| lcc-backend   | custom Django image | 8000 | Running |

### Database Credentials

- **Main DB:** `lankacommerce` (owner: postgres, app user: lcc_user)
- **Test DB:** `lankacommerce_test` (owner: lcc_user -- required for pytest to drop/recreate)
- **User:** `lcc_user` / `dev_password_change_me`
- **Extensions:** uuid-ossp, hstore, pg_trgm, pg_stat_statements

---

## Architecture Notes

### AUTH_USER_MODEL = "platform.PlatformUser"

`PlatformUser` (292 lines) at `apps/platform/models/user.py`:

- Email-based login (no username field)
- UUID primary key
- Platform roles
- All business apps reference `settings.AUTH_USER_MODEL`

The `users` app provides **complementary** tenant-scoped models (profile, preferences, audit trail, RBAC roles/permissions) -- it does NOT replace PlatformUser.

### Multi-Tenancy (django-tenants)

- `TENANT_MODEL = "tenants.Tenant"` and `TENANT_DOMAIN_MODEL = "tenants.Domain"` (in `config/settings/database.py`)
- Database engine: `django_tenants.postgresql_backend`
- Schemas: `public` (shared apps) + per-tenant schemas
- `SHARED_APPS` and `TENANT_APPS` in `config/settings/database.py`
- Custom router: `apps.tenants.routers.LCCDatabaseRouter`

### Existing Mixins and Managers (core/mixins.py, core/managers.py)

- **Mixins:** `UUIDMixin`, `TimestampMixin` (created_on/updated_on -- NOT created_at), `AuditMixin`, `StatusMixin`, `SoftDeleteMixin`
- **Managers:** `ActiveQuerySet`, `SoftDeleteQuerySet`, `AliveQuerySet`, `ActiveManager`, `SoftDeleteManager`, `AliveManager`

---

## Frontend TypeScript & Lint Checking

### TypeScript Check Commands

**Working command** (run from the `frontend/` directory):

```bash
node node_modules/typescript/bin/tsc --noEmit --pretty false
```

**Why NOT `npx tsc` or `pnpm tsc` or `.bin/tsc`?**

- The `.bin/tsc` symlink is **missing** from `node_modules/.bin/` in this project
- Must use the full path: `node node_modules/typescript/bin/tsc`
- `npx tsc` and `pnpm exec tsc` will also fail for the same reason

**Why NOT pipe output through `grep` or `| head`?**

- The terminal returns "stdout is not a tty" when piping tsc output
- Workaround: Write a `.cjs` helper script (NOT `.js` — the project uses `"type": "module"` which treats all `.js` as ESM)

**Temp helper script pattern** (create `frontend/check_ts.cjs`, delete when done):

```js
// check_ts.cjs — CommonJS (.cjs extension required due to "type": "module" in package.json)
const { spawnSync } = require("child_process");
const r = spawnSync("node", ["node_modules/typescript/bin/tsc", "--noEmit", "--pretty", "false"], {
  encoding: "utf8",
  maxBuffer: 10 * 1024 * 1024,
});
const out = (r.stdout || "") + (r.stderr || "");
const lines = out.split("\n").filter((l) => l.includes("error TS"));
process.stdout.write("Total errors: " + lines.length + "\n");
lines.forEach((l) => process.stdout.write(l + "\n"));
```

Run: `node check_ts.cjs` then `rm check_ts.cjs` when done.

### Installing Packages (pnpm Workspace Quirk)

- `pnpm add <package>` **fails** with "adding to workspace root" error
- **Correct approach:** Edit `frontend/package.json` devDependencies directly, then run `pnpm install` from `frontend/`
- The workspace root IS `frontend/` (it contains `pnpm-workspace.yaml` + `pnpm-lock.yaml`)
- Filter flags like `--filter .` or `--filter @lankacommerce/frontend` also fail in this setup

### ESLint

- ESLint is configured in the project
- There is **no `lint` npm script** currently in `frontend/package.json`
- Run manually: `node node_modules/eslint/bin/eslint.js . --ext .ts,.tsx`

---

## Docker Frontend Container

### Rebuilding the Frontend Container (After Package Changes)

**Quick command:**

```bash
make rebuild-frontend
```

**Manual steps (if make isn't available):**

```bash
docker compose stop frontend
docker compose rm -f frontend
docker volume rm $(docker volume ls -q --filter name=pos_) 2>/dev/null || true
docker compose build --no-cache frontend
docker compose up -d frontend
```

**Why remove volumes?** — The anonymous volumes `/app/node_modules` and `/app/.next` contain stale data from the previous broken build. They must be removed for the rebuild to install fresh packages.

### Checking Frontend Container Logs

```bash
make logs-frontend
# or
docker compose logs -f frontend
```

---

## What Was Completed This Session (Session 66)

### SP05 Search Functionality — Deep Audit & Fixes

**Phase-08_Webstore-Ecommerce-Platform/SubPhase-05_Search-Functionality — 92 tasks, 6 groups (A-F) — DEEP AUDITED**

Deep audit of all 92 tasks in the Search Functionality SubPhase. 4 gaps found and immediately fixed. 0 TypeScript errors across entire frontend after fixes.

**Audit Gaps Found & Fixed (4 fixes):**

1. **SearchInput missing forwardRef** → Converted to `forwardRef`, added `onFocus`/`onBlur` props
2. **SearchForm not wired to Autocomplete/RecentSearches** → Full rewrite — integrated dropdowns, `addSearch` on submit, dynamic imports for SSR safety
3. **LoadMoreButton component missing** → Created `LoadMoreButton.tsx` with all states (loading/hasMore/allLoaded); exported from SearchResults and root barrel
4. **search/layout.tsx had empty aside column** → Removed empty aside; filter sidebar already rendered inside `SearchResultsContainer`

**Tests:** TypeScript 0 errors (entire frontend). Django system check: 0 issues.
**Audit Report:** SP05_AUDIT_REPORT.md created with per-task compliance matrix and certification

**File Counts:** 45 search files (6 component dirs + hooks + services + routes)

---

### SP04 Product Detail Page — Deep Audit & Fixes

**Phase-08_Webstore-Ecommerce-Platform/SubPhase-04_Product-Detail-Page — 94 tasks, 6 groups (A-F) — DEEP AUDITED**

Deep audit of all 94 tasks in the Product Detail Page SubPhase. 9 frontend gaps found and immediately fixed. Backend store API created from scratch. 0 TypeScript errors in product detail files.

**Audit Gaps Found & Fixed (9 fixes):**

1. **JSON-LD BreadcrumbList missing** → Added `buildBreadcrumbJsonLd()` + `<Script>` tag in page.tsx
2. **MobileImageSwiper not wired** → Added `sm:hidden` / `hidden sm:block` split in Gallery.tsx
3. **ProductSKU no copy-to-clipboard** → Rewrote with clipboard API + sonner toast + icon toggle
4. **ShortDescription no expand/collapse** → Rewrote with truncate-at-200 + Read more/less button
5. **CartActions no variant price update** → Added `PriceDisplay` re-render on variant change
6. **AddToCartButton no toast** → Added sonner `toast.success()` with "View Cart" action (4s)
7. **ReviewsTab no pagination** → Added PAGE_SIZE=5, Load more button, All loaded sentinel
8. **WriteReviewButton was console.log stub** → Rewrote with auth check, toast, sign-in redirect
9. **CrossSellSection never rendered** → Added import + render in ProductDetailContainer

**Backend Store API Created:**

- `apps/webstore/api/` — `StoreProductViewSet` (lookup_field='slug', AllowAny), `StoreCategoryViewSet`
- Endpoints: `GET /api/v1/store/products/`, `/{slug}/`, `/{slug}/related/`, `/{slug}/reviews/`, `/categories/`
- Django system check: 0 issues

**File Counts:** 61 product components + 5 route files + 4 backend API files
**TypeScript:** 0 errors in product detail files (25 pre-existing errors in unrelated catalog files)
**Audit Report:** SP04_AUDIT_REPORT.md created with per-task compliance matrix and certification

---

### SP03 Storefront Catalog — Full Implementation & Deep Audit

**Phase-08_Webstore-Ecommerce-Platform/SubPhase-03_Storefront-Catalog — 96 tasks, 6 groups (A-F) — DEEP AUDITED**

Complete implementation of the Storefront Catalog module: product listing with filters, sorting, grid/list view, category and collection pages, quick view modal with real product data, and all empty/error states. All 96 tasks implemented, 5 gaps found and fixed during audit. 0 TypeScript errors across 70 implementation files.

**Implementation Summary:**

- **Group A (Tasks 1–16) — Routes & Catalog Shell:** 6 route files (layout, page, loading, error, category/[slug], collection/[slug]), 8 catalog shell components (CatalogPage, CatalogHeader, Breadcrumb, CatalogTitle, ProductCount, CatalogContent, SidebarContainer, GridContainer), 2 lib/store helpers (categories.ts, collections.ts) with real API calls
- **Group B (Tasks 17–36) — Product Grid & Cards:** ProductGrid, ProductCard (with QuickView state), CardImage, CardBadge, CardQuickActions, CardContent, CardCategory, CardTitle, CardRating, CardPrice, CardAddToCart, ProductCardSkeleton — plus GridConfig.ts (grid constants) and CardVariantSelect.tsx (3 display modes: dropdown/swatches/buttons)
- **Group C (Tasks 37–54) — Filter Sidebar:** FilterSidebar, FilterSection, CategoryFilter, PriceRangeFilter, AttributeFilter, ColorFilter, SizeFilter, BrandFilter, AvailabilityFilter, ClearAllFilters, MobileFilterDrawer, FilterSkeleton, FilterTag
- **Group D (Tasks 55–70) — Toolbar & Pagination:** SortDropdown, ViewToggle, CatalogToolbar, Pagination (with ellipsis), LoadMoreButton, LoadingGridSkeleton, ListView, ActiveFilters
- **Group E (Tasks 71–82) — Category & Collection Pages:** CategoryHero, CategoryDescription, CategoryEmpty, SubcategoryGrid, CategoryCard, CollectionHero, CollectionBanner, CollectionDescription, CollectionEmpty, CollectionCard, FeaturedCollections
- **Group F (Tasks 83–96) — Empty States & Quick View:** EmptyState, NoProductsFound, NoSearchResults, EmptyStateIllustration, ErrorState, SuggestionLinks, QuickViewModal (focus trap + Escape + scroll lock), QuickViewContent (real useProduct data + cart + variants)

**Audit Gaps Found & Fixed (5 fixes):**

**File Counts:** 70 files (6 routes + 2 lib + 62 components including barrel)
**Test Result:** 0 TypeScript errors
**Audit Report:** SP03_STOREFRONT_CATALOG_AUDIT_REPORT.md created with per-task compliance matrix and certification

---

## Workflow Rules

1. Always read each Document-Series document carefully before implementing
2. Create REAL Django code (models, views, serializers, etc.) -- NEVER config functions
3. Keep existing config functions and their tests (they still pass)
4. Use Docker PostgreSQL for ALL testing and development -- NEVER SQLite
5. pytest.ini defaults to `config.settings.test_pg` (Docker PostgreSQL)
6. Run `python /e/My_GitHub_Repos/flow/flow.py` for user review after each task
7. Use subagents for complex implementations to manage context window
8. The `users` app models complement PlatformUser -- they don't replace AUTH_USER_MODEL
9. Existing mixins use `created_on`/`updated_on` (NOT `created_at`/`updated_at`)
10. Celery: CELERY_TASK_ALWAYS_EAGER=True in tests, TenantAwareTask for schema switching
11. django-tenants tests: session-scoped tenant + function-scoped tenant_context fixture pattern
12. SoftDeleteMixin is fields-only (`is_deleted`, `deleted_on`) — no `delete()` override
13. Products Category uses `UUIDMixin + TimestampMixin + MPTTModel` (not BaseModel)
14. Product model extends BaseModel (UUID, timestamps, audit, status, soft-delete)
15. SP08 integration tests: `pytestmark = pytest.mark.django_db` (NO `transaction=True`)
16. IntegrityError tests must wrap failing operation in `transaction.atomic()`
17. Phase-03 Core Backend (SP01-SP12), Phase-04 (SP01-SP10), Phase-05 (SP01-SP05) all COMPLETE
