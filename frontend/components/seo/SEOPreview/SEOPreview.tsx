'use client';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { SEO_TEST_IDS } from '@/components/seo/SEOTestIds';
import { GooglePreview } from './GooglePreview';
import { SocialPreview } from './SocialPreview';
import { TitleLengthCheck } from './TitleLengthCheck';
import { DescriptionLengthCheck } from './DescriptionLengthCheck';

interface SEOPreviewProps {
  title: string;
  description: string;
  url: string;
  image?: string;
}

export function SEOPreview({ title, description, url, image }: SEOPreviewProps) {
  return (
    <div className="space-y-4" data-testid={SEO_TEST_IDS.seoPreview}>
      <TitleLengthCheck title={title} />
      <DescriptionLengthCheck description={description} />

      <Tabs defaultValue="google">
        <TabsList>
          <TabsTrigger value="google">Google</TabsTrigger>
          <TabsTrigger value="social">Social</TabsTrigger>
        </TabsList>
        <TabsContent value="google">
          <GooglePreview title={title} description={description} url={url} />
        </TabsContent>
        <TabsContent value="social">
          <SocialPreview title={title} description={description} url={url} image={image} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
