'use client';

import { useCallback, useRef, useState } from 'react';
import { Upload, X, Image as ImageIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/svg+xml'];
const MAX_SIZE = 2 * 1024 * 1024; // 2MB

interface CategoryImageUploadProps {
  imageUrl: string | null;
  onImageChange: (file: File | null) => void;
  error?: string;
  disabled?: boolean;
}

export function CategoryImageUpload({
  imageUrl,
  onImageChange,
  error,
  disabled,
}: CategoryImageUploadProps) {
  const [preview, setPreview] = useState<string | null>(imageUrl);
  const [dragOver, setDragOver] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateAndSetFile = useCallback(
    (file: File) => {
      setValidationError(null);

      if (!ACCEPTED_TYPES.includes(file.type)) {
        setValidationError('Only JPG, PNG, WebP, and SVG files are allowed');
        return;
      }

      if (file.size > MAX_SIZE) {
        setValidationError('File size must be under 2MB');
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
      onImageChange(file);
    },
    [onImageChange]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      if (disabled) return;

      const file = e.dataTransfer.files[0];
      if (file) validateAndSetFile(file);
    },
    [disabled, validateAndSetFile]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) validateAndSetFile(file);
      if (inputRef.current) inputRef.current.value = '';
    },
    [validateAndSetFile]
  );

  const handleRemove = useCallback(() => {
    setPreview(null);
    setValidationError(null);
    onImageChange(null);
  }, [onImageChange]);

  const displayError = validationError || error;

  return (
    <div className="space-y-2">
      <Label>Category Image</Label>

      {preview ? (
        <div className="relative w-32 h-32 rounded-lg border border-border overflow-hidden group">
          <img src={preview} alt="Category" className="w-full h-full object-cover" />
          <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={() => inputRef.current?.click()}
              disabled={disabled}
            >
              Replace
            </Button>
            <Button
              type="button"
              variant="destructive"
              size="icon"
              className="h-8 w-8"
              onClick={handleRemove}
              disabled={disabled}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      ) : (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            if (!disabled) setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => !disabled && inputRef.current?.click()}
          className={`
            w-32 h-32 rounded-lg border-2 border-dashed cursor-pointer
            flex flex-col items-center justify-center gap-2 transition-colors
            ${dragOver ? 'border-primary bg-primary/5' : 'border-muted-foreground/25 hover:border-primary/50'}
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          {dragOver ? (
            <Upload className="h-6 w-6 text-primary" />
          ) : (
            <ImageIcon className="h-6 w-6 text-muted-foreground" />
          )}
          <span className="text-xs text-muted-foreground text-center px-2">
            {dragOver ? 'Drop image' : 'Upload image'}
          </span>
        </div>
      )}

      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_TYPES.join(',')}
        onChange={handleFileInput}
        className="hidden"
      />

      {displayError && <p className="text-xs text-red-500">{displayError}</p>}

      <p className="text-xs text-muted-foreground">JPG, PNG, WebP, or SVG. Max 2MB.</p>
    </div>
  );
}
