# Form Components

Form building components integrating React Hook Form with Zod validation.

## Form (React Hook Form Integration)

Wraps React Hook Form with accessible form fields.

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui';
import { Input, Button } from '@/components/ui';

const schema = z.object({
  name: z.string().min(1, 'Required'),
  email: z.string().email('Invalid email'),
});

function MyForm() {
  const form = useForm({ resolver: zodResolver(schema) });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Name</FormLabel>
              <FormControl><Input {...field} /></FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  );
}
```

---

## FormSection

Groups related form fields with heading and description.

```tsx
import { FormSection } from '@/components/composite';

<FormSection title="Personal Information" description="Enter your details.">
  {/* form fields */}
</FormSection>
```

---

## FormActions

Consistent form button layout (submit, cancel, etc.).

```tsx
import { FormActions } from '@/components/composite';
import { Button } from '@/components/ui';

<FormActions>
  <Button variant="outline">Cancel</Button>
  <Button type="submit">Save</Button>
</FormActions>
```

---

## Specialized Inputs

### MoneyInput
Currency input formatted for LKR (Sri Lankan Rupee).

```tsx
import { MoneyInput } from '@/components/composite';

<MoneyInput value={1500.00} onChange={setValue} currency="LKR" />
```

### PhoneInput
Phone input with +94 (Sri Lanka) prefix.

```tsx
import { PhoneInput } from '@/components/composite';

<PhoneInput value={phone} onChange={setPhone} />
```

### SearchInput
Debounced search with clear button.

```tsx
import { SearchInput } from '@/components/composite';

<SearchInput placeholder="Search products..." onSearch={handleSearch} debounceMs={300} />
```

### PasswordInput
Password with visibility toggle and strength meter.

```tsx
import { PasswordInput } from '@/components/composite';

<PasswordInput showStrength />
```

### NumberInput
Numeric input with increment/decrement buttons.

```tsx
import { NumberInput } from '@/components/composite';

<NumberInput min={0} max={999} step={1} />
```

---

## File & Image Uploads

### FileUpload
Drag-and-drop file upload with validation.

```tsx
import { FileUpload } from '@/components/composite';

<FileUpload accept=".pdf,.doc" maxSize={5 * 1024 * 1024} onUpload={handleFiles} />
```

### ImageUpload
Image upload with preview thumbnails.

```tsx
import { ImageUpload } from '@/components/composite';

<ImageUpload maxFiles={5} onUpload={handleImages} />
```

---

## Selection Components

### MultiSelect
Checkbox-based multi-select dropdown.

```tsx
import { MultiSelect } from '@/components/composite';

<MultiSelect
  options={[
    { value: 'a', label: 'Option A' },
    { value: 'b', label: 'Option B' },
  ]}
  value={selected}
  onChange={setSelected}
/>
```

### Combobox
Searchable dropdown with async data loading.

```tsx
import { Combobox } from '@/components/composite';

<Combobox
  options={products}
  onSearch={searchProducts}
  placeholder="Find product..."
/>
```

---

## Calendar & Date Pickers

### DatePicker
Single date selection with popover calendar.

```tsx
import { DatePicker } from '@/components/ui';

<DatePicker value={date} onChange={setDate} />
```

### DateRangePicker
Start/end date selection.

```tsx
import { DateRangePicker } from '@/components/composite';

<DateRangePicker value={range} onChange={setRange} />
```

---

## Accessibility

- All form fields connect label to control via `htmlFor`/`id`
- Error messages announced via `aria-describedby`
- Required fields indicated with `aria-required`
- Invalid fields marked with `aria-invalid`
- Keyboard: Tab navigates fields, Space toggles checkboxes/switches
