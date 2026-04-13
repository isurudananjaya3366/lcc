/**
 * File Helpers
 *
 * Upload with progress, validation, cancellation, and
 * download with filename extraction and browser triggering.
 */

import { buildFormData, type FormDataOptions } from './formDataBuilder';

// ── Upload Types ───────────────────────────────────────────────

export interface FileValidationRules {
  maxSize?: number;
  minSize?: number;
  allowedTypes?: string[];
  allowedExtensions?: string[];
  maxFiles?: number;
  customValidator?: (file: File) => boolean;
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
  speed: number;
  timeRemaining: number;
  file: File;
}

export interface FileUploadOptions {
  onProgress?: (progress: UploadProgress) => void;
  onSuccess?: (response: unknown) => void;
  onError?: (error: Error) => void;
  validation?: FileValidationRules;
  headers?: Record<string, string>;
  fieldName?: string;
  additionalData?: Record<string, unknown>;
  withCredentials?: boolean;
  timeout?: number;
  formDataOptions?: FormDataOptions;
}

export type UploadState =
  | 'pending'
  | 'uploading'
  | 'completed'
  | 'failed'
  | 'cancelled';

export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

// ── Download Types ─────────────────────────────────────────────

export interface DownloadOptions {
  filename?: string;
  onProgress?: (progress: { loaded: number; total: number; percentage: number }) => void;
  headers?: Record<string, string>;
  timeout?: number;
  withCredentials?: boolean;
}

// ── Validation ─────────────────────────────────────────────────

export function validateFile(
  file: File,
  rules: FileValidationRules
): ValidationResult {
  const errors: string[] = [];

  if (rules.maxSize && file.size > rules.maxSize) {
    errors.push(
      `File size (${formatFileSize(file.size)}) exceeds maximum (${formatFileSize(rules.maxSize)})`
    );
  }

  if (rules.minSize && file.size < rules.minSize) {
    errors.push(
      `File size (${formatFileSize(file.size)}) is below minimum (${formatFileSize(rules.minSize)})`
    );
  }

  if (rules.allowedTypes && rules.allowedTypes.length > 0) {
    if (!rules.allowedTypes.includes(file.type)) {
      errors.push(
        `File type "${file.type}" is not allowed. Allowed: ${rules.allowedTypes.join(', ')}`
      );
    }
  }

  if (rules.allowedExtensions && rules.allowedExtensions.length > 0) {
    const ext = getFileExtension(file.name);
    const normalized = rules.allowedExtensions.map((e) =>
      e.startsWith('.') ? e : `.${e}`
    );
    if (!normalized.includes(ext.toLowerCase())) {
      errors.push(
        `File extension "${ext}" is not allowed. Allowed: ${normalized.join(', ')}`
      );
    }
  }

  if (rules.customValidator && !rules.customValidator(file)) {
    errors.push('File failed custom validation');
  }

  return { valid: errors.length === 0, errors };
}

export function validateFiles(
  files: File[],
  rules: FileValidationRules
): ValidationResult {
  const errors: string[] = [];

  if (rules.maxFiles && files.length > rules.maxFiles) {
    errors.push(`Too many files (${files.length}). Maximum: ${rules.maxFiles}`);
  }

  for (const file of files) {
    const result = validateFile(file, rules);
    errors.push(...result.errors);
  }

  return { valid: errors.length === 0, errors };
}

// ── Upload Controller ──────────────────────────────────────────

export class UploadController {
  private xhr: XMLHttpRequest;
  private _state: UploadState = 'pending';
  private _startTime = 0;

  constructor(xhr: XMLHttpRequest) {
    this.xhr = xhr;
  }

  get state(): UploadState {
    return this._state;
  }

  set state(s: UploadState) {
    this._state = s;
  }

  get startTime(): number {
    return this._startTime;
  }

  set startTime(t: number) {
    this._startTime = t;
  }

  abort(): void {
    if (this._state === 'uploading') {
      this.xhr.abort();
      this._state = 'cancelled';
    }
  }
}

// ── Upload ─────────────────────────────────────────────────────

