import Link from 'next/link';
import { cn } from '@/lib/utils';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from '@/components/ui/card';

interface RelatedPage {
  title: string;
  slug: string;
  excerpt?: string;
}

interface RelatedPagesProps {
  pages: RelatedPage[];
  className?: string;
}

export function RelatedPages({ pages, className }: RelatedPagesProps) {
  if (pages.length === 0) return null;

  return (
    <section className={cn('mt-12', className)}>
      <h2 className="text-2xl font-bold tracking-tight mb-4">Related Pages</h2>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {pages.map((page) => (
          <Link key={page.slug} href={`/${page.slug}`}>
            <Card className="h-full hover:shadow-md transition-shadow">
              <CardHeader>
                <CardTitle className="text-lg">{page.title}</CardTitle>
              </CardHeader>
              {page.excerpt && (
                <CardContent>
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {page.excerpt}
                  </p>
                </CardContent>
              )}
            </Card>
          </Link>
        ))}
      </div>
    </section>
  );
}
