'use client';

import { useState, useRef, useCallback } from 'react';
import { Upload, FileUp, AlertCircle, CheckCircle2, ArrowRight, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';

interface ImportResult {
  imported: number;
  updated: number;
  errors: string[];
}

interface FieldMapping {
  label: string;
  key: string;
  required?: boolean;
}

interface ImportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  entityName: string;
  onImport: (file: File, updateExisting: boolean) => Promise<ImportResult>;
  /** Available fields for column mapping */
  fields?: FieldMapping[];
}

type Step = 'upload' | 'mapping' | 'preview' | 'result';

function parseCSVHeader(text: string): string[] {
  const firstLine = text.split('\n')[0] || '';
  return firstLine.split(',').map((h) => h.trim().replace(/^"|"$/g, ''));
}

function parseCSVRows(text: string, maxRows: number): string[][] {
  const lines = text.split('\n').filter((l) => l.trim());
  return lines
    .slice(1, maxRows + 1)
    .map((line) => line.split(',').map((cell) => cell.trim().replace(/^"|"$/g, '')));
}

export function ImportDialog({
  open,
  onOpenChange,
  entityName,
  onImport,
  fields,
}: ImportDialogProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [updateExisting, setUpdateExisting] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<Step>('upload');

  // Column mapping state
  const [csvHeaders, setCsvHeaders] = useState<string[]>([]);
  const [csvPreviewRows, setCsvPreviewRows] = useState<string[][]>([]);
  const [columnMapping, setColumnMapping] = useState<Record<string, string>>({});

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const selected = e.target.files?.[0];
    if (selected) {
      if (!selected.name.endsWith('.csv')) {
        setError('Only CSV files are supported');
        setFile(null);
        return;
      }
      setFile(selected);
      setError(null);
    }
  }

  const processFile = useCallback(async () => {
    if (!file) return;
    const text = await file.text();
    const headers = parseCSVHeader(text);
    const rows = parseCSVRows(text, 5);
    setCsvHeaders(headers);
    setCsvPreviewRows(rows);

    // Auto-map columns based on name matching
    if (fields) {
      const autoMapping: Record<string, string> = {};
      for (const field of fields) {
        const match = headers.find(
          (h) =>
            h.toLowerCase() === field.key.toLowerCase() ||
            h.toLowerCase() === field.label.toLowerCase() ||
            h.toLowerCase().replace(/[_\s-]/g, '') ===
              field.key.toLowerCase().replace(/[_\s-]/g, '')
        );
        if (match) {
          autoMapping[field.key] = match;
        }
      }
      setColumnMapping(autoMapping);
    }
  }, [file, fields]);

  async function handleNext() {
    if (step === 'upload' && fields && fields.length > 0) {
      await processFile();
      setStep('mapping');
    } else if (step === 'upload') {
      await processFile();
      setStep('preview');
    } else if (step === 'mapping') {
      setStep('preview');
    } else if (step === 'preview') {
      await handleImport();
    }
  }

  function handleBack() {
    if (step === 'mapping') setStep('upload');
    else if (step === 'preview') setStep(fields?.length ? 'mapping' : 'upload');
  }

  async function handleImport() {
    if (!file) return;
    setIsImporting(true);
    setError(null);
    try {
      const importResult = await onImport(file, updateExisting);
      setResult(importResult);
      setStep('result');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Import failed');
    } finally {
      setIsImporting(false);
    }
  }

  function handleClose() {
    setFile(null);
    setUpdateExisting(false);
    setResult(null);
    setError(null);
    setStep('upload');
    setCsvHeaders([]);
    setCsvPreviewRows([]);
    setColumnMapping({});
    onOpenChange(false);
  }

  const requiredFieldsMapped = fields
    ? fields.filter((f) => f.required).every((f) => columnMapping[f.key])
    : true;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent
        className={step === 'preview' || step === 'mapping' ? 'max-w-2xl' : 'max-w-md'}
      >
        <DialogHeader>
          <DialogTitle>Import {entityName}</DialogTitle>
          <DialogDescription>
            {step === 'upload' &&
              `Upload a CSV file to import ${entityName.toLowerCase()} records.`}
            {step === 'mapping' && 'Map CSV columns to the correct fields.'}
            {step === 'preview' && 'Review the data before importing.'}
            {step === 'result' && 'Import results.'}
          </DialogDescription>
        </DialogHeader>

        {step === 'result' && result && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-green-600">
              <CheckCircle2 className="h-5 w-5" />
              <span className="font-medium">Import Complete</span>
            </div>
            <div className="text-sm space-y-1">
              <p>Imported: {result.imported} records</p>
              <p>Updated: {result.updated} records</p>
              {result.errors.length > 0 && (
                <div className="mt-2">
                  <p className="font-medium text-destructive">Errors ({result.errors.length}):</p>
                  <ul className="list-disc list-inside text-xs text-destructive mt-1 max-h-32 overflow-y-auto">
                    {result.errors.map((err, i) => (
                      <li key={i}>{err}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            <DialogFooter>
              <Button onClick={handleClose}>Close</Button>
            </DialogFooter>
          </div>
        )}

        {step === 'upload' && (
          <div className="space-y-4">
            <div
              className="border-2 border-dashed rounded-lg p-6 text-center cursor-pointer hover:border-primary/50 transition-colors"
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                className="hidden"
                onChange={handleFileChange}
              />
              <FileUp className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
              {file ? (
                <p className="text-sm font-medium">{file.name}</p>
              ) : (
                <>
                  <p className="text-sm font-medium">Click to select a CSV file</p>
                  <p className="text-xs text-muted-foreground mt-1">Supported format: .csv</p>
                </>
              )}
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="updateExisting"
                checked={updateExisting}
                onCheckedChange={(checked) => setUpdateExisting(checked === true)}
              />
              <Label htmlFor="updateExisting" className="text-sm">
                Update existing records if match found
              </Label>
            </div>

            {error && (
              <div className="flex items-center gap-2 text-sm text-destructive">
                <AlertCircle className="h-4 w-4" />
                {error}
              </div>
            )}

            <DialogFooter>
              <Button variant="outline" onClick={handleClose}>
                Cancel
              </Button>
              <Button onClick={handleNext} disabled={!file}>
                <ArrowRight className="mr-2 h-4 w-4" />
                Next
              </Button>
            </DialogFooter>
          </div>
        )}

        {step === 'mapping' && fields && (
          <div className="space-y-4">
            <div className="space-y-3 max-h-[400px] overflow-y-auto">
              {fields.map((field) => (
                <div key={field.key} className="flex items-center gap-3">
                  <div className="w-40 flex items-center gap-1">
                    <span className="text-sm">{field.label}</span>
                    {field.required && <span className="text-destructive">*</span>}
                  </div>
                  <Select
                    value={columnMapping[field.key] || '_unmapped'}
                    onValueChange={(v) =>
                      setColumnMapping((prev) => ({
                        ...prev,
                        [field.key]: v === '_unmapped' ? '' : v,
                      }))
                    }
                  >
                    <SelectTrigger className="w-48">
                      <SelectValue placeholder="Select column" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="_unmapped">— Skip —</SelectItem>
                      {csvHeaders.map((h) => (
                        <SelectItem key={h} value={h}>
                          {h}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              ))}
            </div>

            {!requiredFieldsMapped && (
              <div className="flex items-center gap-2 text-sm text-destructive">
                <AlertCircle className="h-4 w-4" />
                All required fields must be mapped
              </div>
            )}

            <DialogFooter>
              <Button variant="outline" onClick={handleBack}>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back
              </Button>
              <Button onClick={handleNext} disabled={!requiredFieldsMapped}>
                <ArrowRight className="mr-2 h-4 w-4" />
                Preview
              </Button>
            </DialogFooter>
          </div>
        )}

        {step === 'preview' && (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Badge variant="secondary">{csvPreviewRows.length} rows previewed</Badge>
              {file && <span className="text-xs text-muted-foreground">from {file.name}</span>}
            </div>

            <div className="max-h-[350px] overflow-auto border rounded-md">
              <Table>
                <TableHeader>
                  <TableRow>
                    {csvHeaders.map((h) => (
                      <TableHead key={h} className="text-xs whitespace-nowrap">
                        {h}
                      </TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {csvPreviewRows.map((row, i) => (
                    <TableRow key={i}>
                      {row.map((cell, j) => (
                        <TableCell key={j} className="text-xs whitespace-nowrap">
                          {cell || <span className="text-muted-foreground">—</span>}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            {error && (
              <div className="flex items-center gap-2 text-sm text-destructive">
                <AlertCircle className="h-4 w-4" />
                {error}
              </div>
            )}

            <DialogFooter>
              <Button variant="outline" onClick={handleBack}>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back
              </Button>
              <Button onClick={handleNext} disabled={isImporting}>
                {isImporting ? (
                  <>Importing...</>
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" />
                    Import
                  </>
                )}
              </Button>
            </DialogFooter>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
