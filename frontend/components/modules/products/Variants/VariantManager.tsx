'use client';

import { useState } from 'react';
import type { Product, ProductVariant } from '@/types/product';
import { AttributeSelector } from './AttributeSelector';
import type { SelectedAttribute } from './AttributeSelector';
import { VariantMatrix } from './VariantMatrix';
import { VariantTable } from './VariantTable';
import { VariantBulkEdit } from './VariantBulkEdit';
import { DeleteVariantDialog } from './DeleteVariantDialog';

interface VariantManagerProps {
  product: Product;
  variants: ProductVariant[];
}

export function VariantManager({ product, variants: initialVariants }: VariantManagerProps) {
  const [mode, setMode] = useState<'view' | 'create'>('view');
  const [variants, setVariants] = useState<ProductVariant[]>(initialVariants);
  const [selectedAttributes, setSelectedAttributes] = useState<SelectedAttribute[]>([]);
  const [bulkEditVariants, setBulkEditVariants] = useState<ProductVariant[] | null>(null);
  const [deleteVariant, setDeleteVariant] = useState<ProductVariant | null>(null);
  const [deleteIds, setDeleteIds] = useState<string[]>([]);

  const handleSaveVariants = async (
    generated: Array<{
      tempId: string;
      name: string;
      sku: string;
      price: number;
      stock: number;
      enabled: boolean;
      attributes: Record<string, string>;
    }>
  ) => {
    // TODO: API call to save variants
    const newVariants: ProductVariant[] = generated.map((g) => ({
      id: g.tempId,
      productId: product.id,
      sku: g.sku,
      variantName: g.name,
      attributeValues: g.attributes,
      price: g.price,
      cost: product.pricing.cost,
      stockQuantity: g.stock,
      isActive: true,
    }));
    setVariants((prev) => [...prev, ...newVariants]);
    setMode('view');
    setSelectedAttributes([]);
  };

  const handleDeleteConfirm = async (ids: string[]) => {
    // TODO: API call to delete variants
    setVariants((prev) => prev.filter((v) => !ids.includes(v.id)));
    setDeleteVariant(null);
    setDeleteIds([]);
  };

  const handleBulkAction = (action: string, ids: string[]) => {
    if (action === 'delete') {
      setDeleteIds(ids);
    }
  };

  return (
    <div className="space-y-6">
      {mode === 'create' ? (
        <>
          <AttributeSelector
            availableAttributes={[]}
            selectedAttributes={selectedAttributes}
            onAttributeChange={setSelectedAttributes}
          />
          {selectedAttributes.some((a) => a.values.length >= 2) && (
            <VariantMatrix
              productId={product.id}
              baseProduct={product}
              selectedAttributes={selectedAttributes.filter((a) => a.values.length >= 2)}
              onSave={handleSaveVariants}
              onCancel={() => {
                setMode('view');
                setSelectedAttributes([]);
              }}
            />
          )}
        </>
      ) : (
        <VariantTable
          productId={product.id}
          variants={variants}
          onEdit={() => {
            // TODO: Open inline editor
          }}
          onDelete={(id) => {
            const v = variants.find((var_) => var_.id === id);
            if (v) setDeleteVariant(v);
          }}
          onBulkAction={handleBulkAction}
        />
      )}

      {/* Bulk Edit Modal */}
      {bulkEditVariants && (
        <VariantBulkEdit
          selectedVariants={bulkEditVariants}
          onClose={() => setBulkEditVariants(null)}
          onApply={async () => {
            // TODO: API call for bulk update
            setBulkEditVariants(null);
          }}
        />
      )}

      {/* Delete Dialog */}
      <DeleteVariantDialog
        variant={deleteVariant}
        variantIds={deleteIds}
        isOpen={!!deleteVariant || deleteIds.length > 0}
        onClose={() => {
          setDeleteVariant(null);
          setDeleteIds([]);
        }}
        onConfirm={handleDeleteConfirm}
      />
    </div>
  );
}
