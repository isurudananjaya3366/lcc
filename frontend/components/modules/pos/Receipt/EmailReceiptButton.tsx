'use client';

import { useState } from 'react';
import { Mail, Loader2, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { posService } from '@/services/pos';

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

interface EmailReceiptButtonProps {
  receiptId: string;
}

export function EmailReceiptButton({ receiptId }: EmailReceiptButtonProps) {
  const [showDialog, setShowDialog] = useState(false);
  const [email, setEmail] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');

  const isValid = EMAIL_REGEX.test(email.trim());

  const handleSend = async () => {
    if (!isValid) {
      setError('Please enter a valid email address.');
      return;
    }
    setIsSending(true);
    setError('');
    try {
      await posService.emailReceipt(receiptId, email.trim());
      setSent(true);
      setShowDialog(false);
    } catch {
      setError('Failed to send email. Please try again.');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <>
      <Button
        variant="outline"
        size="sm"
        onClick={() => setShowDialog(true)}
        disabled={sent}
        className="flex-1"
      >
        {sent ? (
          <CheckCircle className="mr-1.5 h-4 w-4 text-green-500" />
        ) : (
          <Mail className="mr-1.5 h-4 w-4" />
        )}
        {sent ? 'Sent' : 'Email (E)'}
      </Button>

      <Dialog open={showDialog} onOpenChange={(v) => !v && setShowDialog(false)}>
        <DialogContent className="sm:max-w-xs">
          <DialogHeader>
            <DialogTitle>Email Receipt</DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-300">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setError('');
                }}
                onKeyDown={(e) => e.key === 'Enter' && isValid && handleSend()}
                placeholder="customer@example.com"
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
                // eslint-disable-next-line jsx-a11y/no-autofocus
                autoFocus
              />
              {error && <p className="mt-1 text-xs text-red-500">{error}</p>}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" size="sm" onClick={() => setShowDialog(false)}>
              Cancel
            </Button>
            <Button size="sm" onClick={handleSend} disabled={!isValid || isSending}>
              {isSending ? (
                <Loader2 className="mr-1.5 h-4 w-4 animate-spin" />
              ) : (
                <Mail className="mr-1.5 h-4 w-4" />
              )}
              Send
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
