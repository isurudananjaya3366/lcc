import type {
  CMSPage,
  PagesResponse,
  BlogAuthor,
  BlogPost,
  BlogPostsResponse,
  BlogCategory,
  FAQItem,
  ContactFormData,
  ShippingRate,
} from '@/types/storefront/cms.types';

const MOCK_PAGES: Record<string, CMSPage> = {
  about: {
    id: '1',
    slug: 'about',
    title: 'About Us',
    content: '<p>About us content placeholder.</p>',
    status: 'published',
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-01-01T00:00:00Z',
    publishedAt: '2025-01-01T00:00:00Z',
  },
  terms: {
    id: '2',
    slug: 'terms',
    title: 'Terms & Conditions',
    content:
      '<h2>Acceptance of Terms</h2><p>By accessing and using this website, you accept and agree to be bound by the terms and provision of this agreement. If you do not agree to abide by these terms, please do not use this service.</p>' +
      '<h2>Use License</h2><p>Permission is granted to temporarily download one copy of the materials on our website for personal, non-commercial transitory viewing only. This is the grant of a licence, not a transfer of title.</p>' +
      '<h2>Account Responsibilities</h2><p>You are responsible for maintaining the confidentiality of your account and password, and for restricting access to your computer. You agree to accept responsibility for all activities that occur under your account.</p>' +
      '<h2>Payment Terms</h2><p>All prices are listed in Sri Lankan Rupees (LKR). We accept Visa, Mastercard, bank transfers, and cash on delivery. Payment must be received in full before order dispatch unless COD is selected.</p>' +
      '<h2>Shipping &amp; Delivery</h2><p>We deliver across Sri Lanka. Delivery times vary by location. Standard delivery within Colombo takes 1–2 business days. Other provinces may take 3–5 business days. See our Shipping Information page for full details.</p>' +
      '<h2>Returns &amp; Refunds</h2><p>Items may be returned within 14 days of delivery provided they are unused, in original packaging, and accompanied by proof of purchase. Refunds are processed within 5–7 business days to the original payment method.</p>' +
      '<h2>Limitation of Liability</h2><p>We shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising out of your access to or use of this website or any products purchased through it.</p>' +
      '<h2>Governing Law</h2><p>These terms and conditions are governed by and construed in accordance with the laws of the Democratic Socialist Republic of Sri Lanka. Any disputes shall be subject to the exclusive jurisdiction of the courts of Sri Lanka.</p>',
    status: 'published',
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2026-01-01T00:00:00Z',
    publishedAt: '2025-01-01T00:00:00Z',
  },
  privacy: {
    id: '3',
    slug: 'privacy',
    title: 'Privacy Policy',
    content:
      '<h2>Information We Collect</h2><p>We collect personal information that you provide directly, including your name, email address, phone number, delivery address, and payment details when you place an order or create an account.</p>' +
      '<h2>How We Use Information</h2><p>Your information is used for order processing, customer service communications, marketing (with your consent), improving our website experience, and complying with legal obligations.</p>' +
      '<h2>Data Protection</h2><p>We implement SSL encryption across our website, use secure payment processing through certified gateways, and store your data on protected servers with restricted access controls.</p>' +
      '<h2>Cookies</h2><p>We use cookies to maintain your session, remember your preferences, analyse site traffic, and personalise your shopping experience. You can manage cookie settings through your browser preferences.</p>' +
      '<h2>Third-Party Services</h2><p>We share necessary data with trusted third parties including payment processors, delivery partners, and analytics providers. These parties are bound by confidentiality agreements and data protection regulations.</p>' +
      '<h2>Your Rights</h2><p>You have the right to access, correct, or delete your personal data at any time. You may also opt out of marketing communications and request a copy of the information we hold about you.</p>' +
      '<h2>Contact Us</h2><p>For privacy-related concerns, please contact our data protection team at privacy@store.lk or write to us at our registered office in Colombo 03, Sri Lanka.</p>',
    status: 'published',
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2026-01-01T00:00:00Z',
    publishedAt: '2025-01-01T00:00:00Z',
  },
  returns: {
    id: '4',
    slug: 'returns',
    title: 'Return Policy',
    content:
      '<h2>Return Eligibility</h2><p>Items are eligible for return within 14 days of delivery. Products must be unused, in their original packaging, and accompanied by the original receipt or proof of purchase. Items must be in the same condition as received.</p>' +
      '<h2>Return Process</h2><p>To initiate a return: 1) Contact our support team via email or phone. 2) Receive a return authorisation and shipping label. 3) Pack and ship the item securely. 4) Refund is processed once the item is received and inspected.</p>' +
      '<h2>Refund Policy</h2><p>Refunds are processed within 5–7 business days after we receive and inspect the returned item. The refund will be credited to the original payment method. Shipping costs are non-refundable unless the return is due to our error.</p>' +
      '<h2>Exchanges</h2><p>Exchanges are subject to product availability. If the desired replacement is in stock, we will ship it at no additional delivery charge. If the replacement has a different price, the difference will be charged or refunded accordingly.</p>' +
      '<h2>Non-Returnable Items</h2><p>The following items cannot be returned: perishable goods, personal care and hygiene products, custom or personalised items, downloadable software, and items marked as final sale.</p>' +
      '<h2>Contact</h2><p>For returns and exchanges, please contact us at returns@store.lk or call +94 11 234 5678. Our returns team is available Monday to Friday, 9:00 AM to 5:00 PM.</p>',
    status: 'published',
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2026-01-01T00:00:00Z',
    publishedAt: '2025-01-01T00:00:00Z',
  },
  shipping: {
    id: '5',
    slug: 'shipping',
    title: 'Shipping Information',
    content:
      '<h2>Delivery Areas</h2><p>We currently deliver across all provinces of Sri Lanka. Delivery times and rates vary depending on your location. Colombo and Western Province enjoy the fastest delivery times.</p>' +
      '<h2>Shipping Rates</h2><p>Shipping rates are calculated based on your delivery zone. Free shipping is available on qualifying orders. See the rates table below for detailed pricing information.</p>' +
      '<h2>Processing Time</h2><p>Orders are processed within 24 hours of placement on business days. Orders placed on weekends or public holidays will be processed on the next business day. You will receive a confirmation email once your order is dispatched.</p>' +
      '<h2>Tracking</h2><p>A tracking number is provided via email and SMS once your order is shipped. You can track your delivery status through our website or the courier partner\'s tracking page.</p>',
    status: 'published',
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2026-01-01T00:00:00Z',
    publishedAt: '2025-01-01T00:00:00Z',
  },
};

