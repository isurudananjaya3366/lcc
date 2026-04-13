# Data Display Components

Components for rendering tabular data, states, and feedback.

## Table

Basic HTML table with styled headers, rows, and cells.

```tsx
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui';

<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Name</TableHead>
      <TableHead>Price</TableHead>
      <TableHead>Stock</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>Widget</TableCell>
      <TableCell>LKR 1,500</TableCell>
      <TableCell>42</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

---

## DataTable (TanStack React Table v8)

Full-featured data table with sorting, filtering, pagination, and column toggling.

```tsx
import { DataTable } from '@/components/ui';
import { ColumnDef } from '@tanstack/react-table';

const columns: ColumnDef<Product>[] = [
  { accessorKey: 'name', header: 'Name' },
  { accessorKey: 'price', header: 'Price' },
  { accessorKey: 'stock', header: 'Stock' },
];

<DataTable columns={columns} data={products} />
```

### Sub-components

| Component | Purpose |
|-----------|---------|
| `TablePagination` | Page navigation with page size selector |
| `TableToolbar` | Search input + filter/action buttons above table |
| `TableColumnToggle` | Show/hide columns dropdown |

---

## StatCard

KPI dashboard card with trend indicators.

```tsx
import { StatCard } from '@/components/dashboard';

<StatCard
  title="Total Revenue"
  value="LKR 2.4M"
  trend="up"
  trendValue="+12.5%"
  description="vs last month"
/>
```

---

## DescriptionList

Key-value pair display for detail views.

```tsx
import { DescriptionList } from '@/components/composite';

<DescriptionList
  columns={2}
  orientation="horizontal"
  items={[
    { label: 'Order ID', value: '#ORD-12345' },
    { label: 'Status', value: <StatusIndicator status="paid" showDot /> },
    { label: 'Customer', value: 'John Doe' },
    { label: 'Total', value: 'LKR 15,500.00' },
  ]}
/>
```

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| columns | `1 \| 2 \| 3` | `1` | Column layout |
| orientation | `'horizontal' \| 'vertical'` | `'horizontal'` | Label/value arrangement |

---

## Timeline

Vertical chronological event display with status colors.

```tsx
import { Timeline } from '@/components/composite';

<Timeline
  items={[
    { date: new Date(), title: 'Delivered', status: 'success' },
    { date: '2024-01-15', title: 'Shipped', status: 'info' },
    { date: '2024-01-14', title: 'Processing', status: 'pending' },
    { date: '2024-01-13', title: 'Order Placed', status: 'info' },
  ]}
/>
```

| Status | Color | Use Case |
|--------|-------|----------|
| success | Green | Completed actions |
| pending | Yellow | In-progress states |
| error | Red | Failed operations |
| info | Blue | Informational events |

---

## StatusIndicator

Color-coded status badge with optional animated dot.

```tsx
import { StatusIndicator } from '@/components/composite';

<StatusIndicator status="active" showDot />
<StatusIndicator status="pending" size="sm" />
<StatusIndicator status="paid" label="Payment Received" />
```

12 predefined statuses: `active`, `inactive`, `pending`, `processing`, `completed`, `cancelled`, `failed`, `paid`, `unpaid`, `partial`, `shipped`, `delivered`.

---

## State Components

### EmptyState
Placeholder for empty data views.

```tsx
import { EmptyState } from '@/components/composite';

<EmptyState
  title="No products found"
  description="Try adjusting your search or add a new product."
  action={<Button>Add Product</Button>}
/>
```

### ErrorState
Error feedback with retry action.

```tsx
import { ErrorState } from '@/components/composite';

<ErrorState message="Failed to load data." onRetry={handleRetry} />
```

### LoadingState
Loading placeholders with multiple modes.

```tsx
import { LoadingState } from '@/components/composite';

<LoadingState mode="contained" />   {/* Spinner in container */}
<LoadingState mode="fullPage" />    {/* Full viewport spinner */}
<LoadingState mode="overlay" />     {/* Semi-transparent overlay */}
```

---

## Toast Notifications

```tsx
import { useToast } from '@/hooks/use-toast';

const { success, error, warning, info, loading, promise } = useToast();

success('Product saved!');
error('Failed to delete product.');
promise(saveProduct(), {
  loading: 'Saving...',
  success: 'Saved!',
  error: 'Failed to save.',
});
```

---

## Utility Components

### CopyButton
Copy text to clipboard with visual feedback.

```tsx
import { CopyButton } from '@/components/composite';

<CopyButton value="ORD-12345" label="Copy ID" />
<CopyButton value={apiKey} showLabel={false} size="sm" />
```

### ExportButton
Dropdown export with PDF/Excel/CSV format selection.

```tsx
import { ExportButton } from '@/components/composite';

<ExportButton
  onExport={(format) => downloadReport(format)}
  formats={['PDF', 'Excel', 'CSV']}
/>
```

---

## Accessibility

- Tables use `<thead>`, `<tbody>`, proper `<th>` with scope
- DataTable supports keyboard navigation through rows
- Timeline uses semantic time elements with `dateTime`
- StatusIndicator uses semantic color + text (not color-only)
- CopyButton announces "Copied" via `aria-live="polite"`
- Toasts auto-dismiss and support keyboard dismissal
