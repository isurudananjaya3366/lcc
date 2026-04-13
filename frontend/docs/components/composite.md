# Composite Components

Higher-order components that combine multiple UI primitives for common ERP patterns.

## Component Architecture

```
@/components/
├── ui/           → Atomic primitives (Button, Input, Card, Table...)
├── composite/    → Composed patterns (PageHeader, StatusIndicator, Timeline...)
├── dashboard/    → Dashboard-specific (StatCard)
├── common/       → Shared layout (SidePanel, CommandPalette)
└── hooks/        → Custom hooks (useToast)
```

## Import Patterns

```tsx
// UI primitives — single import line
import { Button, Input, Card, Badge, Table } from '@/components/ui';

// Composite components
import {
  PageHeader,
  PageContainer,
  Breadcrumb,
  DescriptionList,
  Timeline,
  StatusIndicator,
  CopyButton,
  ExportButton,
} from '@/components/composite';

// Dashboard components
import { StatCard } from '@/components/dashboard';

// Common layout
import { SidePanel, CommandPalette } from '@/components/common';
```

---

## Page Layout Pattern

Standard ERP page layout combining PageContainer, PageHeader, and content.

```tsx
import { PageContainer, PageHeader } from '@/components/composite';
import { Button } from '@/components/ui';

export default function ProductsPage() {
  return (
    <PageContainer maxWidth="2xl" padding="md">
      <PageHeader
        title="Products"
        description="Manage your product catalog."
        breadcrumb={[
          { label: 'Home', href: '/' },
          { label: 'Products' },
        ]}
        actions={
          <div className="flex gap-2">
            <ExportButton onExport={handleExport} />
            <Button>Add Product</Button>
          </div>
        }
      />

      <div className="mt-6">
        <DataTable columns={columns} data={products} />
      </div>
    </PageContainer>
  );
}
```

---

## Detail Page Pattern

Product/order detail view with description list and timeline.

```tsx
import { PageContainer, PageHeader, DescriptionList, Timeline, StatusIndicator } from '@/components/composite';
import { Card, CardContent, CardHeader, CardTitle, Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui';

export default function OrderDetailPage({ order }) {
  return (
    <PageContainer>
      <PageHeader
        title={`Order ${order.id}`}
        backHref="/orders"
        actions={<CopyButton value={order.id} label="Copy ID" />}
      />

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Order Details</CardTitle>
          </CardHeader>
          <CardContent>
            <DescriptionList
              columns={2}
              items={[
                { label: 'Status', value: <StatusIndicator status={order.status} showDot /> },
                { label: 'Customer', value: order.customerName },
                { label: 'Total', value: `LKR ${order.total.toLocaleString()}` },
                { label: 'Date', value: order.createdAt },
              ]}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Activity</CardTitle></CardHeader>
          <CardContent>
            <Timeline items={order.events} />
          </CardContent>
        </Card>
      </div>
    </PageContainer>
  );
}
```

---

## Dashboard Pattern

KPI cards with data table.

```tsx
import { StatCard } from '@/components/dashboard';
import { PageContainer, PageHeader } from '@/components/composite';

export default function DashboardPage() {
  return (
    <PageContainer maxWidth="full">
      <PageHeader title="Dashboard" />

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Revenue" value="LKR 2.4M" trend="up" trendValue="+12%" />
        <StatCard title="Orders" value="1,234" trend="up" trendValue="+8%" />
        <StatCard title="Products" value="456" trend="neutral" trendValue="0%" />
        <StatCard title="Returns" value="23" trend="down" trendValue="-5%" />
      </div>
    </PageContainer>
  );
}
```

---

## Best Practices

1. **Use barrel imports** — import from `@/components/ui` and `@/components/composite`, not individual files
2. **Prefer composition** — combine primitives into page patterns rather than creating monolithic components
3. **Keep state up** — composite components are controlled; manage state in the parent
4. **Use semantic HTML** — components use proper landmarks (`nav`, `main`, `section`)
5. **Test accessibility** — run Storybook's a11y addon for every new component composition

## Common Pitfalls

- **Don't nest Cards** — use sections within a Card instead
- **Don't skip FormField** — always wrap inputs in FormField for proper label/error binding
- **Don't hardcode colors** — use CSS variables and Tailwind classes for theme support
- **Don't forget dark mode** — test every layout in both light and dark themes
- **Don't ignore loading states** — use Skeleton/LoadingState for async content

## Responsive Breakpoints

| Breakpoint | Width | Use Case |
|------------|-------|----------|
| `sm` | ≥640px | Small tablets |
| `md` | ≥768px | Tablets |
| `lg` | ≥1024px | Desktops |
| `xl` | ≥1280px | Large desktops |
| `2xl` | ≥1536px | Ultra-wide |
