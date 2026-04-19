/**
 * WhatsApp Store — persists phone number / availability for the tenant.
 */

import { createStore } from '../utils';
import { whatsappConfig } from '@/config/whatsapp.config';

interface BusinessHours {
  open: string;  // "HH:mm" Colombo time
  close: string;
  days: number[]; // 0=Sun … 6=Sat
}

interface WhatsAppStoreState {
  number: string;
  isAvailable: boolean;
  businessHours: BusinessHours;

  setNumber: (number: string) => void;
  setAvailability: (available: boolean) => void;
  loadFromTenant: (tenantConfig: { whatsappNumber?: string; whatsappBusinessHours?: Partial<BusinessHours> }) => void;
}

const DEFAULT_HOURS: BusinessHours = {
  open: whatsappConfig.workingHours.start,
  close: whatsappConfig.workingHours.end,
  days: whatsappConfig.workingHours.days,
};

export const useWhatsAppStore = createStore<WhatsAppStoreState>(
  'WhatsApp',
  (set) => ({
    number: whatsappConfig.phoneNumber,
    isAvailable: true,
    businessHours: DEFAULT_HOURS,

    setNumber: (number) => {
      set((state) => {
        state.number = number;
      });
    },

    setAvailability: (available) => {
      set((state) => {
        state.isAvailable = available;
      });
    },

    loadFromTenant: (tenantConfig) => {
      set((state) => {
        if (tenantConfig.whatsappNumber) {
          state.number = tenantConfig.whatsappNumber;
        }
        if (tenantConfig.whatsappBusinessHours) {
          state.businessHours = {
            ...DEFAULT_HOURS,
            ...tenantConfig.whatsappBusinessHours,
          };
        }
      });
    },
  }),
  {
    persist: false,
  }
);
