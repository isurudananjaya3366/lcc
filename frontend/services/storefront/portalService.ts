import type {
  PortalStats,
  PortalOrder,
  OrderStatus,
  PortalOrderItem,
  PortalAddress,
  WishlistItem,
  PortalReview,
} from '@/types/storefront/portal.types';
import type { StoreUser } from '@/types/storefront/auth.types';

// ─── Settings Types ─────────────────────────────────────────────────────────

export type NotificationPrefs = {
  orderUpdates: boolean;
  promotions: boolean;
  newsletter: boolean;
  smsNotifications: boolean;
};

// ─── Mock Data ──────────────────────────────────────────────────────────────

const mockAddress: PortalAddress = {
  id: 'addr-1',
  label: 'Home',
  firstName: 'Kamal',
  lastName: 'Perera',
  phone: '+94 77 123 4567',
  addressLine1: '42 Galle Road',
  addressLine2: 'Apt 3B',
  city: 'Colombo 03',
  district: 'Colombo',
  province: 'Western',
  postalCode: '00300',
  country: 'Sri Lanka',
  isDefault: true,
  type: 'shipping',
};

const mockItems: PortalOrderItem[] = [
  {
    id: 'item-1',
    productId: 'prod-1',
    name: 'Ceylon Cinnamon Gift Box',
    sku: 'CCG-001',
    image: '/images/products/cinnamon-box.jpg',
    price: 2500,
    quantity: 2,
    variant: { size: 'Large' },
    lineTotal: 5000,
  },
  {
    id: 'item-2',
    productId: 'prod-2',
    name: 'Organic Tea Collection',
    sku: 'OTC-015',
    image: '/images/products/tea-collection.jpg',
    price: 1800,
    quantity: 1,
    lineTotal: 1800,
  },
];

const mockOrders: PortalOrder[] = [
  {
    id: 'order-1',
    orderNumber: 'ORD-2026-0001',
    status: 'delivered',
    createdAt: '2026-04-10T09:30:00Z',
    updatedAt: '2026-04-14T16:00:00Z',
    items: mockItems,
    subtotal: 6800,
    shipping: 350,
    tax: 0,
    discount: 500,
    total: 6650,
    shippingAddress: mockAddress,
    paymentMethod: 'Card ending in 4242',
    trackingNumber: 'LK20260410001',
    estimatedDelivery: '2026-04-14',
  },
  {
    id: 'order-2',
    orderNumber: 'ORD-2026-0002',
    status: 'shipped',
    createdAt: '2026-04-15T14:20:00Z',
    updatedAt: '2026-04-16T10:00:00Z',
    items: [mockItems[0]!],
    subtotal: 5000,
    shipping: 350,
    tax: 0,
    discount: 0,
    total: 5350,
    shippingAddress: {
      ...mockAddress,
      id: 'addr-2',
      label: 'Office',
      addressLine1: '15 Duplication Road',
      city: 'Colombo 04',
      postalCode: '00400',
    },
    paymentMethod: 'Cash on Delivery',
    trackingNumber: 'LK20260415002',
    estimatedDelivery: '2026-04-19',
  },
  {
    id: 'order-3',
    orderNumber: 'ORD-2026-0003',
    status: 'pending',
    createdAt: '2026-04-18T08:45:00Z',
    updatedAt: '2026-04-18T08:45:00Z',
    items: [mockItems[1]!],
    subtotal: 1800,
    shipping: 250,
    tax: 0,
    discount: 0,
    total: 2050,
    shippingAddress: mockAddress,
    paymentMethod: 'Bank Transfer',
  },
];

// ─── Helper ─────────────────────────────────────────────────────────────────

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ─── Service Functions ──────────────────────────────────────────────────────

export async function getDashboardStats(): Promise<PortalStats> {
  await delay(400);
  return {
    totalOrders: mockOrders.length,
    pendingOrders: mockOrders.filter((o) => o.status === 'pending').length,
    wishlistCount: 5,
    reviewsCount: 2,
  };
}

export async function getOrders(
  params?: { status?: OrderStatus; page?: number; pageSize?: number }
): Promise<{ orders: PortalOrder[]; total: number; page: number; pageSize: number }> {
  await delay(500);

  const status = params?.status;
  const page = params?.page ?? 1;
  const pageSize = params?.pageSize ?? 10;

  let filtered = [...mockOrders];
  if (status) {
    filtered = filtered.filter((o) => o.status === status);
  }

  const total = filtered.length;
  const start = (page - 1) * pageSize;
  const paged = filtered.slice(start, start + pageSize);

  return { orders: paged, total, page, pageSize };
}

