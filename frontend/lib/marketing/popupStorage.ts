/**
 * Popup Display State Management — localStorage-based tracking
 */

import type { PopupConfig, PopupDisplayState } from '@/types/marketing/popup.types';

const STORAGE_KEY = 'marketing_popup_state';

function getState(): PopupDisplayState {
  if (typeof window === 'undefined') return { shown: {}, dismissed: [], lastShown: {} };
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : { shown: {}, dismissed: [], lastShown: {} };
  } catch {
    return { shown: {}, dismissed: [], lastShown: {} };
  }
}

function setState(state: PopupDisplayState): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Storage full — silently fail
  }
}

/** Record that a popup was shown */
export function recordPopupShown(popupId: string): void {
  const state = getState();
  state.shown[popupId] = (state.shown[popupId] || 0) + 1;
  state.lastShown[popupId] = new Date().toISOString();
  setState(state);
}

/** Record that a popup was dismissed */
export function recordPopupDismissed(popupId: string): void {
  const state = getState();
  if (!state.dismissed.includes(popupId)) {
    state.dismissed.push(popupId);
  }
  setState(state);
}

/** Check if a popup should be displayed based on frequency rules */
export function shouldShowPopup(popup: PopupConfig): boolean {
  const state = getState();
  const now = new Date();

  // Check date range
  if (new Date(popup.startDate) > now || new Date(popup.endDate) < now) return false;
  if (!popup.isActive) return false;

  // Check frequency
  const showCount = state.shown[popup.id] || 0;
  const lastShown = state.lastShown[popup.id];

  switch (popup.frequency) {
    case 'once':
      return showCount === 0;
    case 'session':
      return !state.dismissed.includes(popup.id);
    case 'daily': {
      if (!lastShown) return true;
      const lastDate = new Date(lastShown).toDateString();
      return lastDate !== now.toDateString();
    }
    case 'always':
      return true;
    default:
      return false;
  }
}

/** Clear popup state (for testing/reset) */
export function clearPopupState(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(STORAGE_KEY);
}
