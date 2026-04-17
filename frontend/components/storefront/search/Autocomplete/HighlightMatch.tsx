'use client';

import React, { type FC } from 'react';

export interface HighlightMatchProps {
  text: string;
  query: string;
}

/**
 * Wraps matching portions of `text` in <mark> tags.
 * Escapes regex special characters in the query.
 */
const HighlightMatch: FC<HighlightMatchProps> = ({ text, query }) => {
  if (!query.trim()) return <>{text}</>;

  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`(${escaped})`, 'gi');
  const parts = text.split(regex);

  return (
    <>
      {parts.map((part, i) =>
        regex.test(part) ? (
          <mark
            key={i}
            className="bg-green-100 text-green-900 rounded-sm px-0.5 dark:bg-green-900/40 dark:text-green-200"
          >
            {part}
          </mark>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  );
};

export default HighlightMatch;
