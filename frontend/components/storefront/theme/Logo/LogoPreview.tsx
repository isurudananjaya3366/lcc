'use client';

import { useState } from 'react';
import { ImageOff } from 'lucide-react';

export interface LogoPreviewProps {
  imageUrl: string;
  logoHeight?: number;
  alt?: string;
  showDimensions?: boolean;
  containerHeight?: number;
}

export function LogoPreview({
  imageUrl,
  logoHeight = 60,
  alt = 'Logo preview',
  showDimensions = false,
  containerHeight = 160,
}: LogoPreviewProps) {
  const [loaded, setLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [naturalSize, setNaturalSize] = useState<{
    width: number;
    height: number;
  } | null>(null);

  const handleLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget;
    setNaturalSize({ width: img.naturalWidth, height: img.naturalHeight });
    setLoaded(true);
    setHasError(false);
  };

  const handleError = () => {
    setHasError(true);
    setLoaded(false);
  };

  if (!imageUrl) {
    return (
      <div
        className="flex items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50 text-sm text-gray-400"
        style={{ minHeight: containerHeight }}
      >
        No logo uploaded
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <p className="text-sm font-medium text-gray-700">Preview</p>

      {/* Preview Container */}
      <div
        className="relative flex items-center justify-center overflow-hidden rounded-lg border border-gray-200"
        style={{
          minHeight: containerHeight,
          backgroundImage:
            'linear-gradient(45deg, #f0f0f0 25%, transparent 25%), ' +
            'linear-gradient(-45deg, #f0f0f0 25%, transparent 25%), ' +
            'linear-gradient(45deg, transparent 75%, #f0f0f0 75%), ' +
            'linear-gradient(-45deg, transparent 75%, #f0f0f0 75%)',
          backgroundSize: '16px 16px',
          backgroundPosition: '0 0, 0 8px, 8px -8px, -8px 0px',
        }}
      >
        {/* Loading skeleton */}
        {!loaded && !hasError && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="h-10 w-32 animate-pulse rounded bg-gray-200" />
          </div>
        )}

        {/* Error state */}
        {hasError && (
          <div className="flex flex-col items-center gap-2 text-gray-400">
            <ImageOff className="h-8 w-8" />
            <span className="text-sm">Failed to load image</span>
          </div>
        )}

        {/* Image */}
        {!hasError && (
          <img
            src={imageUrl}
            alt={alt}
            style={{ height: logoHeight, objectFit: 'contain' }}
            className={`transition-opacity ${loaded ? 'opacity-100' : 'opacity-0'}`}
            onLoad={handleLoad}
            onError={handleError}
          />
        )}
      </div>

      {/* Dimensions info */}
      {showDimensions && loaded && naturalSize && (
        <div className="flex gap-4 text-xs text-gray-500">
          <span>
            Original: {naturalSize.width} × {naturalSize.height} px
          </span>
          <span>Display height: {logoHeight}px</span>
        </div>
      )}
    </div>
  );
}
