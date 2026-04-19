'use client';

import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';

interface FAQSearchProps {
  value: string;
  onChange: (v: string) => void;
}

export function FAQSearch({ value, onChange }: FAQSearchProps) {
  return (
    <div className="relative mb-6">
      <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search FAQs..."
        className="pl-10"
      />
    </div>
  );
}