export async function getOrderById(id: string): Promise<PortalOrder> {
  await delay(300);
  const order = mockOrders.find((o) => o.id === id);
  if (!order) {
    throw new Error(`Order not found: ${id}`);
  }
  return order;
}

// ─── Address Service Functions ──────────────────────────────────────────────

const mockAddresses: PortalAddress[] = [
  {
    id: 'addr-1',
    label: 'Home',
    firstName: 'Kamal',
    lastName: 'Perera',
    phone: '+94 77 123 4567',
    addressLine1: '42 Galle Road',
    addressLine2: 'Apt 3B',
    city: 'Colombo',
    district: 'Colombo',
    province: 'Western',
    postalCode: '00300',
    country: 'Sri Lanka',
    isDefault: true,
    type: 'shipping',
  },
  {
    id: 'addr-2',
    label: 'Office',
    firstName: 'Kamal',
    lastName: 'Perera',
    phone: '+94 11 234 5678',
    addressLine1: '15 Duplication Road',
    city: 'Colombo',
    district: 'Colombo',
    province: 'Western',
    postalCode: '00400',
    country: 'Sri Lanka',
    isDefault: false,
    type: 'billing',
  },
];

export async function getAddresses(): Promise<PortalAddress[]> {
  await delay(400);
  return [...mockAddresses];
}

export async function createAddress(
  data: Omit<PortalAddress, 'id'>
): Promise<PortalAddress> {
  await delay(400);
  const newAddress: PortalAddress = {
    ...data,
    id: `addr-${Date.now()}`,
  };
  mockAddresses.push(newAddress);
  if (newAddress.isDefault) {
    mockAddresses.forEach((a) => {
      if (a.id !== newAddress.id) a.isDefault = false;
    });
  }
  return newAddress;
}

export async function updateAddress(
  id: string,
  data: Partial<PortalAddress>
): Promise<PortalAddress> {
  await delay(400);
  const index = mockAddresses.findIndex((a) => a.id === id);
  if (index === -1) throw new Error(`Address not found: ${id}`);
  mockAddresses[index] = { ...mockAddresses[index]!, ...data } as PortalAddress;
  if (data.isDefault) {
    mockAddresses.forEach((a) => {
      if (a.id !== id) a.isDefault = false;
    });
  }
  return mockAddresses[index]!;
}

export async function deleteAddress(id: string): Promise<void> {
  await delay(300);
  const index = mockAddresses.findIndex((a) => a.id === id);
  if (index === -1) throw new Error(`Address not found: ${id}`);
  mockAddresses.splice(index, 1);
}

export async function setDefaultAddress(id: string): Promise<void> {
  await delay(300);
  const address = mockAddresses.find((a) => a.id === id);
  if (!address) throw new Error(`Address not found: ${id}`);
  mockAddresses.forEach((a) => {
    a.isDefault = a.id === id;
  });
}

// ─── Wishlist Service Functions ─────────────────────────────────────────────

const mockWishlistItems: WishlistItem[] = [
  {
    id: 'wish-1',
    productId: 'prod-10',
    name: 'Ceylon Cinnamon Sticks (100g)',
    image: '/images/products/cinnamon-sticks.jpg',
    price: 850,
    compareAtPrice: 1200,
    slug: 'ceylon-cinnamon-sticks-100g',
    inStock: true,
    addedAt: '2026-04-10T09:00:00Z',
  },
  {
    id: 'wish-2',
    productId: 'prod-11',
    name: 'Organic Green Tea Premium',
    image: '/images/products/green-tea.jpg',
    price: 1450,
    slug: 'organic-green-tea-premium',
    inStock: true,
    addedAt: '2026-04-12T14:30:00Z',
  },
  {
    id: 'wish-3',
    productId: 'prod-12',
    name: 'Handmade Brass Oil Lamp',
    image: '/images/products/brass-lamp.jpg',
    price: 3200,
    compareAtPrice: 4000,
    slug: 'handmade-brass-oil-lamp',
    inStock: false,
    addedAt: '2026-04-14T11:15:00Z',
  },
  {
    id: 'wish-4',
    productId: 'prod-13',
    name: 'Traditional Wooden Mask',
    image: '/images/products/wooden-mask.jpg',
    price: 5500,
    slug: 'traditional-wooden-mask',
    inStock: true,
    addedAt: '2026-04-16T08:45:00Z',
  },
];

