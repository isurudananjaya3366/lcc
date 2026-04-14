'use client';

import { type Control } from 'react-hook-form';
import type { WarehouseFormValues } from '@/lib/validations/warehouse';
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface WarehouseAddressFormProps {
  control: Control<WarehouseFormValues>;
  isLoading?: boolean;
}

const sriLankanDistricts = [
  'Colombo',
  'Gampaha',
  'Kalutara',
  'Kandy',
  'Matale',
  'Nuwara Eliya',
  'Galle',
  'Matara',
  'Hambantota',
  'Jaffna',
  'Kilinochchi',
  'Mannar',
  'Mullaitivu',
  'Vavuniya',
  'Batticaloa',
  'Ampara',
  'Trincomalee',
  'Kurunegala',
  'Puttalam',
  'Anuradhapura',
  'Polonnaruwa',
  'Badulla',
  'Monaragala',
  'Ratnapura',
  'Kegalle',
];

export function WarehouseAddressForm({ control, isLoading }: WarehouseAddressFormProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <div className="sm:col-span-2">
        <FormField
          control={control}
          name="address.street"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Address Line 1</FormLabel>
              <FormControl>
                <Input placeholder="Street address" disabled={isLoading} {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      <div className="sm:col-span-2">
        <FormField
          control={control}
          name="address.street2"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Address Line 2 (optional)</FormLabel>
              <FormControl>
                <Input placeholder="Building, suite, unit" disabled={isLoading} {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      <FormField
        control={control}
        name="address.city"
        render={({ field }) => (
          <FormItem>
            <FormLabel>City</FormLabel>
            <FormControl>
              <Input placeholder="City" disabled={isLoading} {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={control}
        name="address.state"
        render={({ field }) => (
          <FormItem>
            <FormLabel>District</FormLabel>
            <Select onValueChange={field.onChange} value={field.value} disabled={isLoading}>
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select district" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                {sriLankanDistricts.map((district) => (
                  <SelectItem key={district} value={district}>
                    {district}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={control}
        name="address.postalCode"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Postal Code (optional)</FormLabel>
            <FormControl>
              <Input placeholder="Postal code" disabled={isLoading} {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={control}
        name="capacity"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Capacity (optional)</FormLabel>
            <FormControl>
              <Input
                type="number"
                min={0}
                placeholder="Max items"
                disabled={isLoading}
                {...field}
                value={field.value ?? ''}
                onChange={(e) =>
                  field.onChange(e.target.value ? Number(e.target.value) : undefined)
                }
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    </div>
  );
}
