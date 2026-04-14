'use client';

import { useMemo } from 'react';
import { AlertCircle, AlertTriangle } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import type { ParsedData } from './ImportFileUpload';

export interface ProductField {
  key: string;
  label: string;
  type: 'string' | 'number' | 'enum';
  required: boolean;
  enumValues?: string[];
}

export const PRODUCT_FIELDS: ProductField[] = [
  { key: 'name', label: 'Product Name', type: 'string', required: true },
  { key: 'sku', label: 'SKU', type: 'string', required: true },
  { key: 'description', label: 'Description', type: 'string', required: false },
  { key: 'cost_price', label: 'Cost Price', type: 'number', required: false },
  { key: 'selling_price', label: 'Selling Price', type: 'number', required: true },
  { key: 'stock_quantity', label: 'Stock Quantity', type: 'number', required: false },
  {
    key: 'status',
    label: 'Status',
    type: 'enum',
    required: false,
    enumValues: ['active', 'inactive'],
  },
  { key: 'category_name', label: 'Category', type: 'string', required: false },
  { key: 'tags', label: 'Tags', type: 'string', required: false },
];

export type ColumnMappings = Record<number, string>;

export interface ValidationError {
  row: number;
  column: string;
  field: string;
  message: string;
  level: 'error' | 'warning';
}

// Auto-mapping rules: file header → product field key
const AUTO_MAP_RULES: Record<string, string[]> = {
  name: ['name', 'product', 'product_name', 'product name', 'title'],
  sku: ['sku', 'code', 'product_code', 'product code', 'item code'],
  description: ['description', 'desc', 'details'],
  cost_price: ['cost', 'cost_price', 'cost price', 'purchase price'],
  selling_price: [
    'price',
    'selling_price',
    'selling price',
    'sale_price',
    'sale price',
    'retail price',
  ],
  stock_quantity: ['stock', 'quantity', 'qty', 'stock_qty', 'stock quantity', 'inventory'],
  status: ['status', 'state'],
  category_name: ['category', 'category_name', 'category name', 'group'],
  tags: ['tags', 'labels'],
};

export function autoMapColumns(headers: string[]): ColumnMappings {
  const mappings: ColumnMappings = {};
  const usedFields = new Set<string>();

  for (let i = 0; i < headers.length; i++) {
    const header = headers[i].toLowerCase().trim();
    for (const [field, aliases] of Object.entries(AUTO_MAP_RULES)) {
      if (!usedFields.has(field) && aliases.includes(header)) {
        mappings[i] = field;
        usedFields.add(field);
        break;
      }
    }
  }

  return mappings;
}

export function validateImportData(data: ParsedData, mappings: ColumnMappings): ValidationError[] {
  const errors: ValidationError[] = [];
  const seenSkus = new Set<string>();
  const skuColIndex = Object.entries(mappings).find(([, v]) => v === 'sku')?.[0];

  for (let rowIdx = 0; rowIdx < data.rows.length; rowIdx++) {
    const row = data.rows[rowIdx];

    for (const [colIdxStr, fieldKey] of Object.entries(mappings)) {
      const colIdx = Number(colIdxStr);
      const field = PRODUCT_FIELDS.find((f) => f.key === fieldKey);
      if (!field) continue;

      const value = row[colIdx]?.trim() ?? '';

      // Required check
      if (field.required && !value) {
        errors.push({
          row: rowIdx,
          column: data.headers[colIdx],
          field: fieldKey,
          message: `${field.label} is required`,
          level: 'error',
        });
        continue;
      }

      if (!value) continue;

      // Number validation
      if (field.type === 'number') {
        const num = Number(value);
        if (isNaN(num)) {
          errors.push({
            row: rowIdx,
            column: data.headers[colIdx],
            field: fieldKey,
            message: `${field.label} must be a number`,
            level: 'error',
          });
        } else if (fieldKey.includes('price') && num < 0) {
          errors.push({
            row: rowIdx,
            column: data.headers[colIdx],
            field: fieldKey,
            message: `${field.label} must be positive`,
            level: 'error',
          });
        } else if (fieldKey === 'stock_quantity' && !Number.isInteger(num)) {
          errors.push({
            row: rowIdx,
            column: data.headers[colIdx],
            field: fieldKey,
            message: 'Stock must be a whole number',
            level: 'error',
          });
        }
      }

      // Enum validation
      if (
        field.type === 'enum' &&
        field.enumValues &&
        !field.enumValues.includes(value.toLowerCase())
      ) {
        errors.push({
          row: rowIdx,
          column: data.headers[colIdx],
          field: fieldKey,
          message: `Invalid value. Expected: ${field.enumValues.join(', ')}`,
          level: 'error',
        });
      }

      // Unique SKU check
      if (fieldKey === 'sku') {
        if (seenSkus.has(value)) {
          errors.push({
            row: rowIdx,
            column: data.headers[colIdx],
            field: 'sku',
            message: 'Duplicate SKU',
            level: 'error',
          });
        } else {
          seenSkus.add(value);
        }
      }
    }

    // Price comparison warning
    const costIdx = Object.entries(mappings).find(([, v]) => v === 'cost_price')?.[0];
    const priceIdx = Object.entries(mappings).find(([, v]) => v === 'selling_price')?.[0];
    if (costIdx !== undefined && priceIdx !== undefined) {
      const cost = Number(row[Number(costIdx)]);
      const price = Number(row[Number(priceIdx)]);
      if (!isNaN(cost) && !isNaN(price) && price < cost) {
        errors.push({
          row: rowIdx,
          column: data.headers[Number(priceIdx)],
          field: 'selling_price',
          message: 'Selling price is below cost',
          level: 'warning',
        });
      }
    }
  }

  return errors;
}

