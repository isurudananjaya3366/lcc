// ================================================================
// Settings Object Store — Task 23
// ================================================================
// Key-value store for terminal configuration, tax rates,
// payment methods, and other runtime settings.
// ================================================================

import { idbService } from '../indexeddb';
import { ObjectStoreNames, type Setting } from '../schema';

const STORE = ObjectStoreNames.SETTINGS;

// ── Well-known keys ────────────────────────────────────────────

export const SettingKeys = {
  TERMINAL_ID: 'terminal_id',
  TERMINAL_NAME: 'terminal_name',
  TERMINAL_LOCATION: 'terminal_location',
  DEFAULT_TAX_RATE: 'default_tax_rate',
  TAX_CATEGORIES: 'tax_categories',
  PAYMENT_METHODS: 'payment_methods',
  RECEIPT_TEMPLATE: 'receipt_template',
  RECEIPT_FOOTER: 'receipt_footer',
  QUICK_BUTTONS: 'quick_buttons',
  CURRENCY: 'currency',
  TIMEZONE: 'timezone',
} as const;

// ── Types ──────────────────────────────────────────────────────

export interface TaxRate {
  name: string;
  rate: number;
  is_default: boolean;
}

export interface PaymentMethod {
  id: string;
  name: string;
  enabled: boolean;
  icon?: string;
}

export interface TerminalSettings {
  terminal_id: string;
  terminal_name: string;
  terminal_location: string;
}

// ── Service ────────────────────────────────────────────────────

class SettingsService {
  async setSetting(key: string, value: unknown): Promise<void> {
    const setting: Setting = {
      key,
      value,
      updated_at: new Date().toISOString(),
    };
    await idbService.put(STORE, setting);
  }

  async getSetting<T = unknown>(key: string, defaultValue?: T): Promise<T> {
    const setting = await idbService.get<Setting>(STORE, key);
    return (setting?.value as T) ?? (defaultValue as T);
  }

  async getAllSettings(): Promise<Setting[]> {
    return idbService.getAll<Setting>(STORE);
  }

  async bulkSetSettings(entries: Record<string, unknown>): Promise<void> {
    const settings: Setting[] = Object.entries(entries).map(([key, value]) => ({
      key,
      value,
      updated_at: new Date().toISOString(),
    }));
    await idbService.bulkPut(STORE, settings);
  }

  async deleteSetting(key: string): Promise<void> {
    await idbService.delete(STORE, key);
  }

  // ── Domain helpers ───────────────────────────────────────────

  async getTerminalSettings(): Promise<TerminalSettings> {
    const [id, name, location] = await Promise.all([
      this.getSetting<string>(SettingKeys.TERMINAL_ID, ''),
      this.getSetting<string>(SettingKeys.TERMINAL_NAME, ''),
      this.getSetting<string>(SettingKeys.TERMINAL_LOCATION, ''),
    ]);
    return {
      terminal_id: id,
      terminal_name: name,
      terminal_location: location,
    };
  }

  async updateTerminalSettings(config: TerminalSettings): Promise<void> {
    await this.bulkSetSettings({
      [SettingKeys.TERMINAL_ID]: config.terminal_id,
      [SettingKeys.TERMINAL_NAME]: config.terminal_name,
      [SettingKeys.TERMINAL_LOCATION]: config.terminal_location,
    });
  }

  async getTaxRates(): Promise<TaxRate[]> {
    return this.getSetting<TaxRate[]>(SettingKeys.TAX_CATEGORIES, []);
  }

  async getDefaultTaxRate(): Promise<number> {
    return this.getSetting<number>(SettingKeys.DEFAULT_TAX_RATE, 0);
  }

  async updateTaxRates(rates: TaxRate[]): Promise<void> {
    await this.setSetting(SettingKeys.TAX_CATEGORIES, rates);
    const defaultRate = rates.find((r) => r.is_default);
    if (defaultRate) {
      await this.setSetting(SettingKeys.DEFAULT_TAX_RATE, defaultRate.rate);
    }
  }

  async getPaymentMethods(): Promise<PaymentMethod[]> {
    return this.getSetting<PaymentMethod[]>(SettingKeys.PAYMENT_METHODS, []);
  }

  async isPaymentMethodEnabled(methodId: string): Promise<boolean> {
    const methods = await this.getPaymentMethods();
    return methods.some((m) => m.id === methodId && m.enabled);
  }

  async updatePaymentMethods(methods: PaymentMethod[]): Promise<void> {
    await this.setSetting(SettingKeys.PAYMENT_METHODS, methods);
  }
}

export const settingsService = new SettingsService();
