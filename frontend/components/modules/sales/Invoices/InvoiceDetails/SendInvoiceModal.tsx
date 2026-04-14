'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Send, Loader2, Paperclip } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import type { Invoice } from '@/services/api/invoiceService';

const sendInvoiceSchema = z.object({
  to: z.string().email('Enter a valid email address'),
  cc: z.string().optional(),
  subject: z.string().min(1, 'Subject is required').max(100),
  message: z.string().max(500).optional(),
  attachPdf: z.boolean(),
});

type SendInvoiceFormValues = z.infer<typeof sendInvoiceSchema>;

interface SendInvoiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  invoice: Invoice;
  onSend: (data: SendInvoiceFormValues) => Promise<void>;
}

function formatCurrency(amount: number): string {
  return `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function getDefaultMessage(invoice: Invoice): string {
  return `Dear ${invoice.customerName},

Please find attached your invoice #${invoice.invoiceNumber} dated ${formatDate(invoice.issueDate)}.

Invoice Details:
- Amount: ${formatCurrency(invoice.total)}
- Due Date: ${formatDate(invoice.dueDate)}

Please contact us if you have any questions.

Best regards`;
}

export function SendInvoiceModal({ isOpen, onClose, invoice, onSend }: SendInvoiceModalProps) {
  const [isSending, setIsSending] = useState(false);

  const form = useForm<SendInvoiceFormValues>({
    resolver: zodResolver(sendInvoiceSchema),
    defaultValues: {
      to: '',
      cc: '',
      subject: `Invoice ${invoice.invoiceNumber}`,
      message: getDefaultMessage(invoice),
      attachPdf: true,
    },
  });

  const handleSubmit = async (data: SendInvoiceFormValues) => {
    setIsSending(true);
    try {
      await onSend(data);
      form.reset();
      onClose();
    } finally {
      setIsSending(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Send Invoice</DialogTitle>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="to"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>To</FormLabel>
                  <FormControl>
                    <Input placeholder="customer@example.com" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="cc"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>CC (optional)</FormLabel>
                  <FormControl>
                    <Input placeholder="accounting@example.com" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="subject"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Subject</FormLabel>
                  <FormControl>
                    <Input maxLength={100} {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="message"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Message</FormLabel>
                  <FormControl>
                    <Textarea rows={6} maxLength={500} className="resize-none" {...field} />
                  </FormControl>
                  <div className="text-right text-xs text-gray-400">
                    {field.value?.length || 0}/500
                  </div>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="attachPdf"
              render={({ field }) => (
                <FormItem className="flex items-center gap-2 space-y-0">
                  <FormControl>
                    <Checkbox checked={field.value} onCheckedChange={field.onChange} />
                  </FormControl>
                  <FormLabel className="flex items-center gap-1.5 text-sm font-normal">
                    <Paperclip className="h-3.5 w-3.5" />
                    Attach PDF (Invoice-{invoice.invoiceNumber}.pdf)
                  </FormLabel>
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit" disabled={isSending}>
                {isSending ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Send className="mr-2 h-4 w-4" />
                )}
                Send
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
