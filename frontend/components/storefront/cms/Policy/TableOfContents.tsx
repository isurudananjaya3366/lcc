'use client';

import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import { Card } from '@/components/ui/card';

interface TableOfContentsProps {
  sections: { id: string; title: string }[];
}

export function TableOfContents({ sections }: TableOfContentsProps) {
  const [activeId, setActiveId] = useState<string>('');

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id);
          }
        }
      },
      { rootMargin: '-80px 0px -60% 0px', threshold: 0.1 }
    );

    for (const section of sections) {
      const el = document.getElementById(section.id);
      if (el) observer.observe(el);
    }

    return () => observer.disconnect();
  }, [sections]);

  return (
    <Card className="sticky top-24 p-4">
      <h3 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">
        On this page
      </h3>
      <nav aria-label="Table of contents">
        <ul className="space-y-1">
          {sections.map((section) => (
            <li key={section.id}>
              <a
                href={`#${section.id}`}
                className={cn(
                  'block text-sm py-1 px-2 rounded-md transition-colors',
                  activeId === section.id
                    ? 'bg-primary/10 text-primary font-medium'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                )}
              >
                {section.title}
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </Card>
  );
}
