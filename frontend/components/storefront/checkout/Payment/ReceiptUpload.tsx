'use client';

import { useState, useRef, useCallback } from 'react';
import { Upload, X, FileText, Image as ImageIcon } from 'lucide-react';
import { useStoreCheckoutStore } from '@/stores/store';

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'application/pdf'];

export const ReceiptUpload = () => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const setPaymentDetails = useStoreCheckoutStore((s) => s.setPaymentDetails);

  const handleFile = useCallback(
    (selected: File) => {
      setError(null);

      if (!ACCEPTED_TYPES.includes(selected.type)) {
        setError('Please upload an image or PDF file');
        return;
      }

      if (selected.size > MAX_FILE_SIZE) {
        setError('File size must be less than 5MB');
        return;
      }

      setFile(selected);

      if (selected.type.startsWith('image/')) {
        const url = URL.createObjectURL(selected);
        setPreview(url);
      } else {
        setPreview(null);
      }

      setPaymentDetails({
        methodType: 'bank_transfer',
        bankReceipt: selected.name,
      });
    },
    [setPaymentDetails]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const dropped = e.dataTransfer.files[0];
      if (dropped) handleFile(dropped);
    },
    [handleFile]
  );

  const handleRemove = () => {
    setFile(null);
    if (preview) {
      URL.revokeObjectURL(preview);
      setPreview(null);
    }
    setError(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <div className="space-y-2">
      <p className="text-sm font-medium text-gray-700">Upload Payment Receipt</p>

      {!file ? (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragOver(true);
          }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={`flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-6 cursor-pointer transition-colors ${
            isDragOver
              ? 'border-blue-400 bg-blue-50'
              : 'border-gray-300 bg-gray-50 hover:border-gray-400'
          }`}
        >
          <Upload className="h-8 w-8 text-gray-400" />
          <p className="text-sm text-gray-600">
            <span className="font-medium text-blue-600">Click to upload</span> or drag and drop
          </p>
          <p className="text-xs text-gray-400">Images or PDF, max 5MB</p>
        </div>
      ) : (
        <div className="flex items-center gap-3 rounded-lg border border-gray-200 p-3 bg-white">
          {preview ? (
            <img
              src={preview}
              alt="Receipt preview"
              className="h-16 w-16 rounded object-cover border border-gray-200"
            />
          ) : (
            <div className="flex h-16 w-16 items-center justify-center rounded bg-gray-100">
              {file.type === 'application/pdf' ? (
                <FileText className="h-8 w-8 text-red-500" />
              ) : (
                <ImageIcon className="h-8 w-8 text-gray-400" />
              )}
            </div>
          )}
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">{file.name}</p>
            <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
          </div>
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              handleRemove();
            }}
            className="shrink-0 rounded-full p-1 hover:bg-gray-100 transition-colors"
          >
            <X className="h-4 w-4 text-gray-400" />
          </button>
        </div>
      )}

      <input
        ref={inputRef}
        type="file"
        accept="image/*,application/pdf"
        onChange={(e) => {
          const selected = e.target.files?.[0];
          if (selected) handleFile(selected);
        }}
        className="hidden"
      />

      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
};
