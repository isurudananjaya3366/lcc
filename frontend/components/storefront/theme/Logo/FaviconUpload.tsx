'use client';

import { useState, useRef, useCallback } from 'react';
import { Upload, X, AlertCircle, CheckCircle2, Globe } from 'lucide-react';

const ACCEPTED_MIME = ['image/png', 'image/x-icon', 'image/vnd.microsoft.icon'];
const MAX_SIZE_BYTES = 500 * 1024; // 500KB

export interface FaviconUploadProps {
  currentFavicon?: string;
  onUploadComplete: (url: string) => void;
}

export function FaviconUpload({ currentFavicon, onUploadComplete }: FaviconUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>(currentFavicon ?? '');
  const [fileName, setFileName] = useState<string | null>(null);

  const processFile = useCallback(
    (file: File) => {
      setError(null);

      if (!ACCEPTED_MIME.includes(file.type)) {
        setError('Favicon must be PNG or ICO format');
        return;
      }

      if (file.size > MAX_SIZE_BYTES) {
        setError('Favicon must be smaller than 500KB');
        return;
      }

      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      setFileName(file.name);
      onUploadComplete(url);
    },
    [onUploadComplete]
  );

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) processFile(file);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleRemove = () => {
    setPreviewUrl('');
    setFileName(null);
    setError(null);
    onUploadComplete('');
  };

  return (
    <div className="space-y-3">
      <p className="text-xs text-gray-500">
        Small icon shown in browser tabs. Recommended 32×32px, PNG or ICO.
      </p>

      {/* Upload button */}
      <button
        type="button"
        onClick={() => fileInputRef.current?.click()}
        className="inline-flex items-center gap-2 rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
      >
        <Upload className="h-4 w-4" />
        {previewUrl ? 'Replace Favicon' : 'Upload Favicon'}
      </button>

      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        accept={ACCEPTED_MIME.join(',')}
        onChange={handleFileChange}
      />

      {/* Preview — browser tab mock */}
      {previewUrl && (
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 rounded-t-lg border border-b-0 border-gray-300 bg-gray-100 px-3 py-1.5">
            <img src={previewUrl} alt="Favicon preview" className="h-4 w-4 object-contain" />
            <span className="text-xs text-gray-600">My Store</span>
            <X className="h-3 w-3 text-gray-400" />
          </div>

          <div className="flex items-center gap-2 text-sm">
            <CheckCircle2 className="h-4 w-4 text-green-600" />
            <span className="truncate text-gray-700">{fileName}</span>
            <button
              type="button"
              onClick={handleRemove}
              className="text-xs text-red-600 hover:underline"
            >
              Remove
            </button>
          </div>

          {/* Size previews */}
          <div className="flex items-end gap-4">
            <div className="text-center">
              <div className="mb-1 flex h-8 w-8 items-center justify-center rounded border border-gray-200 bg-white">
                <img src={previewUrl} alt="" className="h-4 w-4 object-contain" />
              </div>
              <span className="text-[10px] text-gray-400">16px</span>
            </div>
            <div className="text-center">
              <div className="mb-1 flex h-10 w-10 items-center justify-center rounded border border-gray-200 bg-white">
                <img src={previewUrl} alt="" className="h-8 w-8 object-contain" />
              </div>
              <span className="text-[10px] text-gray-400">32px</span>
            </div>
            <div className="text-center">
              <div className="mb-1 flex h-12 w-12 items-center justify-center rounded border border-gray-200 bg-gray-900">
                <img src={previewUrl} alt="" className="h-8 w-8 object-contain" />
              </div>
              <span className="text-[10px] text-gray-400">Dark bg</span>
            </div>
          </div>
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
