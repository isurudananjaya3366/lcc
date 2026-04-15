'use client';

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';

const TIMEZONES = [
  { value: 'Asia/Colombo', label: 'Asia/Colombo (UTC+5:30)' },
  { value: 'Asia/Kolkata', label: 'Asia/Kolkata (UTC+5:30)' },
  { value: 'Asia/Dubai', label: 'Asia/Dubai (UTC+4:00)' },
  { value: 'Asia/Singapore', label: 'Asia/Singapore (UTC+8:00)' },
  { value: 'Europe/London', label: 'Europe/London (UTC+0:00)' },
  { value: 'America/New_York', label: 'America/New York (UTC-5:00)' },
  { value: 'America/Los_Angeles', label: 'America/Los Angeles (UTC-8:00)' },
  { value: 'Australia/Sydney', label: 'Australia/Sydney (UTC+11:00)' },
];

interface TimezoneSelectProps {
  value: string;
  onChange: (value: string) => void;
}

export function TimezoneSelect({ value, onChange }: TimezoneSelectProps) {
  return (
    <div className="space-y-2">
      <Label htmlFor="timezone">Timezone</Label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger id="timezone">
          <SelectValue placeholder="Select timezone" />
        </SelectTrigger>
        <SelectContent>
          {TIMEZONES.map((tz) => (
            <SelectItem key={tz.value} value={tz.value}>
              {tz.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
