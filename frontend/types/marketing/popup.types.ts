/**
 * Popup & Modal Types
 */

export type PopupTrigger = 'page_load' | 'exit_intent' | 'scroll' | 'time_delay' | 'click';

export type PopupFrequency = 'once' | 'session' | 'daily' | 'always';
export type PopupSize = 'small' | 'medium' | 'large' | 'fullscreen';
export type PopupPosition = 'center' | 'bottom-left' | 'bottom-right' | 'top-center' | 'bottom-center';

export interface PopupImage {
  url: string;
  alt: string;
  position?: 'top' | 'left' | 'right' | 'background';
}

export interface PopupButton {
  label: string;
  url?: string;
  action?: 'close' | 'submit' | 'link';
  style?: 'primary' | 'secondary' | 'ghost';
}

export interface PopupTriggerConfig {
  type: PopupTrigger;
  delayMs?: number;
  scrollPercentage?: number;
  exitSensitivity?: number;
}

export interface PopupFrequencyConfig {
  type: PopupFrequency;
  cooldownHours?: number;
}

export interface PopupTargeting {
  pages?: string[];
  userSegments?: string[];
  devices?: ('desktop' | 'mobile')[];
}

export interface PopupResponse {
  popup: PopupConfig;
  variant?: string;
}

export interface PopupFilters {
  type?: PopupType;
  trigger?: PopupTrigger;
  isActive?: boolean;
}
export type PopupType = 'newsletter' | 'promotion' | 'announcement' | 'welcome' | 'cart_abandonment';

export interface PopupConfig {
  id: string;
  title: string;
  description?: string;
  type: PopupType;
  trigger: PopupTrigger;
  imageUrl?: string;
  action?: {
    label: string;
    url?: string;
  };
  dismissLabel?: string;
  delayMs?: number;
  scrollPercentage?: number;
  showOnce: boolean;
  frequency: 'once' | 'session' | 'daily' | 'always';
  startDate: string;
  endDate: string;
  pages?: string[];
  isActive: boolean;
}

export interface PopupDisplayState {
  shown: Record<string, number>;
  dismissed: string[];
  lastShown: Record<string, string>;
}
