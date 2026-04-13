# Layout & Overlay Components

Page-level layout and modal/overlay components.

## Card

Content container with header, body and footer sections.

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui';

<Card>
  <CardHeader>
    <CardTitle>Order Summary</CardTitle>
    <CardDescription>Review your items.</CardDescription>
  </CardHeader>
  <CardContent>{/* content */}</CardContent>
  <CardFooter>{/* actions */}</CardFooter>
</Card>
```

---

## Tabs

Tabbed navigation with three visual variants: default, pills, enclosed.

```tsx
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui';

<Tabs defaultValue="general">
  <TabsList>
    <TabsTrigger value="general">General</TabsTrigger>
    <TabsTrigger value="advanced">Advanced</TabsTrigger>
  </TabsList>
  <TabsContent value="general">General settings</TabsContent>
  <TabsContent value="advanced">Advanced settings</TabsContent>
</Tabs>
```

---

## Accordion

Collapsible content sections.

```tsx
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui';

<Accordion type="single" collapsible>
  <AccordionItem value="faq-1">
    <AccordionTrigger>What is this?</AccordionTrigger>
    <AccordionContent>This is an accordion.</AccordionContent>
  </AccordionItem>
</Accordion>
```

---

## Dialog / ConfirmDialog / FormDialog

Modal overlays for confirmations and forms.

```tsx
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui';
import { ConfirmDialog, FormDialog } from '@/components/ui';

// Basic dialog
<Dialog>
  <DialogTrigger asChild><Button>Open</Button></DialogTrigger>
  <DialogContent>
    <DialogHeader><DialogTitle>Title</DialogTitle></DialogHeader>
    {/* content */}
  </DialogContent>
</Dialog>

// Confirm dialog (destructive action)
<ConfirmDialog
  title="Delete Item?"
  description="This action cannot be undone."
  variant="destructive"
  onConfirm={handleDelete}
/>

// Form dialog
<FormDialog title="Create Product" onSubmit={handleSubmit}>
  {/* form fields */}
</FormDialog>
```

---

## Sheet (Side Panel)

Slide-out panel from any edge.

```tsx
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui';

<Sheet>
  <SheetTrigger asChild><Button>Open Panel</Button></SheetTrigger>
  <SheetContent side="right">
    <SheetHeader><SheetTitle>Details</SheetTitle></SheetHeader>
    {/* content */}
  </SheetContent>
</Sheet>
```

---

## DropdownMenu / ContextMenu

Action menus with keyboard navigation.

```tsx
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui';

<DropdownMenu>
  <DropdownMenuTrigger asChild><Button variant="ghost">⋮</Button></DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuItem>Edit</DropdownMenuItem>
    <DropdownMenuItem className="text-destructive">Delete</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

---

## Tooltip

Contextual information on hover/focus.

```tsx
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui';

<TooltipProvider>
  <Tooltip>
    <TooltipTrigger>Hover me</TooltipTrigger>
    <TooltipContent>Additional information</TooltipContent>
  </Tooltip>
</TooltipProvider>
```

---

## Command / CommandPalette

Searchable command menu (⌘K).

```tsx
import { CommandPalette } from '@/components/common';

// Global command palette — typically mounted in root layout
<CommandPalette
  groups={[
    { heading: 'Navigation', items: [{ label: 'Dashboard', onSelect: () => router.push('/') }] },
    { heading: 'Actions', items: [{ label: 'Create Product', onSelect: openCreateDialog }] },
  ]}
/>
```

---

## PageHeader

Page title bar with breadcrumb, description, and action buttons.

```tsx
import { PageHeader } from '@/components/composite';

<PageHeader
  title="Products"
  description="Manage your catalog."
  breadcrumb={[
    { label: 'Home', href: '/' },
    { label: 'Products' },
  ]}
  actions={<Button>Add Product</Button>}
/>
```

---

## PageContainer

Responsive content wrapper with max-width constraints.

```tsx
import { PageContainer } from '@/components/composite';

<PageContainer maxWidth="xl" padding="md">
  {/* page content */}
</PageContainer>
```

| maxWidth | Value |
|----------|-------|
| sm | 640px |
| md | 768px |
| lg | 1024px |
| xl | 1280px |
| 2xl | 1536px |
| full | 100% |

---

## Accessibility

- Dialogs trap focus and close with Escape
- Sheet announces content via aria-label
- DropdownMenu supports Arrow key navigation
- Tooltip triggered on both hover and focus
- Command palette keyboard navigable
