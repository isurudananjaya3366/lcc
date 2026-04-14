'use client';

import { useState, useMemo } from 'react';
import type { Product } from '@/types/product';
import type { SelectedAttribute } from './AttributeSelector';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Loader2, Trash2, AlertTriangle } from 'lucide-react';

interface GeneratedVariant {
  tempId: string;
  name: string;
  sku: string;
  price: number;
  stock: number;
  enabled: boolean;
  attributes: Record<string, string>;
}

interface VariantMatrixProps {
  productId: string;
  baseProduct: Product;
  selectedAttributes: SelectedAttribute[];
  onSave: (variants: GeneratedVariant[]) => Promise<void>;
  onCancel: () => void;
}

function generateCartesian(attrs: SelectedAttribute[]): Record<string, string>[] {
  if (attrs.length === 0) return [];
  return attrs.reduce<Record<string, string>[]>(
    (combos, attr) => {
      if (attr.values.length === 0) return combos;
      const result: Record<string, string>[] = [];
      for (const combo of combos) {
        for (const value of attr.values) {
          result.push({ ...combo, [attr.name]: value });
        }
      }
      return result;
    },
    [{}]
  );
}

export function VariantMatrix({
  baseProduct,
  selectedAttributes,
  onSave,
  onCancel,
}: VariantMatrixProps) {
  const [saving, setSaving] = useState(false);

  const initialVariants = useMemo(() => {
    const combinations = generateCartesian(selectedAttributes);
    return combinations.map((attrs): GeneratedVariant => {
      const values = Object.values(attrs);
      const name = values.join('-');
      const sku = `${baseProduct.sku}-${values
        .map((v) => v.toUpperCase().replace(/\s+/g, '').slice(0, 3))
        .join('-')}`;
      return {
        tempId: crypto.randomUUID(),
        name,
        sku,
        price: baseProduct.pricing.basePrice,
        stock: 0,
        enabled: true,
        attributes: attrs,
      };
    });
  }, [selectedAttributes, baseProduct.sku, baseProduct.pricing.basePrice]);

  const [variants, setVariants] = useState<GeneratedVariant[]>(initialVariants);

  const updateVariant = (tempId: string, updates: Partial<GeneratedVariant>) => {
    setVariants((prev) => prev.map((v) => (v.tempId === tempId ? { ...v, ...updates } : v)));
  };

  const removeVariant = (tempId: string) => {
    setVariants((prev) => prev.filter((v) => v.tempId !== tempId));
  };

  const toggleAll = (enabled: boolean) => {
    setVariants((prev) => prev.map((v) => ({ ...v, enabled })));
  };

  const enabledVariants = variants.filter((v) => v.enabled);
  const allEnabled = variants.every((v) => v.enabled);

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(enabledVariants);
    } finally {
      setSaving(false);
    }
  };

  const hasDuplicateSkus = () => {
    const skus = enabledVariants.map((v) => v.sku);
    return new Set(skus).size !== skus.length;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>
            Variant Matrix ({enabledVariants.length} of {variants.length} enabled)
          </span>
          {variants.length > 50 && (
            <Badge variant="secondary" className="gap-1">
              <AlertTriangle className="h-3 w-3" />
              Large variant set
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Attribute breakdown */}
        <div className="flex flex-wrap gap-2">
          {selectedAttributes.map((attr) => (
            <Badge key={attr.id} variant="outline">
              {attr.name}: {attr.values.length} value{attr.values.length !== 1 ? 's' : ''}
            </Badge>
          ))}
        </div>

        {/* Matrix table */}
        <div className="overflow-x-auto rounded-md border dark:border-gray-700">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-10">
                  <Checkbox
                    checked={allEnabled}
                    onCheckedChange={(checked) => toggleAll(!!checked)}
                  />
                </TableHead>
                <TableHead>Variant</TableHead>
                <TableHead>SKU</TableHead>
                <TableHead className="w-28">Price</TableHead>
                <TableHead className="w-24">Stock</TableHead>
                <TableHead className="w-12" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {variants.map((variant) => (
                <TableRow key={variant.tempId} className={!variant.enabled ? 'opacity-50' : ''}>
                  <TableCell>
                    <Checkbox
                      checked={variant.enabled}
                      onCheckedChange={(checked) =>
                        updateVariant(variant.tempId, { enabled: !!checked })
                      }
                    />
                  </TableCell>
                  <TableCell className="font-medium">{variant.name}</TableCell>
                  <TableCell>
                    <Input
                      value={variant.sku}
                      onChange={(e) => updateVariant(variant.tempId, { sku: e.target.value })}
                      className="h-8 w-40 font-mono text-xs"
                      disabled={!variant.enabled}
                    />
                  </TableCell>
                  <TableCell>
                    <Input
                      type="number"
                      value={variant.price}
                      onChange={(e) =>
                        updateVariant(variant.tempId, {
                          price: parseFloat(e.target.value) || 0,
                        })
                      }
                      className="h-8 w-24"
                      min={0}
                      step={0.01}
                      disabled={!variant.enabled}
                    />
                  </TableCell>
                  <TableCell>
                    <Input
                      type="number"
                      value={variant.stock}
                      onChange={(e) =>
                        updateVariant(variant.tempId, {
                          stock: parseInt(e.target.value) || 0,
                        })
                      }
                      className="h-8 w-20"
                      min={0}
                      disabled={!variant.enabled}
                    />
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7 text-gray-400 hover:text-red-600"
                      onClick={() => removeVariant(variant.tempId)}
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {variants.length === 0 && (
                <TableRow>
                  <TableCell
                    colSpan={6}
                    className="text-center text-sm text-gray-500 dark:text-gray-400 py-8"
                  >
                    No variants to display. Add attribute values to generate variants.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>

        {hasDuplicateSkus() && (
          <p className="text-sm text-red-600 dark:text-red-400">
            Duplicate SKUs detected. Please ensure all SKUs are unique.
          </p>
        )}

        {/* Actions */}
        <div className="flex items-center justify-end gap-2 pt-2">
          <Button variant="outline" onClick={onCancel} disabled={saving}>
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            disabled={saving || enabledVariants.length === 0 || hasDuplicateSkus()}
          >
            {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Save {enabledVariants.length} Variant{enabledVariants.length !== 1 ? 's' : ''}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
