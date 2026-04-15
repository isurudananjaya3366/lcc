/**
 * Contact Information Configuration
 *
 * Business contact details, hours, and support info.
 */

export const contactConfig = {
  emails: {
    info: 'info@lankacommerce.lk',
    support: 'support@lankacommerce.lk',
    sales: 'sales@lankacommerce.lk',
    admin: 'admin@lankacommerce.lk',
  },

  phones: {
    main: '+94 11 234 5678',
    support: '+94 11 234 5679',
    mobile: '+94 77 123 4567',
  },

  whatsapp: {
    number: '+94771234567',
    url: 'https://wa.me/94771234567',
  },

  businessHours: {
    timezone: 'Asia/Colombo',
    schedule: [
      { day: 'Monday', open: '09:00', close: '18:00' },
      { day: 'Tuesday', open: '09:00', close: '18:00' },
      { day: 'Wednesday', open: '09:00', close: '18:00' },
      { day: 'Thursday', open: '09:00', close: '18:00' },
      { day: 'Friday', open: '09:00', close: '18:00' },
      { day: 'Saturday', open: '09:00', close: '14:00' },
      { day: 'Sunday', open: null, close: null },
    ],
    holidays: ['Poya Days', 'National Holidays'],
  },

  office: {
    name: 'LankaCommerce Cloud (Pvt) Ltd',
    street: '123 Galle Road',
    city: 'Colombo',
    district: 'Colombo',
    province: 'Western',
    postalCode: '00300',
    country: 'Sri Lanka',
  },

  supportCategories: [
    'Order Issues',
    'Returns & Refunds',
    'Shipping & Delivery',
    'Payment Issues',
    'Account & Login',
    'Product Inquiry',
    'General Inquiry',
  ],
} as const;
