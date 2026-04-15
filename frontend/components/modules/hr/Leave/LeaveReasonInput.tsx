'use client';

import { useState } from 'react';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { Upload, X } from 'lucide-react';

interface LeaveReasonInputProps {
  reason: string;
  onReasonChange: (val: string) => void;
  handoverNotes?: string;
  onHandoverNotesChange?: (val: string) => void;
  emergencyContact?: string;
  onEmergencyContactChange?: (val: string) => void;
  isConfidential?: boolean;
  onIsConfidentialChange?: (val: boolean) => void;
  attachments?: File[];
  onAttachmentsChange?: (files: File[]) => void;
  showExtendedFields?: boolean;
  error?: string;
}

const commonReasons = [
  'Personal reasons',
  'Family commitment',
  'Medical appointment',
  'Travel',
  'Religious observance',
];

export function LeaveReasonInput({
  reason,
  onReasonChange,
  handoverNotes,
  onHandoverNotesChange,
  emergencyContact,
  onEmergencyContactChange,
  isConfidential,
  onIsConfidentialChange,
  attachments = [],
  onAttachmentsChange,
  showExtendedFields = false,
  error,
}: LeaveReasonInputProps) {
  const [showTemplates, setShowTemplates] = useState(false);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || !onAttachmentsChange) return;
    const validFiles = Array.from(files).filter((f) => {
      const ext = f.name.split('.').pop()?.toLowerCase();
      return ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'].includes(ext ?? '');
    });
    onAttachmentsChange([...attachments, ...validFiles]);
    e.target.value = '';
  };

  const removeFile = (idx: number) => {
    onAttachmentsChange?.(attachments.filter((_, i) => i !== idx));
  };

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label htmlFor="reason">
            Reason{' '}
            <span className="text-xs text-muted-foreground">(optional, 10-500 characters)</span>
          </Label>
          <Button
            type="button"
            variant="link"
            size="sm"
            className="text-xs"
            onClick={() => setShowTemplates(!showTemplates)}
          >
            {showTemplates ? 'Hide templates' : 'Use template'}
          </Button>
        </div>
        {showTemplates && (
          <div className="flex flex-wrap gap-1">
            {commonReasons.map((r) => (
              <Button
                key={r}
                type="button"
                variant="outline"
                size="sm"
                className="text-xs"
                onClick={() => {
                  onReasonChange(r);
                  setShowTemplates(false);
                }}
              >
                {r}
              </Button>
            ))}
          </div>
        )}
        <Textarea
          id="reason"
          value={reason}
          onChange={(e) => onReasonChange(e.target.value)}
          placeholder="Provide a reason for your leave request..."
          maxLength={500}
          rows={4}
        />
        <div className="flex justify-between">
          {error && <p className="text-xs text-destructive">{error}</p>}
          <p className="ml-auto text-xs text-muted-foreground">{reason?.length ?? 0}/500</p>
        </div>
      </div>

      {onAttachmentsChange && (
        <div className="space-y-2">
          <Label>Attachments</Label>
          <div className="flex items-center gap-2">
            <label className="flex cursor-pointer items-center gap-2 rounded-md border border-dashed px-3 py-2 text-sm text-muted-foreground hover:bg-muted/50">
              <Upload className="h-4 w-4" />
              Upload file
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                multiple
                className="hidden"
                onChange={handleFileUpload}
              />
            </label>
            <span className="text-xs text-muted-foreground">PDF, images, or documents</span>
          </div>
          {attachments.length > 0 && (
            <div className="space-y-1">
              {attachments.map((f, i) => (
                <div key={`${f.name}-${i}`} className="flex items-center gap-2 text-sm">
                  <span className="truncate">{f.name}</span>
                  <span className="text-xs text-muted-foreground">
                    ({(f.size / 1024).toFixed(0)} KB)
                  </span>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="h-5 w-5"
                    onClick={() => removeFile(i)}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {showExtendedFields && onEmergencyContactChange && (
        <div className="space-y-2">
          <Label htmlFor="emergencyContact">Emergency Contact (for extended leave)</Label>
          <Input
            id="emergencyContact"
            value={emergencyContact ?? ''}
            onChange={(e) => onEmergencyContactChange(e.target.value)}
            placeholder="Phone number reachable during leave"
          />
        </div>
      )}

      {showExtendedFields && onHandoverNotesChange && (
        <div className="space-y-2">
          <Label htmlFor="handoverNotes">Handover Notes</Label>
          <Textarea
            id="handoverNotes"
            value={handoverNotes ?? ''}
            onChange={(e) => onHandoverNotesChange(e.target.value)}
            placeholder="Notes about pending tasks and handover..."
            maxLength={1000}
            rows={3}
          />
        </div>
      )}

      {onIsConfidentialChange && (
        <div className="flex items-center gap-2">
          <Checkbox
            id="isConfidential"
            checked={isConfidential}
            onCheckedChange={(checked) => onIsConfidentialChange(!!checked)}
          />
          <Label htmlFor="isConfidential" className="text-sm font-normal">
            Mark as confidential
          </Label>
        </div>
      )}
    </div>
  );
}
