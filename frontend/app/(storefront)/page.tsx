import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: "LankaCommerce Store - Sri Lanka's Premier Online Shopping",
  description:
    'Shop quality products with seamless checkout. Free delivery across Sri Lanka on orders over Rs. 5,000. Browse electronics, fashion, home goods and more.',
};

/**
 * Store homepage — primary landing page for customer visitors.
 * Sections will be implemented in SubPhase-02+.
 */
export default function HomePage() {
  return (
    <div className="space-y-12">
      {/* Hero Banner */}
      <section className="bg-gradient-to-r from-primary/10 to-primary/5">
        <div className="container mx-auto px-4 py-16 md:py-24 text-center">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
            Welcome to LankaCommerce
          </h1>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Discover quality products at unbeatable prices. Free delivery across Sri Lanka on orders
            over Rs. 5,000.
          </p>
          <div className="mt-8 flex gap-4 justify-center">
            <a
              href="/products"
              className="inline-flex items-center justify-center rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            >
              Shop Now
            </a>
            <a
              href="/products"
              className="inline-flex items-center justify-center rounded-md border px-6 py-3 text-sm font-medium hover:bg-accent"
            >
              Browse Categories
            </a>
          </div>
        </div>
      </section>

      {/* Featured Products — placeholder */}
      <section className="container mx-auto px-4">
        <h2 className="text-2xl font-semibold mb-6">Featured Products</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="rounded-lg border bg-white p-4 space-y-3">
              <div className="aspect-square rounded-md bg-muted" />
              <div className="h-4 w-3/4 rounded bg-muted" />
              <div className="h-4 w-1/2 rounded bg-muted" />
            </div>
          ))}
        </div>
      </section>

      {/* Shop by Category — placeholder */}
      <section className="container mx-auto px-4">
        <h2 className="text-2xl font-semibold mb-6">Shop by Category</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {['Electronics', 'Fashion', 'Home & Kitchen', 'Health & Beauty'].map((cat) => (
            <a
              key={cat}
              href="/products"
              className="rounded-lg border bg-white p-6 text-center hover:border-primary transition-colors"
            >
              <div className="h-16 w-16 mx-auto rounded-full bg-primary/10 mb-3" />
              <span className="text-sm font-medium">{cat}</span>
            </a>
          ))}
        </div>
      </section>

      {/* Trust Badges */}
      <section className="container mx-auto px-4 pb-12">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-center">
          <div className="p-6">
            <div className="text-2xl mb-2">🚚</div>
            <h3 className="font-medium">Free Delivery</h3>
            <p className="text-sm text-muted-foreground">On orders over Rs. 5,000</p>
          </div>
          <div className="p-6">
            <div className="text-2xl mb-2">🔄</div>
            <h3 className="font-medium">Easy Returns</h3>
            <p className="text-sm text-muted-foreground">14-day return policy</p>
          </div>
          <div className="p-6">
            <div className="text-2xl mb-2">🛡️</div>
            <h3 className="font-medium">Secure Checkout</h3>
            <p className="text-sm text-muted-foreground">SSL encrypted payments</p>
          </div>
        </div>
      </section>
    </div>
  );
}
