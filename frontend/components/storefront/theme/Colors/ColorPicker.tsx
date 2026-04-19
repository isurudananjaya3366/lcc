'use client';

import { useCallback, useId, useRef } from 'react';
import { ColorSwatchPreview } from './ColorSwatchPreview';
import { HexInput } from './HexInput';

interface ColorPickerProps {
  value: string;
  onChange: (color: string) => void;
  label: string;
  description?: string;
  disabled?: boolean;
  error?: string;
  showCopy?: boolean;
}

export function ColorPicker({
  value,
  onChange,
  label,
  description,
  disabled = false,
  error,
}: ColorPickerProps) {
  const inputId = useId();
  const colorInputRef = useRef<HTMLInputElement>(null);

  const handleNativeChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange(e.target.value);
    },
    [onChange]
  );

  const openNativePicker = useCallback(() => {
    colorInputRef.current?.click();
  }, []);

  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={inputId} className="text-sm font-medium text-gray-700">
        {label}
      </label>
      {description && (
        <p id={`${inputId}-desc`} className="text-xs text-gray-500">
          {description}
        </p>
      )}
      <div className="flex items-center gap-3">
        <ColorSwatchPreview
          color={value}
          size="md"
          onClick={openNativePicker}
          disabled={disabled}
        />
        <HexInput value={value} onChange={onChange} disabled={disabled} error={error} />
        <input
          ref={colorInputRef}
          id={inputId}
          type="color"
          value={value}
          onChange={handleNativeChange}
          disabled={disabled}
          aria-label={label}
          aria-describedby={description ? `${inputId}-desc` : undefined}
          className="h-10 w-10 cursor-pointer rounded border border-gray-300 p-0.5 disabled:cursor-not-allowed disabled:opacity-50"
        />
      </div>
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}