interface ImportPreviewProps {
  data: ParsedData;
  mappings: ColumnMappings;
  onMappingsChange: (mappings: ColumnMappings) => void;
  validationErrors: ValidationError[];
  showMappingRow?: boolean;
}

export function ImportPreview({
  data,
  mappings,
  onMappingsChange,
  validationErrors,
  showMappingRow = true,
}: ImportPreviewProps) {
  const previewRows = data.rows.slice(0, 10);
  const errorCount = validationErrors.filter((e) => e.level === 'error').length;
  const warningCount = validationErrors.filter((e) => e.level === 'warning').length;

  const errorMap = useMemo(() => {
    const map = new Map<string, ValidationError[]>();
    for (const err of validationErrors) {
      if (err.row >= 10) continue; // Only show for preview rows
      const key = `${err.row}-${err.column}`;
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(err);
    }
    return map;
  }, [validationErrors]);

  const handleMappingChange = (colIdx: number, fieldKey: string) => {
    const newMappings = { ...mappings };
    if (fieldKey === 'skip') {
      delete newMappings[colIdx];
    } else {
      newMappings[colIdx] = fieldKey;
    }
    onMappingsChange(newMappings);
  };

  const usedFields = new Set(Object.values(mappings));
  const requiredMissing = PRODUCT_FIELDS.filter((f) => f.required && !usedFields.has(f.key));

  return (
    <div className="space-y-4">
      {/* Validation Summary */}
      {(errorCount > 0 || warningCount > 0 || requiredMissing.length > 0) && (
        <div className="flex flex-wrap gap-2">
          {requiredMissing.length > 0 && (
            <Badge variant="destructive" className="gap-1">
              <AlertCircle className="h-3 w-3" />
              {requiredMissing.length} required field{requiredMissing.length > 1 ? 's' : ''} not
              mapped: {requiredMissing.map((f) => f.label).join(', ')}
            </Badge>
          )}
          {errorCount > 0 && (
            <Badge variant="destructive" className="gap-1">
              <AlertCircle className="h-3 w-3" />
              {errorCount} error{errorCount > 1 ? 's' : ''}
            </Badge>
          )}
          {warningCount > 0 && (
            <Badge
              variant="secondary"
              className="gap-1 bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400"
            >
              <AlertTriangle className="h-3 w-3" />
              {warningCount} warning{warningCount > 1 ? 's' : ''}
            </Badge>
          )}
        </div>
      )}

      <div className="overflow-x-auto rounded-lg border">
        <table className="w-full text-sm">
          <thead>
            {showMappingRow && (
              <tr className="bg-muted/50">
                <th className="px-3 py-2 text-left text-xs font-medium text-muted-foreground w-10">
                  Map
                </th>
                {data.headers.map((_, colIdx) => (
                  <th key={colIdx} className="px-2 py-2 min-w-[140px]">
                    <Select
                      value={mappings[colIdx] || 'skip'}
                      onValueChange={(v) => handleMappingChange(colIdx, v)}
                    >
                      <SelectTrigger className="h-8 text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="skip">— Skip —</SelectItem>
                        {PRODUCT_FIELDS.map((field) => (
                          <SelectItem
                            key={field.key}
                            value={field.key}
                            disabled={usedFields.has(field.key) && mappings[colIdx] !== field.key}
                          >
                            {field.label}
                            {field.required ? ' *' : ''}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </th>
                ))}
              </tr>
            )}
            <tr className="border-b bg-muted/30">
              <th className="px-3 py-2 text-left text-xs font-medium text-muted-foreground w-10">
                #
              </th>
              {data.headers.map((header, i) => (
                <th key={i} className="px-3 py-2 text-left text-xs font-medium">
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {previewRows.map((row, rowIdx) => (
              <tr key={rowIdx} className="border-b last:border-b-0">
                <td className="px-3 py-2 text-xs text-muted-foreground">{rowIdx + 1}</td>
                {row.map((cell, colIdx) => {
                  const cellErrors = errorMap.get(`${rowIdx}-${data.headers[colIdx]}`);
                  const hasError = cellErrors?.some((e) => e.level === 'error');
                  const hasWarning = cellErrors?.some((e) => e.level === 'warning');

                  return (
                    <td
                      key={colIdx}
                      className={`px-3 py-2 text-xs ${
                        hasError
                          ? 'bg-red-50 dark:bg-red-950/20'
                          : hasWarning
                            ? 'bg-amber-50 dark:bg-amber-950/20'
                            : ''
                      }`}
                    >
                      <TooltipProvider>
                        <div className="flex items-center gap-1">
                          <span className="truncate max-w-[160px]">{cell || '—'}</span>
                          {cellErrors && cellErrors.length > 0 && (
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <span>
                                  {hasError ? (
                                    <AlertCircle className="h-3.5 w-3.5 text-red-500 shrink-0" />
                                  ) : (
                                    <AlertTriangle className="h-3.5 w-3.5 text-amber-500 shrink-0" />
                                  )}
                                </span>
                              </TooltipTrigger>
                              <TooltipContent>
                                {cellErrors.map((e, i) => (
                                  <div key={i}>{e.message}</div>
                                ))}
                              </TooltipContent>
                            </Tooltip>
                          )}
                        </div>
                      </TooltipProvider>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {data.totalRows > 10 && (
        <p className="text-xs text-muted-foreground text-center">
          Showing 10 of {data.totalRows.toLocaleString()} rows
        </p>
      )}
    </div>
  );
}
