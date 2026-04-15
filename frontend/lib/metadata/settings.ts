import type { Metadata } from 'next';

const APP_NAME = 'LankaCommerce Cloud';

export function createSettingsMetadata(title: string, description: string): Metadata {
  const fullTitle = `${title} - ${APP_NAME}`;
  return {
    title: fullTitle,
    description,
    openGraph: {
      title: fullTitle,
      description,
      type: 'website',
    },
    twitter: {
      card: 'summary',
      title: fullTitle,
      description,
    },
    robots: {
      index: false,
      follow: false,
    },
  };
}