export async function getWishlist(): Promise<WishlistItem[]> {
  await delay(400);
  return [...mockWishlistItems];
}

export async function removeFromWishlist(id: string): Promise<void> {
  await delay(300);
  const index = mockWishlistItems.findIndex((item) => item.id === id);
  if (index === -1) throw new Error(`Wishlist item not found: ${id}`);
  mockWishlistItems.splice(index, 1);
}

// ─── Review Service Functions ───────────────────────────────────────────────

const mockReviews: PortalReview[] = [
  {
    id: 'rev-1',
    productId: 'prod-1',
    productName: 'Ceylon Cinnamon Gift Box',
    productImage: '/images/products/cinnamon-box.jpg',
    productSlug: 'ceylon-cinnamon-gift-box',
    rating: 5,
    title: 'Excellent quality cinnamon!',
    content:
      'The cinnamon sticks are perfectly rolled and have an amazing aroma. Best quality I have found online. Packaging was also very premium and suitable for gifting.',
    createdAt: '2026-04-11T10:00:00Z',
    updatedAt: '2026-04-11T10:00:00Z',
    isPublished: true,
  },
  {
    id: 'rev-2',
    productId: 'prod-2',
    productName: 'Organic Tea Collection',
    productImage: '/images/products/tea-collection.jpg',
    productSlug: 'organic-tea-collection',
    rating: 4,
    title: 'Great variety of teas',
    content:
      'Love the selection of teas in this collection. The green tea and black tea are outstanding. Would have given 5 stars but the packaging could be improved.',
    createdAt: '2026-04-13T15:30:00Z',
    updatedAt: '2026-04-13T15:30:00Z',
    isPublished: true,
  },
  {
    id: 'rev-3',
    productId: 'prod-3',
    productName: 'Coconut Shell Craft Bowl',
    productImage: '/images/products/coconut-bowl.jpg',
    productSlug: 'coconut-shell-craft-bowl',
    rating: 3,
    title: 'Decent product, slow delivery',
    content:
      'The bowl itself is nicely crafted and looks beautiful. However, the delivery took longer than expected. The finish could be a bit smoother.',
    createdAt: '2026-04-15T09:20:00Z',
    updatedAt: '2026-04-16T12:00:00Z',
    isPublished: false,
  },
];

export async function getMyReviews(): Promise<PortalReview[]> {
  await delay(400);
  return [...mockReviews];
}

export async function deleteReview(id: string): Promise<void> {
  await delay(300);
  const index = mockReviews.findIndex((r) => r.id === id);
  if (index === -1) throw new Error(`Review not found: ${id}`);
  mockReviews.splice(index, 1);
}

export async function updateReview(
  id: string,
  data: { rating: number; title: string; content: string }
): Promise<PortalReview> {
  await delay(400);
  const index = mockReviews.findIndex((r) => r.id === id);
  if (index === -1) throw new Error(`Review not found: ${id}`);
  mockReviews[index] = {
    ...mockReviews[index]!,
    ...data,
    updatedAt: new Date().toISOString(),
  } as PortalReview;
  return mockReviews[index]!;
}

// ─── Account Settings Service Functions ─────────────────────────────────────

export async function updateProfile(data: {
  firstName: string;
  lastName: string;
  phone?: string;
}): Promise<StoreUser> {
  await delay(400);
  return {
    id: 'user-1',
    email: 'kamal@example.com',
    firstName: data.firstName,
    lastName: data.lastName,
    phone: data.phone,
    createdAt: '2026-01-15T08:00:00Z',
  };
}

export async function changePassword(data: {
  currentPassword: string;
  newPassword: string;
}): Promise<void> {
  await delay(500);
  if (data.currentPassword === data.newPassword) {
    throw new Error('New password must be different from current password');
  }
}

export async function getNotificationPrefs(): Promise<NotificationPrefs> {
  await delay(300);
  return {
    orderUpdates: true,
    promotions: false,
    newsletter: true,
    smsNotifications: false,
  };
}

export async function updateNotificationPrefs(
  prefs: NotificationPrefs
): Promise<void> {
  await delay(300);
  void prefs;
}

export async function deleteAccount(password: string): Promise<void> {
  await delay(500);
  if (!password) {
    throw new Error('Password is required');
  }
}
