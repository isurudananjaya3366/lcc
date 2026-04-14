'use client';

import { useState, useCallback } from 'react';
import { Download, Copy, Check, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/cn';

export interface BackupCodesDisplayProps {
  codes: string[];
  onContinue?: () => void;
  className?: string;
}

export function BackupCodesDisplay({ codes, onContinue, className }: BackupCodesDisplayProps) {
  const [copied, setCopied] = useState(false);

  const formatCode = (code: string) => {
    const cleaned = code.replace(/[^A-Za-z0-9]/g, '');
    if (cleaned.length <= 4) return cleaned.toUpperCase();
    return `${cleaned.slice(0, 4)}-${cleaned.slice(4)}`.toUpperCase();
  };

  const handleCopy = useCallback(async () => {
    const text = codes.map(formatCode).join('\n');
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [codes]);

  const handleDownload = useCallback(() => {
    const text = [
      'LankaCommerce Cloud - Backup Codes',
      '===================================',
      `Generated: ${new Date().toLocaleDateString()}`,
      '',
      'Each code can only be used once.',
      'Store these codes in a safe place.',
      '',
      ...codes.map((code, i) => `${i + 1}. ${formatCode(code)}`),
    ].join('\n');

    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'lankacommerce-backup-codes.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [codes]);

  return (
    <div className={cn('space-y-4', className)}>
      {/* Warning */}
      <div className="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 p-3">
        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
        <div className="text-sm text-amber-800">
          <p className="font-medium">Save these codes now</p>
          <p className="mt-1">
            Each backup code can only be used once. Store them in a secure location. You will not be
            able to see these codes again.
          </p>
        </div>
      </div>

      {/* Codes Grid */}
      <div className="grid grid-cols-2 gap-2 rounded-lg border bg-gray-50 p-4">
        {codes.map((code, index) => (
          <div
            key={index}
            className="rounded bg-white px-3 py-2 text-center font-mono text-sm tracking-wider text-gray-800"
          >
            {formatCode(code)}
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <button
          type="button"
          onClick={handleDownload}
          className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
        >
          <Download className="h-4 w-4" />
          Download
        </button>
        <button
          type="button"
          onClick={handleCopy}
          className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
        >
          {copied ? (
            <>
              <Check className="h-4 w-4 text-green-600" />
              <span className="text-green-600">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="h-4 w-4" />
              Copy
            </>
          )}
        </button>
      </div>

      {onContinue && (
        <button
          type="button"
          onClick={onContinue}
          className="w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700"
        >
          I&apos;ve Saved My Codes
        </button>
      )}
    </div>
  );
}
