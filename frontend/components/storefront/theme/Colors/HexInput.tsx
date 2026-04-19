'use client';

import { useState, useCallback, useEffect } from 'react';
import { Check, X, Copy } from 'lucide-react';
import { cn } from '@/lib/utils';

interface HexInputProps {
  value: string;
  onChange: (hex: string) => void;
  onBlur?: () => void;
  disabled?: boolean;
  error?: string;
  label?: string;
}

const HEX_REGEX = /^#[0-9A-Fa-f]{6}$/;

function normalizeHex(input: string): string {
  let hex = input.replace(/[^0-9A-Fa-f#]/g, '');
  // Remove duplicate # signs
  hex = hex.replace(/#+/g, '#');
  if (!hex.startsWith('#')) {
    hex = '#' + hex;
  }
  return hex.slice(0, 7);
}

export function HexInput({
  value,
  onChange,
  onBlur,
  disabled = false,
  error,
  label,
}: HexInputProps) {
  const [internal, setInternal] = useState(value);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setInternal(value);
  }, [value]);

  const isValid = HEX_REGEX.test(internal);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const normalized = normalizeHex(e.target.value);
      setInternal(normalized);
      if (HEX_REGEX.test(normalized)) {
        onChange(normalized);
      }
    },
    [onChange]
  );

  const handleBlur = useCallback(() => {
    if (HEX_REGEX.test(internal)) {
      onChange(internal);
    } else {
      setInternal(value);
    }
    onBlur?.();
  }, [internal, value, onChange, onBlur]);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // clipboard not available
    }
  }, [value]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Escape') {
        setInternal(value);
        (e.target as HTMLInputElement).blur();
      } else if (e.key === 'Enter') {
        (e.target as HTMLInputElement).blur();
      }
    },
    [value]
  );

  return (
    <div className="flex flex-col gap-1">
      {label && <label className="text-xs font-medium text-gray-600">{label}</label>}
      <div className="flex items-center gap-1">
        <div className="relative">
          <input
            type="text"
            value={internal}
            onChange={handleChange}
            onBlur={handleBlur}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            maxLength={7}
            placeholder="#000000"
            className={cn(
              'w-[110px] rounded border px-2 py-1.5 font-mono text-sm pr-7',
              'focus:outline-none focus:ring-2 focus:ring-blue-500',
              disabled && 'opacity-50 cursor-not-allowed bg-gray-100',
              error
                ? 'border-red-400'
                : isValid
                  ? 'border-green-400'
                  : internal.length > 1
                    ? 'border-red-400'
                    : 'border-gray-300'
            )}
          />
          <span className="absolute right-2 top-1/2 -translate-y-1/2">
            {error || (!isValid && internal.length > 1) ? (
              <X className="h-3.5 w-3.5 text-red-500" />
            ) : isValid ? (
              <Check className="h-3.5 w-3.5 text-green-500" />
            ) : null}
          </span>
        </div>
        <button
          type="button"
          onClick={handleCopy}
          disabled={disabled}
          className="rounded p-1.5 text-gray-500 hover:bg-gray-100 hover:text-gray-700 disabled:opacity-50"
          aria-label="Copy hex value"
          title={copied ? 'Copied!' : 'Copy'}
        >
          {copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
        </button>
      </div>
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}
