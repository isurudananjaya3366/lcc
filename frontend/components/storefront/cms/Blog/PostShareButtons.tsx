'use client';

import { useState } from 'react';
import { Share2, Copy, Check } from 'lucide-react';

import { Button } from '@/components/ui/button';

interface PostShareButtonsProps {
  title: string;
  slug: string;
}

export function PostShareButtons({ title, slug }: PostShareButtonsProps) {
  const [copied, setCopied] = useState(false);

  const url = typeof window !== 'undefined'
    ? `${window.location.origin}/blog/${slug}`
    : `/blog/${slug}`;

  const encodedUrl = encodeURIComponent(url);
  const encodedTitle = encodeURIComponent(title);

  const shareLinks = [
    {
      label: 'Facebook',
      href: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
    },
    {
      label: 'X',
      href: `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`,
    },
    {
      label: 'WhatsApp',
      href: `https://wa.me/?text=${encodedTitle}%20${encodedUrl}`,
    },
  ];

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API not available
    }
  };

  return (
    <div className="flex items-center gap-3 py-6 border-t">
      <Share2 className="h-4 w-4 text-muted-foreground" />
      <span className="text-sm font-medium text-muted-foreground">Share:</span>
      {shareLinks.map((link) => (
        <Button
          key={link.label}
          variant="outline"
          size="sm"
          asChild
        >
          <a href={link.href} target="_blank" rel="noopener noreferrer">
            {link.label}
          </a>
        </Button>
      ))}
      <Button variant="outline" size="sm" onClick={handleCopy}>
        {copied ? (
          <>
            <Check className="h-4 w-4 mr-1" />
            Copied
          </>
        ) : (
          <>
            <Copy className="h-4 w-4 mr-1" />
            Copy Link
          </>
        )}
      </Button>
    </div>
  );
}
