'use client';

import * as React from 'react';
import { Upload, X, ImageIcon } from 'lucide-react';

import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

export interface ImageUploadProps {
  value?: File | string | null;
  onChange?: (file: File | null) => void;
  accept?: string;
  maxSize?: number; // bytes
  aspectRatio?: string; // e.g. '1/1', '16/9'
  disabled?: boolean;
  className?: string;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function ImageUpload({
  value,
  onChange,
  accept = 'image/png,image/jpeg,image/webp',
  maxSize = 5 * 1024 * 1024, // 5MB
  aspectRatio,
  disabled = false,
  className,
}: ImageUploadProps) {
  const inputRef = React.useRef<HTMLInputElement>(null);
  const [preview, setPreview] = React.useState<string | null>(null);
  const [dragActive, setDragActive] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (value instanceof File) {
      const url = URL.createObjectURL(value);
      setPreview(url);
      return () => URL.revokeObjectURL(url);
    }
    if (typeof value === 'string') {
      setPreview(value);
    } else {
      setPreview(null);
    }
    return undefined;
  }, [value]);

  const handleFile = (file: File) => {
    setError(null);
    if (file.size > maxSize) {
      setError(`File exceeds ${formatSize(maxSize)} limit`);
      return;
    }
    if (!file.type.startsWith('image/')) {
      setError('Only image files are allowed');
      return;
    }
    onChange?.(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (!disabled && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange?.(null);
    setPreview(null);
    setError(null);
  };

  return (
    <div className={cn('space-y-2', className)}>
      <div
        onDrop={handleDrop}
        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled) setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') inputRef.current?.click();
        }}
        style={aspectRatio ? { aspectRatio } : undefined}
        className={cn(
          'relative flex cursor-pointer flex-col items-center justify-center overflow-hidden rounded-lg border-2 border-dashed transition-colors',
          !preview && 'p-6',
          dragActive
            ? 'border-primary bg-primary/5'
            : 'border-muted-foreground/25 hover:border-primary/50',
          disabled && 'cursor-not-allowed opacity-50'
        )}
      >
        {preview ? (
          <>
            <img
              src={preview}
              alt="Upload preview"
              className="h-full w-full object-cover"
            />
            <Button
              type="button"
              variant="destructive"
              size="icon"
              className="absolute right-2 top-2 h-7 w-7"
              onClick={handleRemove}
              aria-label="Remove image"
            >
              <X className="h-4 w-4" />
            </Button>
          </>
        ) : (
          <div className="flex flex-col items-center gap-2 text-center">
            <div className="rounded-full bg-muted p-3">
              <ImageIcon className="h-6 w-6 text-muted-foreground" />
            </div>
            <div>
              <p className="text-sm font-medium">Upload image</p>
              <p className="text-xs text-muted-foreground">
                Drop or click · Max {formatSize(maxSize)}
              </p>
            </div>
          </div>
        )}
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          disabled={disabled}
          onChange={(e) => {
            if (e.target.files?.[0]) handleFile(e.target.files[0]);
            e.target.value = '';
          }}
          className="sr-only"
          aria-label="Image upload"
        />
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  );
}

export { ImageUpload };
