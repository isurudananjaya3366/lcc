'use client';

import { Textarea } from '@/components/ui/textarea';

interface DescriptionEditorProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export function DescriptionEditor({
  value,
  onChange,
  disabled = false,
}: DescriptionEditorProps) {
  const charCount = value.length;
  const maxChars = 5000;

  const getCountColor = () => {
    if (charCount > maxChars) return 'text-red-600 dark:text-red-400';
    if (charCount > 4500) return 'text-amber-600 dark:text-amber-400';
    return 'text-gray-500 dark:text-gray-400';
  };

  return (
    <div className="space-y-1">
      <Textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Describe the product features and benefits"
        rows={5}
        disabled={disabled}
        className="resize-y"
      />
      <div className="flex justify-end">
        <span className={`text-xs ${getCountColor()}`}>
          {charCount.toLocaleString()} / {maxChars.toLocaleString()} characters
        </span>
      </div>
    </div>
  );
}
