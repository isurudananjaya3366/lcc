/**
 * FormData Builder
 *
 * Utility for building FormData objects from JavaScript objects.
 * Handles nested objects, arrays, File objects, Blob objects,
 * and proper serialization.
 */

// ── Types ──────────────────────────────────────────────────────

export type FormDataArrayFormat = 'repeat' | 'indices' | 'brackets';
export type FormDataNestingFormat = 'dots' | 'brackets';

export interface FormDataOptions {
  arrayFormat?: FormDataArrayFormat;
  nestingFormat?: FormDataNestingFormat;
  skipNull?: boolean;
  skipEmptyString?: boolean;
  defaultFilename?: string;
  dateFormat?: 'iso' | 'timestamp';
}

const DEFAULT_OPTIONS: Required<FormDataOptions> = {
  arrayFormat: 'repeat',
  nestingFormat: 'dots',
  skipNull: false,
  skipEmptyString: false,
  defaultFilename: 'file',
  dateFormat: 'iso',
};

// ── Core ───────────────────────────────────────────────────────

export function buildFormData(
  data: Record<string, unknown>,
  options?: FormDataOptions
): FormData {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  const formData = new FormData();
  appendFields(formData, data, '', opts);
  return formData;
}

function appendFields(
  fd: FormData,
  obj: Record<string, unknown>,
  prefix: string,
  opts: Required<FormDataOptions>
): void {
  for (const key of Object.keys(obj)) {
    const value = obj[key];
    const fullKey = prefix ? joinKey(prefix, key, opts.nestingFormat) : key;

    if (value === undefined) continue;
    if (value === null) {
      if (opts.skipNull) continue;
      fd.append(fullKey, '');
      continue;
    }
    if (typeof value === 'string') {
      if (value === '' && opts.skipEmptyString) continue;
      fd.append(fullKey, value);
    } else if (typeof value === 'number' || typeof value === 'boolean') {
      fd.append(fullKey, String(value));
    } else if (value instanceof Date) {
      fd.append(
        fullKey,
        opts.dateFormat === 'timestamp'
          ? String(value.getTime())
          : value.toISOString()
      );
    } else if (value instanceof File) {
      fd.append(fullKey, value, value.name);
    } else if (value instanceof Blob) {
      fd.append(fullKey, value, opts.defaultFilename);
    } else if (Array.isArray(value)) {
      appendArray(fd, fullKey, value, opts);
    } else if (typeof value === 'object') {
      appendFields(fd, value as Record<string, unknown>, fullKey, opts);
    }
  }
}

function joinKey(
  prefix: string,
  key: string,
  format: FormDataNestingFormat
): string {
  return format === 'brackets' ? `${prefix}[${key}]` : `${prefix}.${key}`;
}

function appendArray(
  fd: FormData,
  key: string,
  values: unknown[],
  opts: Required<FormDataOptions>
): void {
  values.forEach((value, index) => {
    let arrayKey: string;
    switch (opts.arrayFormat) {
      case 'indices':
        arrayKey = `${key}[${index}]`;
        break;
      case 'brackets':
        arrayKey = `${key}[]`;
        break;
      case 'repeat':
      default:
        arrayKey = key;
        break;
    }

    if (value instanceof File) {
      fd.append(arrayKey, value, value.name);
    } else if (value instanceof Blob) {
      fd.append(arrayKey, value, opts.defaultFilename);
    } else if (value !== null && value !== undefined) {
      fd.append(arrayKey, String(value));
    }
  });
}

// ── Helpers ────────────────────────────────────────────────────

export function appendToFormData(
  existing: FormData,
  data: Record<string, unknown>,
  options?: FormDataOptions
): FormData {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  appendFields(existing, data, '', opts);
  return existing;
}

export function formDataToObject(fd: FormData): Record<string, string | File> {
  const result: Record<string, string | File> = {};
  fd.forEach((value, key) => {
    result[key] = value instanceof File ? value : String(value);
  });
  return result;
}

export function cloneFormData(fd: FormData): FormData {
  const clone = new FormData();
  fd.forEach((value, key) => {
    clone.append(key, value);
  });
  return clone;
}
