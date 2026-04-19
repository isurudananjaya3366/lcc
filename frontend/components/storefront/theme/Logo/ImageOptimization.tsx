'use client';

import { useState, useEffect } from 'react';
import { FileImage, AlertTriangle, CheckCircle2 } from 'lucide-react';

export interface ImageOptimizationProps {
  imageUrl: string;
  fileName?: string;
  onOptimize?: (optimizedUrl: string) => void;
}

interface ImageInfo {
  width: number;
  height: number;
  estimatedSizeKB: number;
}

export function ImageOptimization({ imageUrl, fileName, onOptimize }: ImageOptimizationProps) {
  const [info, setInfo] = useState<ImageInfo | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!imageUrl) {
      setInfo(null);
      return;
    }

    setLoading(true);
    const img = new Image();
    img.onload = () => {
      // Estimate size from dimensions (rough heuristic)
      const estimatedSizeKB = Math.round((img.naturalWidth * img.naturalHeight * 3) / 1024 / 4);
      setInfo({
        width: img.naturalWidth,
        height: img.naturalHeight,
        estimatedSizeKB,
      });
      setLoading(false);
    };
    img.onerror = () => setLoading(false);
    img.src = imageUrl;
  }, [imageUrl]);

  if (!imageUrl) return null;

  const isLargeImage = info && info.estimatedSizeKB > 500;
  const isOversized = info && (info.width > 3000 || info.height > 3000);

  const handleCompress = () => {
    if (!imageUrl || !info) return;

    // Client-side compression using canvas
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      const maxW = Math.min(img.naturalWidth, 1920);
      const scale = maxW / img.naturalWidth;
      canvas.width = maxW;
      canvas.height = img.naturalHeight * scale;

      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      const compressed = canvas.toDataURL('image/jpeg', 0.8);
      onOptimize?.(compressed);
    };
    img.src = imageUrl;
  };

  return (
    <div className="space-y-3 rounded-lg border border-gray-200 p-4">
      <div className="flex items-center gap-2">
        <FileImage className="h-5 w-5 text-blue-600" />
        <h4 className="text-sm font-semibold text-gray-800">Image Optimization</h4>
      </div>

      {loading && <div className="h-4 w-40 animate-pulse rounded bg-gray-200" />}

      {info && (
        <div className="space-y-2">
          {/* Stats */}
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="text-gray-500">Dimensions</div>
            <div className="text-gray-800">
              {info.width} × {info.height} px
            </div>
            {fileName && (
              <>
                <div className="text-gray-500">File</div>
                <div className="truncate text-gray-800">{fileName}</div>
              </>
            )}
          </div>

          {/* Tips */}
          <div className="space-y-1.5">
            {isOversized && (
              <div className="flex items-start gap-2 rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-700">
                <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                Image dimensions are very large. Consider resizing to 1920px wide for faster
                loading.
              </div>
            )}
            {isLargeImage && (
              <div className="flex items-start gap-2 rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-700">
                <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                Image file may be large. Use WebP format and 80% quality for best results.
              </div>
            )}
            {!isLargeImage && !isOversized && (
              <div className="flex items-center gap-2 rounded-md bg-green-50 px-3 py-2 text-xs text-green-700">
                <CheckCircle2 className="h-3.5 w-3.5 shrink-0" />
                Image size looks good.
              </div>
            )}
          </div>

          {/* Compress button */}
          {(isLargeImage || isOversized) && onOptimize && (
            <button
              type="button"
              onClick={handleCompress}
              className="rounded-md border border-blue-300 bg-blue-50 px-3 py-1.5 text-xs font-medium text-blue-700 hover:bg-blue-100"
            >
              Compress &amp; Resize (80% quality, max 1920px wide)
            </button>
          )}

          {/* General tips */}
          <details className="group">
            <summary className="cursor-pointer text-xs text-gray-500 hover:text-gray-700">
              Optimization tips
            </summary>
            <ul className="mt-1 space-y-0.5 pl-4 text-xs text-gray-500">
              <li>&bull; Use WebP for 25-35% smaller files vs. JPEG</li>
              <li>&bull; Logos: PNG or SVG for transparency</li>
              <li>&bull; Hero images: max 1920px wide, 80% quality</li>
              <li>&bull; Enable lazy loading for below-the-fold images</li>
              <li>&bull; Use progressive JPEG for perceived faster loading</li>
            </ul>
          </details>
        </div>
      )}
    </div>
  );
}
