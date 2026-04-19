'use client';

import { Card, CardContent } from '@/components/ui/card';
import { SEO_TEST_IDS } from '@/components/seo/SEOTestIds';

interface GooglePreviewProps {
  title: string;
  description: string;
  url: string;
}

export function GooglePreview({ title, description, url }: GooglePreviewProps) {
  const truncatedTitle = title.length > 60 ? `${title.slice(0, 60)}...` : title;
  const truncatedDescription = description.length > 160 ? `${description.slice(0, 160)}...` : description;

  return (
    <Card data-testid={SEO_TEST_IDS.googlePreview}>
      <CardContent className="space-y-1 p-4">
        <h3 className="cursor-pointer text-xl leading-snug text-blue-700 hover:underline">
          {truncatedTitle}
        </h3>
        <p className="text-sm text-green-700">{url}</p>
        <p className="text-sm leading-relaxed text-muted-foreground">
          {truncatedDescription}
        </p>
      </CardContent>
    </Card>
  );
}
