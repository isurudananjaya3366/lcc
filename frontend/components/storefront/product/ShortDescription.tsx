'use client';

import { useState } from 'react';

interface ShortDescriptionProps {
  description: string;
  maxLength?: number;
}

export function ShortDescription({ description, maxLength = 200 }: ShortDescriptionProps) {
  const [expanded, setExpanded] = useState(false);
  const isLong = description.length > maxLength;
  const displayText =
    !isLong || expanded
      ? description
      : `${description.slice(0, maxLength).trimEnd()}…`;

  return (
    <div>
      <p className="text-sm leading-relaxed text-gray-700">{displayText}</p>
      {isLong && (
        <button
          onClick={() => setExpanded((prev) => !prev)}
          className="mt-1 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
        >
          {expanded ? 'Read less' : 'Read more'}
        </button>
      )}
    </div>
  );
}
