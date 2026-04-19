'use client';

import { useState, useRef, useCallback } from 'react';
import { Upload, X, AlertCircle, CheckCircle2 } from 'lucide-react';

const ACCEPTED_FORMATS: Record<string, string[]> = {
  main: ['image/png', 'image/jpeg', 'image/svg+xml', 'image/webp'],
  favicon: ['image/png', 'image/x-icon', 'image/vnd.microsoft.icon'],
  mobile: ['image/png', 'image/jpeg', 'image/svg+xml', 'image/webp'],
};

const FORMAT_LABELS: Record<string, string> = {
  main: 'PNG, JPG, SVG, WebP',
  favicon: 'PNG, ICO',
  mobile: 'PNG, JPG, SVG, WebP',
};

export interface LogoUploadProps {
  logoType: 'main' | 'favicon' | 'mobile';
  currentUrl?: string;
  onUploadComplete: (url: string) => void;
  maxSizeMB?: number;
  acceptedFormats?: string[];
}

export function LogoUpload({
  logoType,
  currentUrl,
  onUploadComplete,
  maxSizeMB = 2,
  acceptedFormats,
}: LogoUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [fileSize, setFileSize] = useState<string | null>(null);

  const allowedMimes = acceptedFormats ?? ACCEPTED_FORMATS[logoType] ?? [];
  const formatLabel = FORMAT_LABELS[logoType];
  const maxBytes = maxSizeMB * 1024 * 1024;

  const validateAndProcess = useCallback(
    (file: File) => {
      setError(null);

      if (!allowedMimes.includes(file.type)) {
        setError(`Please upload a ${formatLabel} file`);
        return;
      }

      if (file.size > maxBytes) {
        setError(`File must be smaller than ${maxSizeMB}MB`);
        return;
      }

      // Generate client-side preview URL
      const objectUrl = URL.createObjectURL(file);
      setFileName(file.name);
      setFileSize(formatFileSize(file.size));
      onUploadComplete(objectUrl);
    },
    [allowedMimes, formatLabel, maxBytes, maxSizeMB, onUploadComplete]
  );

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) validateAndProcess(file);
    // Reset input so the same file can be re-selected
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file) validateAndProcess(file);
  };

  const handleRemove = () => {
    setFileName(null);
    setFileSize(null);
    setError(null);
    onUploadComplete('');
  };

  return (
    <div className="space-y-3">
      {/* Drop Zone */}
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
        <p className="text-xs text-gray-400">
          {formatLabel} &bull; Max {maxSizeMB}MB
        </p>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        accept={allowedMimes.join(',')}
        onChange={handleFileChange}
      />

      {/* File Info */}
      {currentUrl && fileName && (
        <div className="flex items-center gap-2 rounded-md bg-green-50 px-3 py-2 text-sm">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          <span className="flex-1 truncate text-green-800">{fileName}</span>
          {fileSize && <span className="text-green-600">{fileSize}</span>}
          <button
            type="button"
            onClick={handleRemove}
            className="rounded p-1 hover:bg-green-100"
            aria-label="Remove file"
          >
            <X className="h-4 w-4 text-green-700" />
          </button>
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

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}
