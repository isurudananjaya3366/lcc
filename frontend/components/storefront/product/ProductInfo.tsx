'use client';

import type { Product } from '@/lib/api/store/modules/products';
import { ProductTitle } from './ProductTitle';
import { ProductSKU } from './ProductSKU';
import { RatingSummary } from './RatingSummary';
import { PriceDisplay } from './PriceDisplay';
import { ShortDescription } from './ShortDescription';
import { StockStatus } from './StockStatus';
import { DeliveryEstimate } from './DeliveryEstimate';
import { ShareButtons } from './ShareButtons';

interface ProductInfoProps {
  product: Product;
}

export function ProductInfo({ product }: ProductInfoProps) {
  return (
    <div className="space-y-5">
      <ProductTitle name={product.name} />
      <ProductSKU sku={product.sku} />

      <RatingSummary
        rating={product.rating}
        reviewCount={product.review_count}
        productId={product.id}
      />

      <PriceDisplay
        price={product.price}
        salePrice={product.sale_price}
        currency={product.currency}
      />

      {product.description && (
        <ShortDescription description={product.description} />
      )}

      <StockStatus inStock={product.in_stock} stockQuantity={product.stock_quantity} />

      <DeliveryEstimate price={product.price} />

      <ShareButtons productName={product.name} productSlug={product.slug} />
    </div>
  );
}
