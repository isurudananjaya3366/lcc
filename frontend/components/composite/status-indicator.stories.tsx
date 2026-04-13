import type { Meta, StoryObj } from '@storybook/react';
import { StatusIndicator } from '@/components/composite';

const meta = {
  title: 'Composite/StatusIndicator',
  component: StatusIndicator,
  parameters: { layout: 'centered' },
  tags: ['autodocs'],
  argTypes: {
    status: {
      control: 'select',
      options: ['active', 'inactive', 'pending', 'processing', 'completed', 'cancelled', 'failed', 'paid', 'unpaid', 'partial', 'shipped', 'delivered'],
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
    },
  },
} satisfies Meta<typeof StatusIndicator>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Active: Story = {
  args: { status: 'active', showDot: true },
};

export const Pending: Story = {
  args: { status: 'pending', showDot: true },
};

export const Failed: Story = {
  args: { status: 'failed' },
};

export const Paid: Story = {
  args: { status: 'paid', showDot: true },
};

export const Processing: Story = {
  args: { status: 'processing', showDot: true },
};

export const AllStatuses: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <StatusIndicator status="active" showDot />
      <StatusIndicator status="inactive" />
      <StatusIndicator status="pending" showDot />
      <StatusIndicator status="processing" showDot />
      <StatusIndicator status="completed" />
      <StatusIndicator status="cancelled" />
      <StatusIndicator status="failed" />
      <StatusIndicator status="paid" showDot />
      <StatusIndicator status="unpaid" />
      <StatusIndicator status="partial" />
      <StatusIndicator status="shipped" />
      <StatusIndicator status="delivered" />
    </div>
  ),
};

export const Sizes: Story = {
  render: () => (
    <div className="flex items-center gap-2">
      <StatusIndicator status="active" showDot size="sm" />
      <StatusIndicator status="active" showDot size="md" />
      <StatusIndicator status="active" showDot size="lg" />
    </div>
  ),
};