export function uploadFile(
  file: File,
  url: string,
  options: FileUploadOptions = {}
): UploadController {
  const {
    onProgress,
    onSuccess,
    onError,
    validation,
    headers = {},
    fieldName = 'file',
    additionalData = {},
    withCredentials = false,
    timeout = 0,
    formDataOptions,
  } = options;

  // Validate
  if (validation) {
    const result = validateFile(file, validation);
    if (!result.valid) {
      const err = new Error(result.errors.join('; '));
      onError?.(err);
      const xhr = new XMLHttpRequest();
      const ctrl = new UploadController(xhr);
      ctrl.state = 'failed';
      return ctrl;
    }
  }

  // Build FormData
  const fd = buildFormData(
    { [fieldName]: file, ...additionalData },
    formDataOptions
  );

  const xhr = new XMLHttpRequest();
  const controller = new UploadController(xhr);

  xhr.open('POST', url, true);
  xhr.withCredentials = withCredentials;
  xhr.timeout = timeout;

  for (const [key, value] of Object.entries(headers)) {
    xhr.setRequestHeader(key, value);
  }

  // Progress
  xhr.upload.onprogress = (e) => {
    if (!e.lengthComputable || !onProgress) return;
    const elapsed = (Date.now() - controller.startTime) / 1000;
    const speed = elapsed > 0 ? e.loaded / elapsed : 0;
    const remaining = speed > 0 ? (e.total - e.loaded) / speed : 0;
    onProgress({
      loaded: e.loaded,
      total: e.total,
      percentage: Math.round((e.loaded / e.total) * 100),
      speed,
      timeRemaining: remaining,
      file,
    });
  };

  xhr.onload = () => {
    if (xhr.status >= 200 && xhr.status < 300) {
      controller.state = 'completed';
      try {
        onSuccess?.(JSON.parse(xhr.responseText));
      } catch {
        onSuccess?.(xhr.responseText);
      }
    } else {
      controller.state = 'failed';
      onError?.(new Error(`Upload failed with status ${xhr.status}`));
    }
  };

  xhr.onerror = () => {
    controller.state = 'failed';
    onError?.(new Error('Network error during upload'));
  };

  xhr.onabort = () => {
    controller.state = 'cancelled';
    onError?.(new Error('Upload cancelled'));
  };

  xhr.ontimeout = () => {
    controller.state = 'failed';
    onError?.(new Error('Upload timed out'));
  };

  controller.state = 'uploading';
  controller.startTime = Date.now();
  xhr.send(fd);

  return controller;
}

export function uploadFiles(
  files: File[],
  url: string,
  options: FileUploadOptions = {}
): UploadController[] {
  if (options.validation) {
    const result = validateFiles(files, options.validation);
    if (!result.valid) {
      options.onError?.(new Error(result.errors.join('; ')));
      return [];
    }
  }

  return files.map((file) => uploadFile(file, url, options));
}

// ── Download ───────────────────────────────────────────────────

export function downloadFile(
  url: string,
  options: DownloadOptions = {}
): Promise<void> {
  const { filename, onProgress, headers = {}, timeout = 0, withCredentials = false } =
    options;

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.responseType = 'blob';
    xhr.withCredentials = withCredentials;
    xhr.timeout = timeout;

    for (const [key, value] of Object.entries(headers)) {
      xhr.setRequestHeader(key, value);
    }

    xhr.onprogress = (e) => {
      if (!e.lengthComputable || !onProgress) return;
      onProgress({
        loaded: e.loaded,
        total: e.total,
        percentage: Math.round((e.loaded / e.total) * 100),
      });
    };

    xhr.onload = () => {
      if (xhr.status < 200 || xhr.status >= 300) {
        reject(new Error(`Download failed with status ${xhr.status}`));
        return;
      }
      const blob = xhr.response as Blob;
      const resolvedName =
        filename ||
        getFilenameFromHeader(xhr.getResponseHeader('Content-Disposition')) ||
        getFilenameFromUrl(url) ||
        'download';
      triggerDownload(blob, resolvedName);
      resolve();
    };

    xhr.onerror = () => reject(new Error('Network error during download'));
    xhr.ontimeout = () => reject(new Error('Download timed out'));

    xhr.send();
  });
}

// ── Filename Utilities ─────────────────────────────────────────

export function getFilenameFromHeader(header: string | null): string | null {
  if (!header) return null;

  // filename*=utf-8''encoded_name
  const utf8Match = header.match(/filename\*\s*=\s*utf-8''(.+)/i);
  if (utf8Match) return decodeURIComponent(utf8Match[1]);

  // filename="name" or filename=name
  const match = header.match(/filename\s*=\s*"?([^";]+)"?/i);
  return match ? match[1].trim() : null;
}

export function getFilenameFromUrl(url: string): string | null {
  try {
    const pathname = new URL(url, 'http://localhost').pathname;
    const segments = pathname.split('/').filter(Boolean);
    const last = segments[segments.length - 1];
    return last && last.includes('.') ? decodeURIComponent(last) : null;
  } catch {
    return null;
  }
}

export function triggerDownload(blob: Blob, filename: string): void {
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = objectUrl;
  anchor.download = filename;
  anchor.style.display = 'none';
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  setTimeout(() => URL.revokeObjectURL(objectUrl), 100);
}

// ── General Utilities ──────────────────────────────────────────

export function getFileExtension(filename: string): string {
  const idx = filename.lastIndexOf('.');
  return idx >= 0 ? filename.slice(idx) : '';
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  const size = bytes / Math.pow(1024, i);
  return `${size.toFixed(i > 0 ? 1 : 0)} ${units[i]}`;
}

export function getMimeType(filename: string): string {
  const ext = getFileExtension(filename).toLowerCase();
  const map: Record<string, string> = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx':
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xls': 'application/vnd.ms-excel',
    '.xlsx':
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.csv': 'text/csv',
    '.txt': 'text/plain',
    '.zip': 'application/zip',
    '.json': 'application/json',
  };
  return map[ext] || 'application/octet-stream';
}
