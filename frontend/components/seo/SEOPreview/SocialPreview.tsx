'use client';

import { Card, CardContent } from '@/components/ui/card';
import { SEO_TEST_IDS } from '@/components/seo/SEOTestIds';

interface SocialPreviewProps {
  title: string;
  description: string;
  url: string;
  image?: string;
}

export function SocialPreview({ title, description, url, image }: SocialPreviewProps) {
  const domain = (() => {
    try {
      return new URL(url).hostname;
    } catch {
      return url;
    }
  })();

  return (
    <Card className="overflow-hidden" data-testid={SEO_TEST_IDS.socialPreview}>
      {image ? (
        <div className="aspect-video w-full overflow-hidden bg-muted">
          <img
            src={image}
            alt={title}
            className="h-full w-full object-cover"
          />
        </div>
      ) : (
        <div className="flex aspect-video w-full items-center justify-center bg-muted">
          <span className="text-sm text-muted-foreground">No image set</span>
        </div>
      )}
      <CardContent className="space-y-1 p-4">
        <p className="text-xs uppercase text-muted-foreground">{domain}</p>
        <h3 className="font-semibold leading-snug">{title}</h3>
        <p className="text-sm text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}
