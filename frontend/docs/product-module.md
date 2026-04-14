# Product Management Module Documentation

## Overview

The Product Management Module provides a complete UI for managing products, categories, variants, and bulk import/export operations. Built with Next.js App Router, React Hook Form, Zod validation, and shadcn/ui components.

## Module Structure

```
frontend/
├── app/(dashboard)/products/
│   ├── layout.tsx                    # Products section layout
│   ├── page.tsx                      # Product list page
│   ├── loading.tsx                   # Loading skeleton
│   ├── error.tsx                     # Error boundary
│   ├── new/
│   │   ├── page.tsx                  # Create product page
│   │   └── CreateProductForm.tsx     # Create form client wrapper
│   ├── [id]/
│   │   ├── page.tsx                  # Product detail page
│   │   ├── ProductDetailView.tsx     # Detail client wrapper
│   │   ├── edit/
│   │   │   ├── page.tsx             # Edit product page
│   │   │   └── EditProductForm.tsx  # Edit form client wrapper
│   │   └── variants/
│   │       ├── page.tsx             # Variant management page
│   │       └── VariantManagementView.tsx
│   └── categories/
│       ├── page.tsx                  # Category list page
│       ├── CategoryListView.tsx      # Category list client wrapper
│       ├── new/
│       │   ├── page.tsx             # Create category page
│       │   └── CreateCategoryForm.tsx
│       └── [id]/
│           ├── page.tsx             # Edit category page
│           └── EditCategoryForm.tsx
│
├── components/modules/products/
│   ├── ProductList/                  # Product listing components
│   │   ├── ProductListHeader.tsx     # Header with title, add button
│   │   ├── ProductTable.tsx          # Data table with columns
│   │   ├── ProductTableColumns.tsx   # Column definitions
│   │   ├── BulkActionsBar.tsx        # Bulk action toolbar
│   │   ├── ProductFilters.tsx        # Combined filter bar
│   │   ├── cells/                    # Table cell components
│   │   │   ├── ProductNameCell.tsx
│   │   │   ├── PriceCell.tsx
│   │   │   ├── StockCell.tsx
│   │   │   ├── StatusBadgeCell.tsx
│   │   │   └── ActionsCell.tsx
│   │   ├── filters/                  # Filter components
│   │   │   ├── SearchInput.tsx
│   │   │   ├── StatusFilter.tsx
│   │   │   ├── CategoryFilter.tsx
│   │   │   └── StockFilter.tsx
│   │   └── index.ts
│   │
│   ├── ProductForm/                  # Product form components
│   │   ├── ProductForm.tsx           # Main form orchestrator
│   │   ├── BasicInfoSection.tsx
│   │   ├── DescriptionEditor.tsx
│   │   ├── PricingSection.tsx
│   │   ├── InventorySection.tsx
│   │   ├── CategorizationSection.tsx
│   │   ├── CategoryMultiSelect.tsx
│   │   ├── TagsInput.tsx
│   │   ├── MediaSection.tsx
│   │   ├── ImageUploadZone.tsx
│   │   ├── ImagePreviewGrid.tsx
│   │   └── index.ts
│   │
│   ├── ProductDetail/                # Product detail components
│   │   ├── ProductDetailHeader.tsx
│   │   ├── ProductInfoCard.tsx
│   │   ├── ProductPricingCard.tsx
│   │   ├── ProductInventoryCard.tsx
│   │   ├── ProductImageGallery.tsx
│   │   ├── ProductActivityTimeline.tsx
│   │   ├── DeleteProductDialog.tsx
│   │   └── index.ts
│   │
│   ├── Variants/                     # Variant management components
│   │   ├── AttributeSelector.tsx
│   │   ├── VariantMatrix.tsx
│   │   ├── VariantTable.tsx
│   │   ├── VariantInlineEditor.tsx
│   │   ├── VariantBulkEdit.tsx
│   │   ├── DeleteVariantDialog.tsx
│   │   ├── VariantManager.tsx
│   │   └── index.ts
│   │
│   ├── Categories/                   # Category management components
│   │   ├── CategoryTree.tsx
│   │   ├── CategoryNameInput.tsx
│   │   ├── ParentCategorySelect.tsx
│   │   ├── CategoryImageUpload.tsx
│   │   ├── CategoryForm.tsx
│   │   ├── DeleteCategoryDialog.tsx
│   │   └── index.ts
│   │
│   ├── Export/                       # Export components
│   │   ├── ExportButton.tsx
│   │   ├── exportUtils.ts
│   │   └── index.ts
│   │
│   └── Import/                       # Import components
│       ├── ImportButton.tsx
│       ├── ImportFileUpload.tsx
│       ├── ImportPreview.tsx
│       ├── ImportDialog.tsx
│       └── index.ts
│
├── lib/
│   ├── validations/product.ts        # Zod schemas
│   ├── sku.ts                        # SKU generation utilities
│   └── tax.ts                        # Tax category definitions
│
├── types/product.ts                  # Product TypeScript interfaces
│
└── services/api/
    └── categoryService.ts            # Category API service
```

