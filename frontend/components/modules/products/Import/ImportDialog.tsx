'use client';

import { useState, useEffect } from 'react';
import { Check, Loader2, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { ImportFileUpload, type ParsedData } from './ImportFileUpload';
import {
  ImportPreview,
  autoMapColumns,
  validateImportData,
  type ColumnMappings,
  type ValidationError,
  PRODUCT_FIELDS,
} from './ImportPreview';
import { Badge } from '@/components/ui/badge';

type ImportStep = 'upload' | 'map' | 'preview' | 'confirm';

const STEPS: { key: ImportStep; label: string }[] = [
  { key: 'upload', label: 'Upload' },
  { key: 'map', label: 'Map Columns' },
  { key: 'preview', label: 'Preview' },
  { key: 'confirm', label: 'Confirm' },
];

export interface ImportResult {
  total: number;
  success: number;
  failed: number;
  errors: Array<{ row: number; message: string }>;
}

interface ImportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onImportComplete: (result: ImportResult) => void;
}

export function ImportDialog({ open, onOpenChange, onImportComplete }: ImportDialogProps) {
  const [currentStep, setCurrentStep] = useState<ImportStep>('upload');
  const [file, setFile] = useState<File | null>(null);
  const [parsedData, setParsedData] = useState<ParsedData | null>(null);
  const [mappings, setMappings] = useState<ColumnMappings>({});
  const [validationErrors, setValidationErrors] = useState<ValidationError[]>([]);
  const [isImporting, setIsImporting] = useState(false);
  const [importResult, setImportResult] = useState<ImportResult | null>(null);

  // Reset state when dialog closes
  useEffect(() => {
    if (!open) {
      setCurrentStep('upload');
      setFile(null);
      setParsedData(null);
      setMappings({});
      setValidationErrors([]);
      setIsImporting(false);
      setImportResult(null);
    }
  }, [open]);

  const stepIndex = STEPS.findIndex((s) => s.key === currentStep);

  const handleFileSelect = (selectedFile: File, data: ParsedData) => {
    setFile(selectedFile);
    setParsedData(data);
    const autoMappings = autoMapColumns(data.headers);
    setMappings(autoMappings);
  };

  const handleNext = () => {
    if (currentStep === 'upload' && parsedData) {
      setCurrentStep('map');
    } else if (currentStep === 'map') {
      // Validate data before preview
      if (parsedData) {
        const errors = validateImportData(parsedData, mappings);
        setValidationErrors(errors);
      }
      setCurrentStep('preview');
    } else if (currentStep === 'preview') {
      setCurrentStep('confirm');
    }
  };

  const handleBack = () => {
    if (currentStep === 'map') setCurrentStep('upload');
    else if (currentStep === 'preview') setCurrentStep('map');
    else if (currentStep === 'confirm') setCurrentStep('preview');
  };

  const handleImport = async () => {
    if (!parsedData) return;
    setIsImporting(true);

    try {
      // TODO: Replace with actual API call
      // Split into batches and process
      const totalRows = parsedData.totalRows;
      const errorRows = validationErrors.filter((e) => e.level === 'error');
      const validCount = totalRows - new Set(errorRows.map((e) => e.row)).size;

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 100));

      const result: ImportResult = {
        total: totalRows,
        success: validCount,
        failed: totalRows - validCount,
        errors: errorRows.map((e) => ({ row: e.row + 1, message: e.message })),
      };

      setImportResult(result);
      onImportComplete(result);
    } catch {
      // Error handled by result display
    } finally {
      setIsImporting(false);
    }
  };

  const requiredMapped = PRODUCT_FIELDS.filter((f) => f.required).every((f) =>
    Object.values(mappings).includes(f.key)
  );
  const criticalErrors = validationErrors.filter((e) => e.level === 'error').length;

  const canProceed = () => {
    switch (currentStep) {
      case 'upload':
        return !!parsedData;
      case 'map':
        return requiredMapped;
      case 'preview':
        return true;
      case 'confirm':
        return criticalErrors === 0;
      default:
        return false;
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Import Products</DialogTitle>
        </DialogHeader>

        {/* Step Indicator */}
        <div className="flex items-center justify-between px-4 py-3">
          {STEPS.map((step, idx) => {
            const isCompleted = idx < stepIndex;
            const isCurrent = step.key === currentStep;
            return (
              <div key={step.key} className="flex items-center gap-2">
                <div
                  className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-medium transition-colors ${
                    isCompleted
                      ? 'bg-primary text-primary-foreground'
                      : isCurrent
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted text-muted-foreground'
                  }`}
                >
                  {isCompleted ? <Check className="h-4 w-4" /> : idx + 1}
                </div>
                <span
                  className={`text-sm hidden sm:inline ${isCurrent ? 'font-medium' : 'text-muted-foreground'}`}
                >
                  {step.label}
                </span>
                {idx < STEPS.length - 1 && (
                  <div className={`h-px w-8 ${isCompleted ? 'bg-primary' : 'bg-border'}`} />
                )}
              </div>
            );
          })}
        </div>

        {/* Step Content */}
        <div className="min-h-[300px] py-4">
          {currentStep === 'upload' && <ImportFileUpload onFileSelect={handleFileSelect} />}

          {currentStep === 'map' && parsedData && (
            <ImportPreview
              data={parsedData}
              mappings={mappings}
              onMappingsChange={setMappings}
              validationErrors={[]}
              showMappingRow
            />
          )}

          {currentStep === 'preview' && parsedData && (
            <ImportPreview
              data={parsedData}
              mappings={mappings}
              onMappingsChange={setMappings}
              validationErrors={validationErrors}
              showMappingRow={false}
            />
          )}

          {currentStep === 'confirm' && parsedData && (
            <div className="space-y-4">
              {importResult ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30">
                      <Check className="h-5 w-5 text-green-600" />
                    </div>
                    <div>
                      <p className="font-medium">Import Complete</p>
                      <p className="text-sm text-muted-foreground">
                        {importResult.success} of {importResult.total} products imported
                        successfully
                      </p>
                    </div>
                  </div>

                  {importResult.failed > 0 && (
                    <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-950/20">
                      <p className="text-sm font-medium text-red-800 dark:text-red-400">
                        {importResult.failed} products failed to import
                      </p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <FileText className="h-8 w-8 text-muted-foreground" />
                    <div>
                      <p className="font-medium">{parsedData.fileName}</p>
                      <p className="text-sm text-muted-foreground">
                        {parsedData.totalRows.toLocaleString()} products to import
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Badge variant="secondary">{Object.keys(mappings).length} columns mapped</Badge>
                    {criticalErrors > 0 ? (
                      <Badge variant="destructive">
                        {criticalErrors} errors — fix before importing
                      </Badge>
                    ) : (
                      <Badge className="bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                        Ready to import
                      </Badge>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        <DialogFooter className="gap-2 sm:gap-0">
          <Button variant="ghost" onClick={() => onOpenChange(false)} disabled={isImporting}>
            {importResult ? 'Close' : 'Cancel'}
          </Button>

          {!importResult && (
            <>
              {currentStep !== 'upload' && (
                <Button variant="outline" onClick={handleBack} disabled={isImporting}>
                  Back
                </Button>
              )}

              {currentStep === 'confirm' ? (
                <Button onClick={handleImport} disabled={!canProceed() || isImporting}>
                  {isImporting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Importing...
                    </>
                  ) : (
                    'Import Products'
                  )}
                </Button>
              ) : (
                <Button onClick={handleNext} disabled={!canProceed()}>
                  Next
                </Button>
              )}
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
