import type { Meta, StoryObj } from '@storybook/react';
import { Badge } from '@/components/ui';

const meta = {
  title: 'UI/Badge',
  component: Badge,
  parameters: { layout: 'centered' },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'secondary', 'destructive', 'outline', 'success', 'warning'],
    },
  },
} satisfies Meta<typeof Badge>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { children: 'Badge' },
};

export const Secondary: Story = {
  args: { variant: 'secondary', children: 'Secondary' },
};

export const Destructive: Story = {
  args: { variant: 'destructive', children: 'Error' },
};

export const Outline: Story = {
  args: { variant: 'outline', children: 'Outline' },
};

export const Success: Story = {
  args: { variant: 'success', children: 'Active' },
};

export const Warning: Story = {
  args: { variant: 'warning', children: 'Pending' },
};
