'use client';

import { useState, useRef, useCallback } from 'react';
import { Upload, X, AlertCircle, CheckCircle2 } from 'lucide-react';

const ACCEPTED_MIME = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_SIZE_BYTES = 5 * 1024 * 1024; // 5MB

export interface HeroImageUploadProps {
  currentImage?: string;
  onUploadComplete: (url: string) => void;
  maxSizeMB?: number;
  recommendedWidth?: number;
  recommendedHeight?: number;
}

export function HeroImageUpload({
  currentImage,
  onUploadComplete,
  maxSizeMB = 5,
  recommendedWidth = 1920,
  recommendedHeight = 600,
}: HeroImageUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>(currentImage ?? '');
  const [fileName, setFileName] = useState<string | null>(null);
  const [fileSize, setFileSize] = useState<string | null>(null);

  const maxBytes = maxSizeMB * 1024 * 1024;

  const processFile = useCallback(
    (file: File) => {
      setError(null);
      setWarning(null);

      if (!ACCEPTED_MIME.includes(file.type)) {
        setError('Please upload a JPG, PNG, or WebP image');
        return;
      }

      if (file.size > maxBytes) {
        setError(`File must be smaller than ${maxSizeMB}MB`);
        return;
      }

      // Check dimensions
      const img = new Image();
      const objectUrl = URL.createObjectURL(file);
      img.onload = () => {
        if (img.naturalWidth < 1200 || img.naturalHeight < 400) {
          setWarning(
            `Image is ${img.naturalWidth}×${img.naturalHeight}px. Recommended minimum: 1200×400px`
          );
        }
        setPreviewUrl(objectUrl);
        setFileName(file.name);
        setFileSize(formatBytes(file.size));
        onUploadComplete(objectUrl);
      };
      img.onerror = () => {
        URL.revokeObjectURL(objectUrl);
        setError('Unable to read image');
      };
      img.src = objectUrl;
    },
    [maxBytes, maxSizeMB, onUploadComplete]
  );

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) processFile(file);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file) processFile(file);
  };

  const handleRemove = () => {
    setPreviewUrl('');
    setFileName(null);
    setFileSize(null);
    setError(null);
    setWarning(null);
    onUploadComplete('');
  };

  return (
    <div className="space-y-3">
      <p className="text-xs text-gray-500">
        Recommended: {recommendedWidth}×{recommendedHeight}px &bull; JPG, PNG, or WebP &bull; Max{' '}
        {maxSizeMB}MB
      </p>

      {/* Drop zone */}
      <div
        role="button"
        tabIndex={0}
        className={`flex cursor-pointer flex-col items-center gap-2 rounded-lg border-2 border-dashed p-6 text-center transition-colors ${
          dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
        }`}
        onClick={() => fileInputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') fileInputRef.current?.click();
        }}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <Upload className="h-8 w-8 text-gray-400" />
        <div>
          <span className="font-medium text-blue-600">Click to upload</span>{' '}
          <span className="text-gray-500">or drag and drop</span>
        </div>
        <p className="text-xs text-gray-400">JPG, PNG, WebP &bull; Max {maxSizeMB}MB</p>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        accept={ACCEPTED_MIME.join(',')}
        onChange={handleFileChange}
      />

      {/* Preview */}
      {previewUrl && (
        <div className="space-y-2">
          <div className="relative overflow-hidden rounded-lg border border-gray-200">
            <img
              src={previewUrl}
              alt="Hero preview"
              className="w-full object-cover"
              style={{ maxHeight: 240 }}
            />
            <button
              type="button"
              onClick={handleRemove}
              className="absolute right-2 top-2 rounded-full bg-black/50 p-1 text-white hover:bg-black/70"
              aria-label="Remove image"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          {fileName && (
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <span className="truncate">{fileName}</span>
              {fileSize && <span className="text-gray-400">{fileSize}</span>}
            </div>
          )}
        </div>
      )}

      {/* Warning */}
      {warning && (
        <div className="flex items-center gap-2 rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-700">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {warning}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}
    </div>
  );
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}
