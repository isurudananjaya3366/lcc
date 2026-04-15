'use client';

import { useCallback, useRef, useState } from 'react';
import { Upload, FileText, X, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';

const ACCEPTED_TYPES = [
  'text/csv',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-excel',
];
const ACCEPTED_EXTENSIONS = '.csv,.xlsx,.xls';
const MAX_SIZE = 10 * 1024 * 1024; // 10MB

export interface ParsedData {
  headers: string[];
  rows: string[][];
  totalRows: number;
  fileName: string;
}

interface ImportFileUploadProps {
  onFileSelect: (file: File, data: ParsedData) => void;
  error?: string;
}

function parseCSV(text: string): { headers: string[]; rows: string[][] } {
  const lines = text.split(/\r?\n/).filter((line) => line.trim().length > 0);
  if (lines.length === 0) return { headers: [], rows: [] };

  const parseLine = (line: string): string[] => {
    const result: string[] = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      if (char === '"') {
        if (inQuotes && line[i + 1] === '"') {
          current += '"';
          i++;
        } else {
          inQuotes = !inQuotes;
        }
      } else if (char === ',' && !inQuotes) {
        result.push(current.trim());
        current = '';
      } else {
        current += char;
      }
    }
    result.push(current.trim());
    return result;
  };

  const headers = parseLine(lines[0] ?? '');
  const rows = lines.slice(1).map(parseLine);
  return { headers, rows };
}

export function ImportFileUpload({ onFileSelect, error }: ImportFileUploadProps) {
  const [dragOver, setDragOver] = useState(false);
  const [parsing, setParsing] = useState(false);
  const [selectedFile, setSelectedFile] = useState<{
    name: string;
    rows: number;
    columns: number;
  } | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const processFile = useCallback(
    async (file: File) => {
      setValidationError(null);

      // Validate type
      if (!ACCEPTED_TYPES.includes(file.type) && !file.name.match(/\.(csv|xlsx|xls)$/i)) {
        setValidationError('Invalid file type. Please upload CSV or Excel file.');
        return;
      }

      // Validate size
      if (file.size > MAX_SIZE) {
        setValidationError('File too large. Maximum size is 10MB.');
        return;
      }

      setParsing(true);

      try {
        if (file.name.endsWith('.csv') || file.type === 'text/csv') {
          const text = await file.text();
          const { headers, rows } = parseCSV(text);

          if (rows.length === 0) {
            setValidationError('File is empty or missing data.');
            setParsing(false);
            return;
          }

          const parsed: ParsedData = {
            headers,
            rows,
            totalRows: rows.length,
            fileName: file.name,
          };

          setSelectedFile({ name: file.name, rows: rows.length, columns: headers.length });
          onFileSelect(file, parsed);
        } else {
          // For Excel files, we'd use a library like xlsx
          // For now, show a placeholder message
          // TODO: Add xlsx library integration
          setValidationError('Excel parsing requires the xlsx library. Please use CSV for now.');
        }
      } catch {
        setValidationError('Failed to parse file. Please check the file format.');
      } finally {
        setParsing(false);
      }
    },
    [onFileSelect]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) processFile(file);
    },
    [processFile]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) processFile(file);
      if (inputRef.current) inputRef.current.value = '';
    },
    [processFile]
  );

  const handleReset = () => {
    setSelectedFile(null);
    setValidationError(null);
  };

  const displayError = validationError || error;

  if (selectedFile) {
    return (
      <div className="space-y-3">
        <div className="flex items-center gap-3 rounded-lg border p-4">
          <FileText className="h-8 w-8 text-primary shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{selectedFile.name}</p>
            <p className="text-xs text-muted-foreground">
              {selectedFile.rows.toLocaleString()} rows &bull; {selectedFile.columns} columns
            </p>
          </div>
          <Button variant="ghost" size="icon" onClick={handleReset} className="shrink-0">
            <X className="h-4 w-4" />
          </Button>
        </div>
        <Button variant="outline" size="sm" onClick={() => inputRef.current?.click()}>
          Change File
        </Button>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_EXTENSIONS}
          onChange={handleFileInput}
          className="hidden"
        />
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => !parsing && inputRef.current?.click()}
        className={`
          flex flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed p-8 cursor-pointer transition-colors
          ${dragOver ? 'border-primary bg-primary/5' : 'border-muted-foreground/25 hover:border-primary/50'}
          ${parsing ? 'opacity-50 cursor-wait' : ''}
        `}
      >
        {parsing ? (
          <>
            <Loader2 className="h-8 w-8 text-primary animate-spin" />
            <p className="text-sm text-muted-foreground">Parsing file...</p>
          </>
        ) : dragOver ? (
          <>
            <Upload className="h-8 w-8 text-primary" />
            <p className="text-sm font-medium">Drop file to upload</p>
          </>
        ) : (
          <>
            <Upload className="h-8 w-8 text-muted-foreground" />
            <div className="text-center">
              <p className="text-sm">
                Drag & drop file here or{' '}
                <span className="font-medium text-primary">click to browse</span>
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                Accepts: CSV, Excel (.xlsx) &bull; Max size: 10MB
              </p>
            </div>
          </>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_EXTENSIONS}
        onChange={handleFileInput}
        className="hidden"
      />

      {displayError && <p className="text-sm text-red-500">{displayError}</p>}
    </div>
  );
}
