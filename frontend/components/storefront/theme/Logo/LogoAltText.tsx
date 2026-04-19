'use client';

import { Info } from 'lucide-react';

export interface LogoAltTextProps {
  value: string;
  onChange: (text: string) => void;
  storeName?: string;
  maxLength?: number;
  required?: boolean;
}

export function LogoAltText({
  value,
  onChange,
  storeName,
  maxLength = 125,
  required = false,
}: LogoAltTextProps) {
  const remaining = maxLength - value.length;
  const tooShort = value.length > 0 && value.length < 5;
  const defaultSuggestion = storeName ? `${storeName} Logo` : 'Store Logo';

  const handleUseDefault = () => {
    onChange(defaultSuggestion);
  };

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-gray-700">
        Logo Alt Text
        {required && <span className="ml-1 text-red-500">*</span>}
      </label>

      <p className="text-xs text-gray-500">
        Alternative text for accessibility (announced by screen readers)
      </p>

      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value.slice(0, maxLength))}
        placeholder={`e.g., ${defaultSuggestion}`}
        maxLength={maxLength}
        className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      />

      <div className="flex items-center justify-between text-xs">
        <span className={remaining < 20 ? 'text-amber-600' : 'text-gray-400'}>
          {value.length} / {maxLength} characters
        </span>
        {!value && (
          <button
            type="button"
            onClick={handleUseDefault}
            className="text-blue-600 hover:underline"
          >
            Use default: &quot;{defaultSuggestion}&quot;
          </button>
        )}
      </div>

      {tooShort && (
        <p className="text-xs text-amber-600">
          Alt text should be more descriptive (at least 5 characters)
        </p>
      )}

      {/* Best practices */}
      <details className="group">
        <summary className="flex cursor-pointer items-center gap-1 text-xs text-gray-500 hover:text-gray-700">
          <Info className="h-3 w-3" />
          Alt text best practices
        </summary>
        <ul className="mt-1 space-y-1 pl-4 text-xs text-gray-500">
          <li>&bull; &quot;Acme Store Logo&quot; — brand name + context</li>
          <li>&bull; &quot;TechMart Home&quot; — descriptive and concise</li>
          <li>&bull; Avoid generic text like &quot;image&quot; or &quot;logo&quot;</li>
          <li>&bull; Keep between 20-60 characters for best results</li>
        </ul>
      </details>
    </div>
  );
}
