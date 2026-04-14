'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';

const noteSchema = z.object({
  type: z.enum(['internal', 'customer']),
  content: z.string().min(1, 'Note is required').max(1000, 'Max 1000 characters'),
});

type NoteFormData = z.infer<typeof noteSchema>;

interface AddNoteFormProps {
  orderId: string;
  onSubmit: (data: NoteFormData) => Promise<void>;
  isSubmitting?: boolean;
}

export function AddNoteForm({
  orderId,
  onSubmit,
  isSubmitting: externalSubmitting,
}: AddNoteFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    reset,
    setValue,
    formState: { errors },
  } = useForm<NoteFormData>({
    resolver: zodResolver(noteSchema),
    defaultValues: { type: 'internal', content: '' },
  });

  const content = watch('content');
  const noteType = watch('type');
  const charCount = content?.length || 0;
  const submitting = externalSubmitting || isSubmitting;

  const handleFormSubmit = async (data: NoteFormData) => {
    setIsSubmitting(true);
    try {
      await onSubmit(data);
      reset();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-3 border-t pt-3">
      {/* Type selector */}
      <div className="flex gap-3">
        <label className="flex items-center gap-1.5 text-sm">
          <input
            type="radio"
            value="internal"
            checked={noteType === 'internal'}
            onChange={() => setValue('type', 'internal')}
            className="h-4 w-4"
          />
          <span>Internal</span>
          <span className="text-xs text-gray-400">(Private)</span>
        </label>
        <label className="flex items-center gap-1.5 text-sm">
          <input
            type="radio"
            value="customer"
            checked={noteType === 'customer'}
            onChange={() => setValue('type', 'customer')}
            className="h-4 w-4"
          />
          <span>Customer</span>
          <span className="text-xs text-gray-400">(Visible)</span>
        </label>
      </div>

      {/* Content */}
      <Textarea
        placeholder="Add a note..."
        rows={3}
        {...register('content')}
        onKeyDown={(e) => {
          if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
            handleSubmit(handleFormSubmit)();
          }
        }}
      />
      {errors.content && <p className="text-xs text-red-500">{errors.content.message}</p>}

      {/* Footer */}
      <div className="flex items-center justify-between">
        <span
          className={`text-xs ${
            charCount > 950 ? 'text-red-500' : charCount > 900 ? 'text-orange-500' : 'text-gray-400'
          }`}
        >
          {charCount} / 1000
        </span>
        <Button type="submit" size="sm" disabled={submitting}>
          {submitting ? 'Adding...' : 'Add Note'}
        </Button>
      </div>
    </form>
  );
}