## Component Groups

### Group A: Page Routes & Layout
- Products layout with sidebar navigation
- All page routes with server components
- Loading skeletons and error boundaries
- Dynamic routes with `params` as `Promise<{ id: string }>`

### Group B: Product List
- Data table with TanStack Table v8
- Custom cell renderers (name, price, stock, status, actions)
- Search, status, category, and stock filters
- Bulk actions bar for multi-select operations
- Debounced search with `useDebounce` hook

### Group C: Product Form
- React Hook Form with Zod validation
- Sections: Basic Info, Description, Pricing (LKR), Inventory, Categorization, Media
- PriceInput component with LKR formatting
- Image upload with drag-and-drop
- Category multi-select and tags input
- SKU auto-generation utility

### Group D: Product Detail
- Detail view with header, info, pricing, inventory cards
- Image gallery with lightbox dialog
- Activity timeline with typed activity events
- Delete product dialog using ConfirmDialog

### Group E: Variants & Categories
- Variant attribute selector (max 3 attributes)
- Variant matrix with cartesian product generation
- Variant table with inline editing
- Bulk edit dialog for price/stock/status operations
- Category tree with recursive rendering
- Category form with auto-slug, parent select, image upload
- Delete category dialog with product/children handling

### Group F: Import/Export
- Export button with format selector popover (CSV/Excel/PDF)
- CSV export with client-side generation
- Import button opening multi-step dialog
- File upload with drag-and-drop, CSV parsing
- Column mapping with auto-detection
- Data validation with error/warning display
- Import preview table with validation highlighting

## Key Patterns

### Server/Client Boundary
All page routes are server components using Suspense to wrap client "View" components:
```tsx
// page.tsx (Server Component)
export default function Page() {
  return (
    <Suspense fallback={<Skeleton />}>
      <ClientView />
    </Suspense>
  );
}
```

### Form Pattern
Forms use React Hook Form with Zod resolver:
```tsx
const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(schema),
  defaultValues: { ... },
});
```

### Delete Dialogs
All destructive dialogs use the shared `ConfirmDialog` component (not AlertDialog):
```tsx
<ConfirmDialog variant="destructive" ... />
```

### Currency Formatting
LKR currency formatting via `Intl.NumberFormat('en-LK', { style: 'currency', currency: 'LKR' })`.

## API Integration Points

All components currently use mock data with TODO comments marking where API calls should be wired:
- Product CRUD: `services/api/productService.ts`
- Category CRUD: `services/api/categoryService.ts`
- Export endpoints: `POST /api/v1/products/export/{format}`
- Import endpoint: `POST /api/v1/products/bulk-import`

## TypeScript Types

Core types defined in `types/product.ts`:
- `Product`, `ProductStatus`, `ProductType`
- `ProductPricing`, `ProductInventory`, `ProductVariant`
- `ProductImage`, `ProductCategory`, `ProductBrand`
- `ProductCreateRequest`, `ProductUpdateRequest`
- `ProductSearchParams`, `ProductBulkOperation`