export async function getPageBySlug(slug: string): Promise<CMSPage | null> {
  return MOCK_PAGES[slug] ?? null;
}

export async function getPages(): Promise<PagesResponse> {
  const pages = Object.values(MOCK_PAGES);
  return {
    data: pages,
    pagination: { page: 1, limit: 10, total: pages.length, pages: 1 },
  };
}

const mockBlogAuthor: BlogAuthor = {
  id: 'author-1',
  name: 'Nimali Fernando',
  avatar: '/images/team/nimali.jpg',
  bio: 'Content writer and Sri Lankan lifestyle enthusiast.',
};

const mockBlogCategories: BlogCategory[] = [
  { id: 'cat-1', name: 'Lifestyle', slug: 'lifestyle', description: 'Sri Lankan lifestyle tips', postCount: 3 },
  { id: 'cat-2', name: 'Products', slug: 'products', description: 'Product guides and reviews', postCount: 2 },
  { id: 'cat-3', name: 'News', slug: 'news', description: 'Company updates and news', postCount: 1 },
];

const mockBlogPosts: BlogPost[] = [
  {
    id: 'post-1', slug: 'ceylon-cinnamon-guide', title: 'The Complete Guide to Ceylon Cinnamon',
    content: '<p>Ceylon cinnamon, also known as "true cinnamon", is native to Sri Lanka...</p><p>Unlike cassia cinnamon, Ceylon cinnamon has a delicate, sweet flavor...</p><h2>Health Benefits</h2><p>Rich in antioxidants and anti-inflammatory properties...</p><h2>How to Use</h2><p>Add to your morning tea, smoothies, or baked goods...</p>',
    excerpt: 'Discover the rich history and health benefits of authentic Ceylon cinnamon from Sri Lanka.',
    featuredImage: '/images/blog/ceylon-cinnamon.jpg',
    author: mockBlogAuthor,
    category: mockBlogCategories[0]!,
    tags: [{ id: 'tag-1', name: 'Cinnamon', slug: 'cinnamon' }, { id: 'tag-2', name: 'Spices', slug: 'spices' }],
    readingTime: 5, status: 'published',
    createdAt: '2026-03-15T10:00:00Z', updatedAt: '2026-03-15T10:00:00Z', publishedAt: '2026-03-15T10:00:00Z',
  },
  {
    id: 'post-2', slug: 'traditional-sri-lankan-crafts', title: 'Traditional Sri Lankan Crafts You Should Know',
    content: '<p>Sri Lanka has a rich tradition of handcrafts dating back thousands of years...</p><h2>Batik Art</h2><p>The ancient art of wax-resist dyeing...</p><h2>Lacquerwork</h2><p>Colorful lacquered wooden items from Matale...</p>',
    excerpt: 'Explore the beautiful world of traditional Sri Lankan handicrafts and their cultural significance.',
    featuredImage: '/images/blog/sri-lankan-crafts.jpg',
    author: mockBlogAuthor,
    category: mockBlogCategories[0]!,
    tags: [{ id: 'tag-3', name: 'Crafts', slug: 'crafts' }, { id: 'tag-4', name: 'Culture', slug: 'culture' }],
    readingTime: 7, status: 'published',
    createdAt: '2026-03-20T10:00:00Z', updatedAt: '2026-03-20T10:00:00Z', publishedAt: '2026-03-20T10:00:00Z',
  },
  {
    id: 'post-3', slug: 'top-10-gift-ideas', title: 'Top 10 Gift Ideas from Sri Lanka',
    content: '<p>Looking for the perfect Sri Lankan gift? Here are our top picks...</p><h2>1. Ceylon Tea Collection</h2><p>A premium selection of teas from the highlands...</p><h2>2. Cinnamon Gift Set</h2><p>Handpicked Ceylon cinnamon...</p>',
    excerpt: 'Find the perfect gift with our curated list of authentic Sri Lankan products.',
    featuredImage: '/images/blog/gift-ideas.jpg',
    author: mockBlogAuthor,
    category: mockBlogCategories[1]!,
    tags: [{ id: 'tag-5', name: 'Gifts', slug: 'gifts' }, { id: 'tag-6', name: 'Guide', slug: 'guide' }],
    readingTime: 4, status: 'published',
    createdAt: '2026-04-01T10:00:00Z', updatedAt: '2026-04-01T10:00:00Z', publishedAt: '2026-04-01T10:00:00Z',
  },
  {
    id: 'post-4', slug: 'sustainable-packaging', title: 'Our Commitment to Sustainable Packaging',
    content: '<p>We are proud to announce our transition to 100% eco-friendly packaging...</p><h2>Why It Matters</h2><p>Sri Lanka`s beautiful environment deserves protection...</p>',
    excerpt: 'Learn about our journey towards sustainable, eco-friendly packaging for all products.',
    featuredImage: '/images/blog/sustainable.jpg',
    author: { ...mockBlogAuthor, id: 'author-2', name: 'Rajitha Silva' },
    category: mockBlogCategories[2]!,
    tags: [{ id: 'tag-7', name: 'Sustainability', slug: 'sustainability' }],
    readingTime: 3, status: 'published',
    createdAt: '2026-04-10T10:00:00Z', updatedAt: '2026-04-10T10:00:00Z', publishedAt: '2026-04-10T10:00:00Z',
  },
];

