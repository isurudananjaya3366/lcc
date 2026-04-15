'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Download, FileText, Sheet, FileJson, Loader2 } from 'lucide-react';
import type { Attendance } from '@/types/hr';

interface ExportAttendanceProps {
  records: Attendance[];
  startDate: string;
  endDate: string;
  disabled?: boolean;
}

function formatDate(d?: string): string {
  if (!d) return '';
  return new Date(d).toLocaleDateString('en-LK');
}

function formatTime(t?: string): string {
  if (!t) return '';
  return new Date(t).toLocaleTimeString('en-LK', { hour: '2-digit', minute: '2-digit' });
}

function escapeCSV(v: string): string {
  if (v.includes(',') || v.includes('"') || v.includes('\n')) {
    return `"${v.replace(/"/g, '""')}"`;
  }
  return v;
}

function buildCSVContent(records: Attendance[]): string {
  const headers = ['Employee ID', 'Date', 'Check In', 'Check Out', 'Work Hours', 'Status'];
  const rows = records.map((r) => [
    escapeCSV(r.employeeId),
    escapeCSV(formatDate(r.date)),
    escapeCSV(formatTime(r.checkInTime)),
    escapeCSV(formatTime(r.checkOutTime)),
    String(r.workHours ?? 0),
    escapeCSV(r.status),
  ]);
  return [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
}

function downloadBlob(content: string, filename: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export function ExportAttendance({ records, startDate, endDate, disabled }: ExportAttendanceProps) {
  const [exporting, setExporting] = useState(false);
  const baseName = `attendance-report-${startDate}-${endDate}`;

  const handleExport = (format: 'csv' | 'xlsx' | 'pdf' | 'json') => {
    setExporting(true);
    try {
      switch (format) {
        case 'csv': {
          const csv = buildCSVContent(records);
          downloadBlob(csv, `${baseName}.csv`, 'text/csv;charset=utf-8;');
          break;
        }
        case 'xlsx': {
          // Generate CSV content with Excel-compatible BOM for .xlsx import
          const csv = '\uFEFF' + buildCSVContent(records);
          downloadBlob(csv, `${baseName}.csv`, 'application/vnd.ms-excel');
          break;
        }
        case 'json': {
          const json = JSON.stringify(records, null, 2);
          downloadBlob(json, `${baseName}.json`, 'application/json');
          break;
        }
        case 'pdf': {
          // Trigger print dialog for PDF generation
          window.print();
          break;
        }
      }
    } finally {
      setExporting(false);
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" disabled={disabled || exporting}>
          {exporting ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Download className="mr-2 h-4 w-4" />
          )}
          Export
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => handleExport('csv')}>
          <Sheet className="mr-2 h-4 w-4" />
          Export as CSV
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleExport('xlsx')}>
          <Sheet className="mr-2 h-4 w-4" />
          Export as Excel
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleExport('pdf')}>
          <FileText className="mr-2 h-4 w-4" />
          Export as PDF
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleExport('json')}>
          <FileJson className="mr-2 h-4 w-4" />
          Export as JSON
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
