'use client';

import { useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Upload, X, FileText } from 'lucide-react';

interface DocumentUploadSectionProps {
  documents: Record<string, File | null>;
  onFileChange: (field: string, file: File | null) => void;
}

const DOCUMENT_FIELDS = [
  { key: 'nicCopy', label: 'NIC Copy', required: true, accept: 'image/*,.pdf' },
  { key: 'photo', label: 'Photo', required: true, accept: 'image/*' },
  { key: 'cv', label: 'CV / Resume', required: false, accept: '.pdf,.doc,.docx' },
  { key: 'contract', label: 'Contract', required: false, accept: '.pdf' },
  { key: 'certificates', label: 'Certificates', required: false, accept: 'image/*,.pdf' },
];

function FileInput({
  field,
  file,
  accept,
  onChange,
}: {
  field: string;
  file: File | null;
  accept: string;
  onChange: (file: File | null) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);

  return (
    <div className="flex items-center gap-2">
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => onChange(e.target.files?.[0] ?? null)}
      />
      {file ? (
        <div className="flex flex-1 items-center gap-2 rounded-md border bg-muted/50 px-3 py-2">
          <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />
          <span className="flex-1 truncate text-sm">{file.name}</span>
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            onClick={() => onChange(null)}
          >
            <X className="h-3 w-3" />
          </Button>
        </div>
      ) : (
        <Button type="button" variant="outline" size="sm" onClick={() => inputRef.current?.click()}>
          <Upload className="mr-2 h-4 w-4" />
          Choose File
        </Button>
      )}
    </div>
  );
}

export function DocumentUploadSection({ documents, onFileChange }: DocumentUploadSectionProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Documents</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {DOCUMENT_FIELDS.map((doc) => (
          <div key={doc.key} className="space-y-2">
            <Label>
              {doc.label} {doc.required && '*'}
            </Label>
            <FileInput
              field={doc.key}
              file={documents[doc.key] ?? null}
              accept={doc.accept}
              onChange={(file) => onFileChange(doc.key, file)}
            />
          </div>
        ))}
        <p className="text-xs text-muted-foreground">
          Accepted formats: Images (JPG, PNG), PDF, DOC/DOCX. Max 5MB per file.
        </p>
      </CardContent>
    </Card>
  );
}
