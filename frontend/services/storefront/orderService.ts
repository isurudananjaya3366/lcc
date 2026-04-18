import type { StoreCartItem } from '@/stores/store';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface OrderLineItem {
  productId: string;
  name: string;
  sku: string;
  price: number;
  quantity: number;
  variant: Record<string, string> | null;
}

export interface OrderSubmitPayload {
  contactInfo: {
    email: string;
    phone: string;
    firstName: string;
    lastName: string;
  };
  shippingAddress: {
    province: string;
    district: string;
    city: string;
    address1: string;
    address2?: string;
    landmark?: string;
    postalCode: string;
  };
  shippingMethodId: string;
  paymentMethod: string;
  items: OrderLineItem[];
  discountCode?: string;
}

export interface OrderConfirmation {
  orderId: string;
  orderNumber: string;
  status: 'pending' | 'confirmed' | 'processing';
  total: number;
  currency: string;
  estimatedDelivery: string;
  createdAt: string;
}

export interface OrderStatus {
  orderId: string;
  orderNumber: string;
  status: string;
  updatedAt: string;
}

// ─── Config ─────────────────────────────────────────────────────────────────

const API_BASE = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/store`;

// ─── API Functions ──────────────────────────────────────────────────────────

export async function submitOrder(payload: OrderSubmitPayload): Promise<OrderConfirmation> {
  const response = await fetch(`${API_BASE}/orders/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(
      (error as { detail?: string }).detail || `Order submission failed (${response.status})`
    );
  }

  return response.json();
}

export async function getOrderStatus(orderId: string): Promise<OrderStatus> {
  const response = await fetch(`${API_BASE}/orders/${encodeURIComponent(orderId)}/status/`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(
      (error as { detail?: string }).detail || `Failed to get order status (${response.status})`
    );
  }

  return response.json();
}

// ─── Helpers ────────────────────────────────────────────────────────────────

export function cartItemsToOrderLines(items: StoreCartItem[]): OrderLineItem[] {
  return items.map((item) => ({
    productId: item.productId,
    name: item.name,
    sku: item.sku,
    price: item.price,
    quantity: item.quantity,
    variant: item.variant,
  }));
}
