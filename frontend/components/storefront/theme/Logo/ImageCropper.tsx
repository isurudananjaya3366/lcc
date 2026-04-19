'use client';

import { useState } from 'react';
import { Crop } from 'lucide-react';

export interface ImageCropperProps {
  imageUrl: string;
  onCrop: (croppedUrl: string) => void;
}

const ASPECT_RATIOS = [
  { label: 'Free', value: null },
  { label: '1:1', value: 1 },
  { label: '16:9', value: 16 / 9 },
  { label: '3:1', value: 3 },
  { label: '4:3', value: 4 / 3 },
  { label: '2:1', value: 2 },
] as const;

export function ImageCropper({ imageUrl, onCrop }: ImageCropperProps) {
  const [selectedRatio, setSelectedRatio] = useState<number | null>(null);
  const [applied, setApplied] = useState(false);

  const handleApply = () => {
    if (!imageUrl) return;

    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      let cropW = img.naturalWidth;
      let cropH = img.naturalHeight;
      let offsetX = 0;
      let offsetY = 0;

      if (selectedRatio) {
        const currentRatio = img.naturalWidth / img.naturalHeight;
        if (currentRatio > selectedRatio) {
          // Image is wider, crop width
          cropW = Math.round(img.naturalHeight * selectedRatio);
          offsetX = Math.round((img.naturalWidth - cropW) / 2);
        } else {
          // Image is taller, crop height
          cropH = Math.round(img.naturalWidth / selectedRatio);
          offsetY = Math.round((img.naturalHeight - cropH) / 2);
        }
      }

      canvas.width = cropW;
      canvas.height = cropH;
      ctx.drawImage(img, offsetX, offsetY, cropW, cropH, 0, 0, cropW, cropH);

      const croppedUrl = canvas.toDataURL('image/png');
      onCrop(croppedUrl);
      setApplied(true);
    };
    img.src = imageUrl;
  };

  if (!imageUrl) return null;

  return (
    <div className="space-y-3 rounded-lg border border-gray-200 p-4">
      <div className="flex items-center gap-2">
        <Crop className="h-5 w-5 text-blue-600" />
        <h4 className="text-sm font-semibold text-gray-800">Crop Image</h4>
      </div>

      {/* Aspect ratio selector */}
      <div className="space-y-1">
        <p className="text-xs text-gray-500">Select aspect ratio</p>
        <div className="flex flex-wrap gap-2">
          {ASPECT_RATIOS.map((ar) => (
            <button
              key={ar.label}
              type="button"
              onClick={() => {
                setSelectedRatio(ar.value);
                setApplied(false);
              }}
              className={`rounded-md border px-3 py-1 text-sm transition-colors ${
                selectedRatio === ar.value
                  ? 'border-blue-600 bg-blue-50 text-blue-700'
                  : 'border-gray-300 text-gray-600 hover:bg-gray-50'
              }`}
            >
              {ar.label}
            </button>
          ))}
        </div>
      </div>

      {/* Preview with aspect ratio overlay */}
      <div className="relative overflow-hidden rounded-md border border-gray-200 bg-gray-50">
        <img src={imageUrl} alt="Crop preview" className="mx-auto max-h-48 object-contain" />
        {selectedRatio && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div
              className="border-2 border-dashed border-blue-500 bg-blue-500/10"
              style={{
                aspectRatio: selectedRatio,
                maxWidth: '80%',
                maxHeight: '80%',
                width: selectedRatio >= 1 ? '80%' : 'auto',
                height: selectedRatio < 1 ? '80%' : 'auto',
              }}
            />
          </div>
        )}
      </div>

      {/* Apply */}
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={handleApply}
          disabled={selectedRatio === null && !applied}
          className="rounded-md bg-blue-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {applied ? 'Re-crop' : 'Apply Crop'}
        </button>
        {applied && <span className="text-xs text-green-600">Crop applied</span>}
      </div>
    </div>
  );
}
