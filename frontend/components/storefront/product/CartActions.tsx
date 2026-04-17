'use client';

import { useState, useCallback } from 'react';
import type { Product, ProductVariant } from '@/lib/api/store/modules/products';
import { useStoreCartStore } from '@/stores/store/cart';
import { VariantSelector } from './VariantSelector';
import { QuantitySelector } from './QuantitySelector';
import { AddToCartButton } from './AddToCartButton';
import { BuyNowButton } from './BuyNowButton';
import { WishlistButton } from './WishlistButton';
import { PriceDisplay } from './PriceDisplay';

interface CartActionsProps {
  product: Product;
}

export function CartActions({ product }: CartActionsProps) {
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(null);
  const [quantity, setQuantity] = useState(1);
  const addToCart = useStoreCartStore((s) => s.addToCart);

  const hasVariants = product.variants && product.variants.length > 0;
  const needsVariantSelection = hasVariants && !selectedVariant;

  const currentPrice = selectedVariant?.price ?? product.sale_price ?? product.price;
  const currentInStock = selectedVariant ? selectedVariant.in_stock : product.in_stock;
  const currentStockQty = selectedVariant
    ? (selectedVariant.in_stock ? 99 : 0)
    : product.stock_quantity;

  const maxQuantity = Math.max(1, currentStockQty);

  const primaryImage = product.images?.find((img) => img.is_primary) ?? product.images?.[0];

  const handleAddToCart = useCallback(() => {
    return addToCart(
      {
        productId: String(product.id),
        name: selectedVariant ? `${product.name} - ${selectedVariant.name}` : product.name,
        sku: selectedVariant?.sku ?? product.sku,
        price: currentPrice,
        image: primaryImage?.url ?? '',
        variant: selectedVariant?.attributes,
      },
      quantity
    );
  }, [addToCart, product, selectedVariant, currentPrice, primaryImage, quantity]);

  const handleBuyNow = useCallback(() => {
    const success = handleAddToCart();
    if (success) {
      window.location.href = '/checkout';
    }
  }, [handleAddToCart]);

  return (
    <div className="space-y-5">
      {/* Variant Selection */}
      {hasVariants && (
        <VariantSelector
          variants={product.variants}
          onVariantChange={setSelectedVariant}
        />
      )}

      {/* Price update on variant change */}
      {selectedVariant && (
        <PriceDisplay
          price={currentPrice}
          salePrice={null}
          currency={product.currency}
        />
      )}

      {/* Quantity */}
      <QuantitySelector
        value={quantity}
        max={maxQuantity}
        onChange={setQuantity}
      />

      {/* Action Buttons */}
      <div className="space-y-3">
        <AddToCartButton
          onAdd={handleAddToCart}
          disabled={!currentInStock || needsVariantSelection}
        />
        <BuyNowButton
          onBuyNow={handleBuyNow}
          disabled={!currentInStock || needsVariantSelection}
        />
      </div>

      {/* Wishlist */}
      <WishlistButton
        productId={String(product.id)}
        productName={product.name}
        productSlug={product.slug}
        price={product.price}
        salePrice={product.sale_price}
        image={primaryImage?.url ?? ''}
        inStock={product.in_stock}
      />

      {needsVariantSelection && (
        <p className="text-sm text-amber-600">Please select all options before adding to cart.</p>
      )}
    </div>
  );
}
