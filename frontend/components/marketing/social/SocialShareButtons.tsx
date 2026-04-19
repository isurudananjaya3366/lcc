'use client';

import { useState } from 'react';
import { Share2, Check, Copy, Facebook, Twitter, Linkedin } from 'lucide-react';
import { WhatsAppIcon } from '../whatsapp/WhatsAppIcon';
import { openShareDialog, nativeShare, getShareUrl } from '@/lib/marketing/share';
import type { ShareData, SocialPlatform } from '@/types/marketing/social.types';

interface SocialShareButtonsProps {
  data: ShareData;
  platforms?: SocialPlatform[];
  variant?: 'icons' | 'buttons' | 'compact';
  className?: string;
}

const platformConfig: Record<SocialPlatform, { icon: typeof Share2; label: string; color: string }> = {
  facebook: { icon: Facebook, label: 'Facebook', color: 'hover:text-[#1877F2]' },
  twitter: { icon: Twitter, label: 'Twitter', color: 'hover:text-[#1DA1F2]' },
  whatsapp: { icon: Share2, label: 'WhatsApp', color: 'hover:text-[#25D366]' },
  linkedin: { icon: Linkedin, label: 'LinkedIn', color: 'hover:text-[#0A66C2]' },
  pinterest: { icon: Share2, label: 'Pinterest', color: 'hover:text-[#E60023]' },
  email: { icon: Share2, label: 'Email', color: 'hover:text-gray-700' },
  copy: { icon: Copy, label: 'Copy Link', color: 'hover:text-gray-700' },
};

const DEFAULT_PLATFORMS: SocialPlatform[] = ['facebook', 'twitter', 'whatsapp', 'linkedin', 'copy'];

export function SocialShareButtons({
  data,
  platforms = DEFAULT_PLATFORMS,
  variant = 'icons',
  className = '',
}: SocialShareButtonsProps) {
  const [copied, setCopied] = useState(false);

  const handleShare = async (platform: SocialPlatform) => {
    if (platform === 'copy') {
      await navigator.clipboard.writeText(data.url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      return;
    }
    openShareDialog(platform, data);
  };

  const handleNativeShare = async () => {
    const success = await nativeShare(data);
    if (!success) {
      // Fallback — do nothing, buttons are visible
    }
  };

  if (variant === 'compact') {
    return (
      <button
        onClick={handleNativeShare}
        className={`inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 ${className}`}
        type="button"
      >
        <Share2 className="h-4 w-4" />
        Share
      </button>
    );
  }

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {variant === 'buttons' && <span className="text-sm text-gray-500">Share:</span>}
      {platforms.map((platform) => {
        const config = platformConfig[platform];
        const Icon = platform === 'whatsapp' ? WhatsAppIcon : config.icon;
        const isCopied = platform === 'copy' && copied;

        return (
          <button
            key={platform}
            onClick={() => handleShare(platform)}
            className={`rounded-full p-2 text-gray-400 transition-colors hover:bg-gray-100 ${config.color}`}
            type="button"
            title={isCopied ? 'Copied!' : config.label}
            aria-label={config.label}
          >
            {isCopied ? <Check className="h-4 w-4 text-green-500" /> : <Icon className="h-4 w-4" />}
          </button>
        );
      })}
    </div>
  );
}
