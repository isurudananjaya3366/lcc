'use client';

import { useState, useRef, useCallback, type DragEvent } from 'react';
import { Upload, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_SIZE = 5 * 1024 * 1024; // 5MB

interface ImageUploadZoneProps {
  onUpload: (files: File[]) => void;
  maxFiles?: number;
  disabled?: boolean;
  currentCount?: number;
}

export function ImageUploadZone({
  onUpload,
  maxFiles = 10,
  disabled = false,
  currentCount = 0,
}: ImageUploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const validateAndUpload = useCallback(
    (fileList: FileList | File[]) => {
      setError('');
      const files = Array.from(fileList);
      const errors: string[] = [];
      const valid: File[] = [];

      const remaining = maxFiles - currentCount;
      if (remaining <= 0) {
        setError(`Maximum ${maxFiles} images allowed`);
        return;
      }

      for (const file of files) {
        if (!ACCEPTED_TYPES.includes(file.type)) {
          errors.push(`${file.name}: Invalid file type`);
          continue;
        }
        if (file.size > MAX_SIZE) {
          errors.push(`${file.name}: File exceeds 5MB limit`);
          continue;
        }
        if (valid.length >= remaining) {
          errors.push(`${file.name}: Maximum image limit reached`);
          continue;
        }
        valid.push(file);
      }

      if (errors.length > 0) {
        setError(errors[0]);
      }

      if (valid.length > 0) {
        onUpload(valid);
      }
    },
    [onUpload, maxFiles, currentCount]
  );

  const handleDragEnter = (e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (!disabled && e.dataTransfer.files.length > 0) {
      validateAndUpload(e.dataTransfer.files);
    }
  };

  const handleClick = () => {
    if (!disabled) inputRef.current?.click();
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndUpload(e.target.files);
      e.target.value = '';
    }
  };

  return (
    <div className="space-y-2">
      <div
        role="button"
        tabIndex={disabled ? -1 : 0}
        aria-label="Upload images by dropping files here or clicking to browse"
        className={cn(
          'flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 text-center transition-colors',
          isDragging
            ? 'border-blue-600 bg-blue-50 dark:bg-blue-950/30'
            : 'border-gray-300 bg-gray-50 hover:border-gray-400 dark:border-gray-600 dark:bg-gray-800/50 dark:hover:border-gray-500',
          disabled && 'cursor-not-allowed opacity-50'
        )}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={handleClick}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleClick();
          }
        }}
      >
        <Upload className="mb-2 h-8 w-8 text-gray-400" />
        <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {isDragging ? 'Drop images to upload' : 'Drag and drop images here'}
        </p>
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">or click to browse</p>
        <p className="mt-2 text-xs text-gray-400 dark:text-gray-500">
          JPEG, PNG, WebP &middot; Max 5MB each &middot; {currentCount}/{maxFiles} images
        </p>
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        multiple
        onChange={handleInputChange}
        className="hidden"
        aria-hidden="true"
      />

      {error && (
        <div
          className="flex items-center gap-1.5 text-xs text-red-600 dark:text-red-400"
          role="alert"
        >
          <AlertCircle className="h-3.5 w-3.5 shrink-0" />
          {error}
        </div>
      )}
    </div>
  );
}
