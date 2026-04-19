'use client';

import { useCallback, useEffect, useState } from 'react';

import { PageLayout } from '@/components/storefront/cms/Layout';
import { getBlogCategories, getBlogPosts } from '@/services/storefront/cmsService';
import type { BlogCategory, BlogPost, PaginationMeta } from '@/types/storefront/cms.types';

import { BlogCategories } from './BlogCategories';
import { BlogGrid } from './BlogGrid';
import { BlogHeader } from './BlogHeader';
import { BlogPagination } from './BlogPagination';

export function BlogListPage() {
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [categories, setCategories] = useState<BlogCategory[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState<PaginationMeta>({
    page: 1,
    limit: 6,
    total: 0,
    pages: 0,
  });
  const [loading, setLoading] = useState(true);

  const fetchPosts = useCallback(async (category: string, p: number) => {
    setLoading(true);
    try {
      const res = await getBlogPosts({
        page: p,
        category: category || undefined,
      });
      setPosts(res.data);
      setPagination(res.pagination);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void getBlogCategories().then(setCategories);
  }, []);

  useEffect(() => {
    void fetchPosts(selectedCategory, page);
  }, [selectedCategory, page, fetchPosts]);

  const handleCategorySelect = (slug: string) => {
    setSelectedCategory(slug);
    setPage(1);
  };

  return (
    <PageLayout>
      <BlogHeader />
      <div className="container mx-auto px-4 pb-12 space-y-8">
        <BlogCategories
          categories={categories}
          selected={selectedCategory}
          onSelect={handleCategorySelect}
        />
        {loading ? (
          <div className="text-center py-12 text-muted-foreground">
            Loading posts...
          </div>
        ) : (
          <>
            <BlogGrid posts={posts} />
            <BlogPagination
              currentPage={pagination.page}
              totalPages={pagination.pages}
              onPageChange={setPage}
            />
          </>
        )}
      </div>
    </PageLayout>
  );
}
