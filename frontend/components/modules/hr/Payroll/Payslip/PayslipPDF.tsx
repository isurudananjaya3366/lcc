'use client';

import { Button } from '@/components/ui/button';
import { Download } from 'lucide-react';
import { useDownloadPayslipPdf } from '@/hooks/hr/usePayroll';

interface PayslipPDFProps {
  payrollId: string;
  employeeId: string;
}

export function PayslipPDF({ payrollId, employeeId }: PayslipPDFProps) {
  const downloadMutation = useDownloadPayslipPdf();

  return (
    <Button
      variant="outline"
      onClick={() => downloadMutation.mutate({ payrollId, employeeId })}
      disabled={downloadMutation.isPending}
    >
      <Download className="mr-2 h-4 w-4" />
      {downloadMutation.isPending ? 'Downloading...' : 'Download PDF'}
    </Button>
  );
}
