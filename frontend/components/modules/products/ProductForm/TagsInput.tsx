'use client';

import { useState, useRef, type KeyboardEvent } from 'react';
import { X } from 'lucide-react';

import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';

interface TagsInputProps {
  value: string[];
  onChange: (value: string[]) => void;
  maxTags?: number;
  placeholder?: string;
  disabled?: boolean;
}

function formatTag(raw: string): string {
  return raw
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '')
    .replace(/^-|-$/g, '');
}

export function TagsInput({
  value,
  onChange,
  maxTags = 20,
  placeholder = 'Add tags...',
  disabled = false,
}: TagsInputProps) {
  const [input, setInput] = useState('');
  const [error, setError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const addTag = (raw: string) => {
    const tag = formatTag(raw);
    setError('');

    if (!tag || tag.length < 2) {
      setError('Tag must be at least 2 characters');
      return;
    }
    if (tag.length > 30) {
      setError('Tag must be 30 characters or less');
      return;
    }
    if (value.includes(tag)) {
      setError('This tag already exists');
      return;
    }
    if (value.length >= maxTags) {
      setError(`Maximum ${maxTags} tags allowed`);
      return;
    }

    onChange([...value, tag]);
    setInput('');
  };

  const removeTag = (index: number) => {
    onChange(value.filter((_, i) => i !== index));
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      if (input.trim()) {
        addTag(input);
      }
    } else if (e.key === 'Backspace' && !input && value.length > 0) {
      removeTag(value.length - 1);
    } else if (e.key === 'Escape') {
      setInput('');
      inputRef.current?.blur();
    }
  };

  return (
    <div className="space-y-1">
      <div
        className={cn(
          'flex min-h-10 flex-wrap items-center gap-1.5 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2',
          disabled && 'cursor-not-allowed opacity-50'
        )}
        onClick={() => inputRef.current?.focus()}
      >
        {value.map((tag, i) => (
          <Badge key={tag} variant="secondary" className="gap-1 text-xs">
            {tag}
            {!disabled && (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  removeTag(i);
                }}
                className="ml-0.5 rounded-full p-0.5 hover:bg-gray-300 dark:hover:bg-gray-600"
                aria-label={`Remove ${tag}`}
              >
                <X className="h-3 w-3" />
              </button>
            )}
          </Badge>
        ))}
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            setError('');
          }}
          onKeyDown={handleKeyDown}
          onBlur={() => {
            if (input.trim()) addTag(input);
          }}
          placeholder={value.length === 0 ? placeholder : ''}
          disabled={disabled}
          className="min-w-[80px] flex-1 bg-transparent outline-none placeholder:text-muted-foreground"
          aria-label="Add tag"
        />
      </div>
      {error && <p className="text-xs text-red-600 dark:text-red-400">{error}</p>}
      {value.length > 0 && (
        <p className="text-xs text-muted-foreground">
          {value.length}/{maxTags} tags
        </p>
      )}
    </div>
  );
}
