import type { Meta, StoryObj } from '@storybook/react';
import { Timeline } from '@/components/composite';

const meta = {
  title: 'Composite/Timeline',
  component: Timeline,
  parameters: { layout: 'padded' },
  tags: ['autodocs'],
} satisfies Meta<typeof Timeline>;

export default meta;
type Story = StoryObj<typeof meta>;

export const OrderTracking: Story = {
  args: {
    items: [
      { date: new Date(), title: 'Order Delivered', description: 'Package was delivered to the customer.', status: 'success' },
      { date: new Date(Date.now() - 86400000), title: 'Out for Delivery', description: 'Package is on the way.', status: 'info' },
      { date: new Date(Date.now() - 172800000), title: 'Shipped', description: 'Package left the warehouse.', status: 'info' },
      { date: new Date(Date.now() - 259200000), title: 'Processing', description: 'Order is being prepared.', status: 'pending' },
      { date: new Date(Date.now() - 345600000), title: 'Order Placed', description: 'Order #12345 was placed.', status: 'info' },
    ],
  },
};

export const MixedStatuses: Story = {
  args: {
    items: [
      { date: new Date(Date.now() - 3600000), title: 'Payment Failed', description: 'Credit card was declined.', status: 'error' },
      { date: new Date(Date.now() - 7200000), title: 'Retry Initiated', status: 'pending' },
      { date: new Date(Date.now() - 86400000), title: 'Order Created', status: 'success' },
    ],
  },
};
