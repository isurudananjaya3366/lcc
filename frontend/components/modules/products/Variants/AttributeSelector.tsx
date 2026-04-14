'use client';

import { useState, useCallback, KeyboardEvent } from 'react';
import { Plus, X, GripVertical } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export interface Attribute {
  id: string;
  name: string;
  type: string;
  values: string[];
}

export interface SelectedAttribute {
  id: string;
  name: string;
  values: string[];
}

interface AttributeSelectorProps {
  availableAttributes: Attribute[];
  selectedAttributes: SelectedAttribute[];
  onAttributeChange: (attrs: SelectedAttribute[]) => void;
  maxAttributes?: number;
}

const PREDEFINED_VALUES: Record<string, string[]> = {
  Size: ['XS', 'S', 'M', 'L', 'XL', 'XXL', '3XL', 'One Size'],
  Color: ['Red', 'Blue', 'Green', 'Black', 'White', 'Navy', 'Gray', 'Yellow', 'Pink', 'Purple'],
  Material: ['Cotton', 'Polyester', 'Silk', 'Linen', 'Wool', 'Denim', 'Leather'],
  Style: ['Regular', 'Slim', 'Relaxed', 'Athletic', 'Classic'],
};

const ATTRIBUTE_TYPES = Object.keys(PREDEFINED_VALUES);

export function AttributeSelector({
  selectedAttributes,
  onAttributeChange,
  maxAttributes = 3,
}: AttributeSelectorProps) {
  const [newValue, setNewValue] = useState<Record<string, string>>({});

  const addAttribute = (type: string) => {
    if (selectedAttributes.length >= maxAttributes) return;
    if (selectedAttributes.some((a) => a.name === type)) return;

    onAttributeChange([...selectedAttributes, { id: crypto.randomUUID(), name: type, values: [] }]);
  };

  const removeAttribute = (id: string) => {
    onAttributeChange(selectedAttributes.filter((a) => a.id !== id));
  };

  const addValue = useCallback(
    (attrId: string) => {
      const value = (newValue[attrId] || '').trim();
      if (!value) return;

      const attr = selectedAttributes.find((a) => a.id === attrId);
      if (!attr) return;
      if (attr.values.some((v) => v.toLowerCase() === value.toLowerCase())) return;

      onAttributeChange(
        selectedAttributes.map((a) =>
          a.id === attrId ? { ...a, values: [...a.values, value] } : a
        )
      );
      setNewValue((prev) => ({ ...prev, [attrId]: '' }));
    },
    [selectedAttributes, newValue, onAttributeChange]
  );

  const removeValue = (attrId: string, valueToRemove: string) => {
    onAttributeChange(
      selectedAttributes.map((a) =>
        a.id === attrId ? { ...a, values: a.values.filter((v) => v !== valueToRemove) } : a
      )
    );
  };

  const addPredefinedValue = (attrId: string, value: string) => {
    const attr = selectedAttributes.find((a) => a.id === attrId);
    if (!attr || attr.values.includes(value)) return;
    onAttributeChange(
      selectedAttributes.map((a) => (a.id === attrId ? { ...a, values: [...a.values, value] } : a))
    );
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>, attrId: string) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addValue(attrId);
    }
  };

  const combinationCount = selectedAttributes.reduce(
    (total, attr) => total * Math.max(attr.values.length, 1),
    selectedAttributes.length > 0 ? 1 : 0
  );

  const usedTypes = selectedAttributes.map((a) => a.name);
  const availableTypes = ATTRIBUTE_TYPES.filter((t) => !usedTypes.includes(t));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Variant Attributes</span>
          {selectedAttributes.length > 0 && combinationCount > 0 && (
            <Badge variant="secondary">
              {selectedAttributes
                .filter((a) => a.values.length > 0)
                .map(
                  (a) =>
                    `${a.values.length} ${a.name.toLowerCase()}${a.values.length > 1 ? 's' : ''}`
                )
                .join(' × ')}{' '}
              = {combinationCount} variant{combinationCount !== 1 ? 's' : ''}
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Attribute selector */}
        {selectedAttributes.length < maxAttributes && availableTypes.length > 0 && (
          <div className="flex items-center gap-2">
            <Select onValueChange={addAttribute}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Add attribute..." />
              </SelectTrigger>
              <SelectContent>
                {availableTypes.map((type) => (
                  <SelectItem key={type} value={type}>
                    {type}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {selectedAttributes.length}/{maxAttributes} attributes
            </span>
          </div>
        )}

        {/* Selected attributes */}
        {selectedAttributes.map((attr) => (
          <div key={attr.id} className="rounded-lg border p-4 dark:border-gray-700">
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <GripVertical className="h-4 w-4 text-gray-400 cursor-grab" />
                <Label className="font-medium">{attr.name}</Label>
                <Badge variant="outline" className="text-xs">
                  {attr.values.length} value{attr.values.length !== 1 ? 's' : ''}
                </Badge>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 text-gray-400 hover:text-red-600"
                onClick={() => removeAttribute(attr.id)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Value input */}
            <div className="flex items-center gap-2 mb-2">
              <Input
                placeholder={`Add ${attr.name.toLowerCase()} value...`}
                value={newValue[attr.id] || ''}
                onChange={(e) => setNewValue((prev) => ({ ...prev, [attr.id]: e.target.value }))}
                onKeyDown={(e) => handleKeyDown(e, attr.id)}
                className="h-8"
              />
              <Button size="sm" variant="outline" className="h-8" onClick={() => addValue(attr.id)}>
                <Plus className="h-3.5 w-3.5" />
              </Button>
            </div>

            {/* Predefined suggestions */}
            {PREDEFINED_VALUES[attr.name] && (
              <div className="mb-2">
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Quick add:</p>
                <div className="flex flex-wrap gap-1">
                  {PREDEFINED_VALUES[attr.name]
                    .filter((v) => !attr.values.includes(v))
                    .map((value) => (
                      <button
                        key={value}
                        type="button"
                        className="rounded border px-2 py-0.5 text-xs text-gray-600 hover:bg-gray-100 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-800"
                        onClick={() => addPredefinedValue(attr.id, value)}
                      >
                        + {value}
                      </button>
                    ))}
                </div>
              </div>
            )}

            {/* Selected values */}
            <div className="flex flex-wrap gap-1.5">
              {attr.values.map((value) => (
                <Badge key={value} variant="secondary" className="gap-1">
                  {value}
                  <button
                    type="button"
                    className="ml-0.5 hover:text-red-600"
                    onClick={() => removeValue(attr.id, value)}
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>

            {attr.values.length < 2 && (
              <p className="mt-2 text-xs text-amber-600 dark:text-amber-400">
                Each attribute needs at least 2 values
              </p>
            )}
          </div>
        ))}

        {selectedAttributes.length === 0 && (
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
            Select at least one attribute to create variants.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
