'use client';

import { useState, useEffect, useRef, KeyboardEvent } from 'react';
import type { ProductVariant } from '@/types/product';
import { Input } from '@/components/ui/input';
import { Loader2, Check } from 'lucide-react';

interface VariantInlineEditorProps {
  variant: ProductVariant;
  field: 'sku' | 'price' | 'stockQuantity';
  onSave: (id: string, updates: Partial<ProductVariant>) => Promise<void>;
  onCancel?: () => void;
}

export function VariantInlineEditor({
  variant,
  field,
  onSave,
  onCancel,
}: VariantInlineEditorProps) {
  const [value, setValue] = useState(String(variant[field]));
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
    inputRef.current?.select();
  }, []);

  const validate = (val: string): string | null => {
    if (field === 'sku') {
      if (!val.trim()) return 'SKU is required';
    }
    if (field === 'price') {
      const num = parseFloat(val);
      if (isNaN(num) || num <= 0) return 'Price must be greater than 0';
    }
    if (field === 'stockQuantity') {
      const num = parseInt(val);
      if (isNaN(num) || num < 0) return 'Stock cannot be negative';
    }
    return null;
  };

  const handleSave = async () => {
    const err = validate(value);
    if (err) {
      setError(err);
      return;
    }

    setSaving(true);
    setError('');
    try {
      const updates: Partial<ProductVariant> = {};
      if (field === 'sku') updates.sku = value.trim();
      if (field === 'price') updates.price = parseFloat(value);
      if (field === 'stockQuantity') updates.stockQuantity = parseInt(value);

      await onSave(variant.id, updates);
      setSaved(true);
      setTimeout(() => setSaved(false), 1500);
    } catch {
      setError('Failed to save');
      setValue(String(variant[field]));
    } finally {
      setSaving(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSave();
    } else if (e.key === 'Escape') {
      setValue(String(variant[field]));
      onCancel?.();
    }
  };

  const inputType = field === 'sku' ? 'text' : 'number';

  return (
    <div className="relative">
      <div className="flex items-center gap-1">
        <Input
          ref={inputRef}
          type={inputType}
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
            setError('');
          }}
          onKeyDown={handleKeyDown}
          onBlur={handleSave}
          className={`h-7 text-xs ${
            error ? 'border-red-500 focus:border-red-500' : saved ? 'border-green-500' : ''
          } ${field === 'sku' ? 'font-mono w-36' : 'w-24'}`}
          min={field === 'stockQuantity' ? 0 : undefined}
          step={field === 'price' ? 0.01 : undefined}
          disabled={saving}
        />
        {saving && <Loader2 className="h-3 w-3 animate-spin text-gray-400" />}
        {saved && <Check className="h-3 w-3 text-green-500" />}
      </div>
      {error && <p className="absolute top-full mt-0.5 text-[10px] text-red-500">{error}</p>}
    </div>
  );
}
