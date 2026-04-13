import type { Meta, StoryObj } from '@storybook/react';
import { Input } from '@/components/ui';

const meta = {
  title: 'UI/Input',
  component: Input,
  parameters: { layout: 'centered' },
  tags: ['autodocs'],
} satisfies Meta<typeof Input>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { placeholder: 'Enter text...' },
};

export const WithLabel: Story = {
  render: () => (
    <div className="space-y-2">
      <label htmlFor="email" className="text-sm font-medium">Email</label>
      <Input id="email" type="email" placeholder="name@example.com" />
    </div>
  ),
};

export const Disabled: Story = {
  args: { placeholder: 'Disabled', disabled: true },
};

export const WithError: Story = {
  args: { placeholder: 'Invalid', 'aria-invalid': true, className: 'border-destructive' },
};
