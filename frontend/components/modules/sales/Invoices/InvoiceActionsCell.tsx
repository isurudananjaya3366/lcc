'use client';

import { useRouter } from 'next/navigation';
import { Eye, Download, Mail, XCircle, MoreVertical } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import type { Invoice } from '@/services/api/invoiceService';

interface InvoiceActionsCellProps {
  invoice: Invoice;
  onSend?: (invoice: Invoice) => void;
  onVoid?: (invoice: Invoice) => void;
  onDownload?: (invoice: Invoice) => void;
}

const sendableStatuses = ['draft', 'sent', 'overdue'];
const voidableStatuses = ['draft', 'sent', 'partially_paid'];
const downloadableStatuses = ['sent', 'paid', 'partially_paid', 'overdue', 'void'];

export function InvoiceActionsCell({
  invoice,
  onSend,
  onVoid,
  onDownload,
}: InvoiceActionsCellProps) {
  const router = useRouter();

  const canSend = sendableStatuses.includes(invoice.status);
  const canVoid = voidableStatuses.includes(invoice.status);
  const canDownload = downloadableStatuses.includes(invoice.status);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <MoreVertical className="h-4 w-4" />
          <span className="sr-only">Invoice actions</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-[160px]">
        <DropdownMenuItem onClick={() => router.push(`/invoices/${invoice.id}`)}>
          <Eye className="mr-2 h-4 w-4" />
          View Details
        </DropdownMenuItem>

        {canDownload && (
          <DropdownMenuItem onClick={() => onDownload?.(invoice)}>
            <Download className="mr-2 h-4 w-4" />
            Download PDF
          </DropdownMenuItem>
        )}

        {canSend && (
          <DropdownMenuItem onClick={() => onSend?.(invoice)}>
            <Mail className="mr-2 h-4 w-4" />
            Send Invoice
          </DropdownMenuItem>
        )}

        {canVoid && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => onVoid?.(invoice)}
              className="text-red-600 dark:text-red-400"
            >
              <XCircle className="mr-2 h-4 w-4" />
              Void Invoice
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
