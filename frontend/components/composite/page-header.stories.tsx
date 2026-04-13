import type { Meta, StoryObj } from '@storybook/react';
import { PageHeader } from '@/components/composite';
import { Button } from '@/components/ui';

const meta = {
  title: 'Composite/PageHeader',
  component: PageHeader,
  parameters: { layout: 'padded' },
  tags: ['autodocs'],
} satisfies Meta<typeof PageHeader>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Basic: Story = {
  args: {
    title: 'Products',
  },
};

export const WithDescription: Story = {
  args: {
    title: 'Products',
    description: 'Manage your product catalog and inventory.',
  },
};

export const WithBreadcrumbAndActions: Story = {
  args: {
    title: 'Product Details',
    description: 'View and edit product information.',
    breadcrumb: [
      { label: 'Home', href: '/' },
      { label: 'Products', href: '/products' },
      { label: 'Widget Pro' },
    ],
    actions: (
      <div className="flex gap-2">
        <Button variant="outline">Cancel</Button>
        <Button>Save Changes</Button>
      </div>
    ),
  },
};

export const WithBackButton: Story = {
  args: {
    title: 'Edit Product',
    backHref: '/products',
    description: 'Update product details.',
  },
};