const BLOG_PAGE_SIZE = 6;

export async function getBlogPosts(params?: {
  page?: number;
  category?: string;
}): Promise<BlogPostsResponse> {
  const page = params?.page ?? 1;
  const category = params?.category;

  let filtered = mockBlogPosts;
  if (category) {
    filtered = mockBlogPosts.filter((p) => p.category.slug === category);
  }

  const total = filtered.length;
  const pages = Math.ceil(total / BLOG_PAGE_SIZE);
  const start = (page - 1) * BLOG_PAGE_SIZE;
  const data = filtered.slice(start, start + BLOG_PAGE_SIZE);

  return {
    data,
    pagination: { page, limit: BLOG_PAGE_SIZE, total, pages },
  };
}

export async function getBlogPostBySlug(slug: string): Promise<BlogPost | null> {
  return mockBlogPosts.find((p) => p.slug === slug) ?? null;
}

export async function getBlogCategories(): Promise<BlogCategory[]> {
  return mockBlogCategories;
}

// Mock FAQ data
const mockFAQItems: FAQItem[] = [
  { id: 'faq-1', question: 'What payment methods do you accept?', answer: 'We accept Visa, Mastercard, bank transfers, and cash on delivery across Sri Lanka.', category: 'Payments', order: 1 },
  { id: 'faq-2', question: 'How long does delivery take?', answer: 'Standard delivery within Colombo takes 1-2 business days. Other areas in Sri Lanka take 3-5 business days.', category: 'Shipping', order: 2 },
  { id: 'faq-3', question: 'What is your return policy?', answer: 'We offer a 14-day return policy for unused items in original packaging. Contact us to initiate a return.', category: 'Returns', order: 3 },
  { id: 'faq-4', question: 'Do you offer international shipping?', answer: 'Currently, we only ship within Sri Lanka. International shipping is coming soon.', category: 'Shipping', order: 4 },
  { id: 'faq-5', question: 'How can I track my order?', answer: 'Once your order is shipped, you will receive a tracking number via email and SMS to track your delivery.', category: 'Orders', order: 5 },
  { id: 'faq-6', question: 'Can I change or cancel my order?', answer: 'You can modify or cancel your order within 1 hour of placing it. Contact our support team for assistance.', category: 'Orders', order: 6 },
  { id: 'faq-7', question: 'Do you have a physical store?', answer: 'Yes, our main store is located in Colombo 03. Visit us during business hours: Mon-Sat 9AM-6PM.', category: 'General', order: 7 },
  { id: 'faq-8', question: 'How do I contact customer support?', answer: 'You can reach us via WhatsApp at +94 77 123 4567, email at support@store.lk, or through the contact form on our website.', category: 'General', order: 8 },
];

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export async function getFAQItems(): Promise<FAQItem[]> {
  return mockFAQItems;
}

export async function submitContactForm(data: ContactFormData): Promise<void> {
  void data;
  await delay(800);
}

const mockShippingRates: ShippingRate[] = [
  { id: 'sr-1', zone: 'Colombo', method: 'Standard Delivery', minDays: 1, maxDays: 2, price: 350, freeAbove: 5000 },
  { id: 'sr-2', zone: 'Colombo', method: 'Express Delivery', minDays: 0, maxDays: 1, price: 600 },
  { id: 'sr-3', zone: 'Western Province', method: 'Standard Delivery', minDays: 2, maxDays: 3, price: 450, freeAbove: 7500 },
  { id: 'sr-4', zone: 'Other Provinces', method: 'Standard Delivery', minDays: 3, maxDays: 5, price: 550, freeAbove: 10000 },
  { id: 'sr-5', zone: 'Other Provinces', method: 'Express Delivery', minDays: 2, maxDays: 3, price: 900 },
];

export async function getShippingRates(): Promise<ShippingRate[]> {
  return mockShippingRates;
}
