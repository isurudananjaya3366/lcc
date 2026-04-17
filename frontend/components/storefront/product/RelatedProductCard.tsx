import Link from 'next/link';
import Image from 'next/image';
import type { Product } from '@/lib/api/store/modules/products';

interface RelatedProductCardProps {
  product: Product;
}

export function RelatedProductCard({ product }: RelatedProductCardProps) {
  const primaryImage = product.images?.find((img) => img.is_primary) ?? product.images?.[0];
  const hasDiscount = product.sale_price !== null && product.sale_price < product.price;

  return (
    <Link
      href={`/products/${product.slug}`}
      className="group block rounded-lg border border-gray-200 bg-white p-3 transition-shadow hover:shadow-md"
    >
      <div className="relative aspect-square overflow-hidden rounded-md bg-gray-100">
        {primaryImage ? (
          <Image
            src={primaryImage.url}
            alt={primaryImage.alt_text || product.name}
            fill
            sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
            className="object-cover transition-transform duration-300 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-gray-400">
            <svg className="h-10 w-10" fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0 0 22.5 18.75V5.25A2.25 2.25 0 0 0 20.25 3H3.75A2.25 2.25 0 0 0 1.5 5.25v13.5A2.25 2.25 0 0 0 3.75 21Z" />
            </svg>
          </div>
        )}
      </div>

      <div className="mt-2 space-y-1">
        <h3 className="text-sm font-medium text-gray-900 line-clamp-2 group-hover:text-blue-600">
          {product.name}
        </h3>
        <div className="flex items-baseline gap-2">
          <span className={`text-sm font-semibold ${hasDiscount ? 'text-red-600' : 'text-gray-900'}`}>
            {product.currency} {(hasDiscount ? product.sale_price! : product.price).toLocaleString('en-LK', { minimumFractionDigits: 2 })}
          </span>
          {hasDiscount && (
            <span className="text-xs text-gray-500 line-through">
              {product.currency} {product.price.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}
