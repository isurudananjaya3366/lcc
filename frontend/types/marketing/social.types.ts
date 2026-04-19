/**
 * Social Media Sharing Types
 */

export type SocialPlatform = 'facebook' | 'twitter' | 'whatsapp' | 'linkedin' | 'pinterest' | 'email' | 'copy';

export interface ShareData {
  title: string;
  description?: string;
  url: string;
  imageUrl?: string;
  hashtags?: string[];
}

export interface SocialLink {
  platform: SocialPlatform;
  url: string;
  label: string;
}

export interface ShareButtonConfig {
  platform: SocialPlatform;
  icon: string;
  label: string;
  color: string;
  bgColor: string;
}

export interface ShareResult {
  success: boolean;
  platform: SocialPlatform;
  error?: string;
}

export interface ShareOptions {
  windowWidth?: number;
  windowHeight?: number;
  trackingCallback?: (platform: SocialPlatform) => void;
}
