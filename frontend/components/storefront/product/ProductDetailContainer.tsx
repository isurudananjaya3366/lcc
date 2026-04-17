import type { Product } from '@/lib/api/store/modules/products';
import type { BreadcrumbItem } from '@/components/storefront/catalog/Breadcrumb';
import { ProductBreadcrumb } from './ProductBreadcrumb';
import { ProductLayout } from './ProductLayout';
import { Gallery } from './Gallery';
import { ProductInfo } from './ProductInfo';
import { CartActions } from './CartActions';
import { ProductTabs } from './ProductTabs';
import { RelatedProducts } from './RelatedProducts';
import { CrossSellSection } from './CrossSellSection';
import { RecentlyViewedTracker } from './RecentlyViewedTracker';
import { RecentlyViewed } from './RecentlyViewed';

interface ProductDetailContainerProps {
  product: Product;
  breadcrumbs: BreadcrumbItem[];
  relatedProducts?: Product[];
}

export function ProductDetailContainer({
  product,
  breadcrumbs,
  relatedProducts,
}: ProductDetailContainerProps) {
  const primaryImage = product.images?.find((img) => img.is_primary) ?? product.images?.[0];

  return (
    <div className="py-6">
      {/* Track recently viewed */}
      <RecentlyViewedTracker
        product={{
          slug: product.slug,
          name: product.name,
          price: product.sale_price ?? product.price,
          currency: product.currency,
          image: primaryImage?.url ?? '',
        }}
      />

      {/* Breadcrumb */}
      <ProductBreadcrumb items={breadcrumbs} className="mb-6" />

      {/* Main product layout: Gallery + Info + Cart Actions */}
      <ProductLayout
        gallery={
          <Gallery
            images={product.images ?? []}
            productName={product.name}
          />
        }
        info={
          <div className="space-y-6">
            <ProductInfo product={product} />
            <CartActions product={product} />
          </div>
        }
      />

      {/* Product tabs (description, specs, reviews) */}
      <section className="mt-12 border-t pt-8">
        <ProductTabs
          description={product.description}
          productId={product.id}
          reviewCount={product.review_count}
        />
      </section>

      {/* Related products */}
      {relatedProducts && relatedProducts.length > 0 && (
        <section className="mt-12 border-t pt-8">
          <RelatedProducts products={relatedProducts} />
        </section>
      )}

      {/* Cross-sell (Frequently Bought Together) */}
      {relatedProducts && relatedProducts.length > 0 && (
        <section className="mt-12 border-t pt-8">
          <CrossSellSection products={relatedProducts.slice(0, 3)} />
        </section>
      )}

      {/* Recently viewed */}
      <section className="mt-12 border-t pt-8">
        <RecentlyViewed currentSlug={product.slug} />
      </section>
    </div>
  );
}
