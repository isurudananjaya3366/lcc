'use client';

import { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { UseFormRegister, FieldErrors } from 'react-hook-form';
import type { QuoteFormValues } from '@/lib/validations/quote';

interface QuoteValiditySectionProps {
  register: UseFormRegister<QuoteFormValues>;
  errors: FieldErrors<QuoteFormValues>;
  expiryDate: string;
  onExpiryChange: (value: string) => void;
}

/**
 * Quote validity section with expiry date, validity days auto-calculation,
 * and terms/notes fields.
 * Task 75: Validity Section
 */
export function QuoteValiditySection({
  register,
  errors,
  expiryDate,
  onExpiryChange,
}: QuoteValiditySectionProps) {
  const [validityDays, setValidityDays] = useState<number>(30);

  // Sync validity days from expiry date
  useEffect(() => {
    if (expiryDate) {
      const expiry = new Date(expiryDate);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const diffMs = expiry.getTime() - today.getTime();
      const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
      if (diffDays >= 0) {
        setValidityDays(diffDays);
      }
    }
  }, [expiryDate]);

  // Update expiry date from validity days
  const handleDaysChange = (days: number) => {
    setValidityDays(days);
    if (days >= 0) {
      const newDate = new Date();
      newDate.setDate(newDate.getDate() + days);
      onExpiryChange(newDate.toISOString().split('T')[0]);
    }
  };

  // Minimum date is today
  const today = new Date().toISOString().split('T')[0];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Validity &amp; Terms</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <Label htmlFor="expiryDate">Valid Until *</Label>
            <Input
              id="expiryDate"
              type="date"
              min={today}
              value={expiryDate}
              onChange={(e) => onExpiryChange(e.target.value)}
            />
            {errors.expiryDate && (
              <p className="mt-1 text-xs text-red-500">{errors.expiryDate.message}</p>
            )}
          </div>
          <div>
            <Label htmlFor="validityDays">Validity (Days)</Label>
            <Input
              id="validityDays"
              type="number"
              min={0}
              max={365}
              value={validityDays}
              onChange={(e) => handleDaysChange(parseInt(e.target.value) || 0)}
            />
            <p className="mt-1 text-xs text-gray-500">Auto-calculated from expiry date</p>
          </div>
        </div>

        <div>
          <Label htmlFor="terms">Terms &amp; Conditions</Label>
          <Textarea
            id="terms"
            placeholder="Enter quote terms and conditions..."
            rows={3}
            maxLength={2000}
            {...register('terms')}
          />
          {errors.terms && <p className="mt-1 text-xs text-red-500">{errors.terms.message}</p>}
        </div>

        <div>
          <Label htmlFor="notes">Notes</Label>
          <Textarea
            id="notes"
            placeholder="Add internal notes..."
            rows={2}
            maxLength={1000}
            {...register('notes')}
          />
        </div>
      </CardContent>
    </Card>
  );
}
