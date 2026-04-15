'use client';

import { useRef } from 'react';
import { Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { LogoPreview } from './LogoPreview';

const ACCEPTED_TYPES = ['image/png', 'image/jpeg', 'image/jpg', 'image/svg+xml'];
const MAX_SIZE = 2 * 1024 * 1024; // 2MB

interface LogoUploadProps {
  value?: string;
  onChange: (value: string) => void;
  onRemove?: () => void;
}

export function LogoUpload({ value, onChange, onRemove }: LogoUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File) => {
    if (!ACCEPTED_TYPES.includes(file.type)) return;
    if (file.size > MAX_SIZE) return;
    const reader = new FileReader();
    reader.onloadend = () => {
      if (typeof reader.result === 'string') onChange(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  if (value) {
    return <LogoPreview src={value} onRemove={onRemove ?? (() => onChange(''))} />;
  }

  return (
    <div
      className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-6 transition-colors hover:border-primary/50"
      onDragOver={(e) => e.preventDefault()}
      onDrop={handleDrop}
    >
      <Upload className="mb-2 h-8 w-8 text-muted-foreground" />
      <p className="mb-1 text-sm font-medium">Drop your logo here or click to upload</p>
      <p className="text-xs text-muted-foreground">PNG, JPG, JPEG, or SVG (max 2MB)</p>
      <Button
        type="button"
        variant="outline"
        size="sm"
        className="mt-3"
        onClick={() => inputRef.current?.click()}
      >
        Choose File
      </Button>
      <input
        ref={inputRef}
        type="file"
        accept=".png,.jpg,.jpeg,.svg"
        className="hidden"
        onChange={handleChange}
      />
    </div>
  );
}
