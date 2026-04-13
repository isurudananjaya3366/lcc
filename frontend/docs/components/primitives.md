# UI Primitives

Core building-block components built on Radix UI primitives with Tailwind CSS styling and CVA variants.

## Button

Versatile button component with multiple variants and states.

```tsx
import { Button } from '@/components/ui';

// Variants
<Button variant="default">Primary</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="destructive">Delete</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="link">Link</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="default">Default</Button>
<Button size="lg">Large</Button>
<Button size="icon"><Icon name="plus" /></Button>

// States
<Button isLoading>Saving...</Button>
<Button disabled>Disabled</Button>
```

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | `'default' \| 'destructive' \| 'outline' \| 'secondary' \| 'ghost' \| 'link'` | `'default'` | Visual style |
| size | `'default' \| 'sm' \| 'lg' \| 'icon'` | `'default'` | Size variant |
| isLoading | `boolean` | `false` | Shows spinner |
| asChild | `boolean` | `false` | Render as child element |

### Accessibility
- Full keyboard support (Tab, Enter, Space)
- Disabled state prevents interaction and announces to screen readers
- Loading state shows spinner with aria-busy

---

## Input

Text input with prefix/suffix slots, clearable, and validation states.

```tsx
import { Input } from '@/components/ui';

<Input placeholder="Enter name..." />
<Input type="email" placeholder="email@example.com" />
<Input disabled placeholder="Disabled" />
```

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| type | `string` | `'text'` | HTML input type |
| prefix | `ReactNode` | - | Leading content |
| suffix | `ReactNode` | - | Trailing content |
| clearable | `boolean` | `false` | Show clear button |

---

## Textarea

Multi-line text input.

```tsx
import { Textarea } from '@/components/ui';

<Textarea placeholder="Enter description..." rows={4} />
```

---

## Select

Full-featured dropdown select built on Radix UI.

```tsx
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui';

<Select>
  <SelectTrigger><SelectValue placeholder="Choose..." /></SelectTrigger>
  <SelectContent>
    <SelectItem value="option1">Option 1</SelectItem>
    <SelectItem value="option2">Option 2</SelectItem>
  </SelectContent>
</Select>
```

---

## Checkbox, RadioGroup, Switch

Toggle controls built on Radix UI primitives.

```tsx
import { Checkbox, RadioGroup, RadioGroupItem, Switch } from '@/components/ui';

<Checkbox id="terms" />
<RadioGroup defaultValue="a">
  <RadioGroupItem value="a" />
  <RadioGroupItem value="b" />
</RadioGroup>
<Switch />
```

---

## Badge

Status labels with semantic color variants.

```tsx
import { Badge } from '@/components/ui';

<Badge>Default</Badge>
<Badge variant="success">Active</Badge>
<Badge variant="warning">Pending</Badge>
<Badge variant="destructive">Error</Badge>
```

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | `'default' \| 'secondary' \| 'destructive' \| 'outline' \| 'success' \| 'warning'` | `'default'` | Color variant |

---

## Label

Form field labels with required indicator support.

```tsx
import { Label } from '@/components/ui';

<Label htmlFor="name">Full Name</Label>
```

---

## Avatar

User avatar with image and fallback support.

```tsx
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui';

<Avatar>
  <AvatarImage src="/photo.jpg" alt="User" />
  <AvatarFallback>JD</AvatarFallback>
</Avatar>
```

---

## Separator, Slider, Progress

Utility UI primitives.

```tsx
import { Separator, Slider, Progress } from '@/components/ui';

<Separator />
<Slider defaultValue={[50]} max={100} step={1} />
<Progress value={60} />
```

---

## Skeleton

Loading placeholder animations.

```tsx
import { Skeleton, TableSkeleton, CardSkeleton } from '@/components/ui';

<Skeleton className="h-4 w-[200px]" />
<TableSkeleton rows={5} columns={4} />
<CardSkeleton count={3} />
```

---

## Alert

Contextual feedback messages with variants.

```tsx
import { Alert, AlertTitle, AlertDescription } from '@/components/ui';

<Alert variant="destructive">
  <AlertTitle>Error</AlertTitle>
  <AlertDescription>Something went wrong.</AlertDescription>
</Alert>
```
