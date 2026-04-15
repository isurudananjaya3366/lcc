import { getStoreClient, type PaginatedResponse } from '../client';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface SearchFacetOption {
  value: string;
  label: string;
  count: number;
}

export interface SearchFacet {
  field_name: string;
  display_name: string;
  options: SearchFacetOption[];
}

export interface SearchSuggestion {
  text: string;
  type: 'product' | 'category' | 'brand';
  url: string;
  highlight: string;
}

export interface SearchFilters {
  categories?: string[];
  brands?: string[];
  price_min?: number;
  price_max?: number;
  rating_min?: number;
  in_stock_only?: boolean;
  on_sale_only?: boolean;
  sort_by?: 'relevance' | 'price_asc' | 'price_desc' | 'newest' | 'rating' | 'popularity';
}

export interface SearchResult<T = unknown> {
  items: T[];
  total_count: number;
  page: number;
  page_size: number;
  has_more: boolean;
  facets: SearchFacet[];
  query: string;
  suggestions: string[];
}

export interface SearchHistoryItem {
  id: string;
  query: string;
  filters: SearchFilters;
  timestamp: string;
  result_count: number;
}

// ─── Guest Search History (localStorage) ────────────────────────────────────

const SEARCH_HISTORY_KEY = 'store_search_history';
const MAX_HISTORY_ITEMS = 20;

function getLocalHistory(): SearchHistoryItem[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = localStorage.getItem(SEARCH_HISTORY_KEY);
    if (raw) return JSON.parse(raw);
  } catch {
    // Corrupted data
  }
  return [];
}

function saveLocalHistory(history: SearchHistoryItem[]): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(history.slice(0, MAX_HISTORY_ITEMS)));
}

function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;
  return !!localStorage.getItem('store-auth-token');
}

// ─── Validation Utilities ───────────────────────────────────────────────────

export function validateSearchQuery(query: string): boolean {
  return query.trim().length >= 3;
}

export function highlightMatches(text: string, query: string): string {
  if (!query) return text;
  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return text.replace(new RegExp(`(${escaped})`, 'gi'), '<mark>$1</mark>');
}

export function getPriceRangeFacets(): { label: string; min: number; max: number }[] {
  return [
    { label: 'Under ₨ 25,000', min: 0, max: 25000 },
    { label: '₨ 25,000 - 50,000', min: 25000, max: 50000 },
    { label: '₨ 50,000 - 100,000', min: 50000, max: 100000 },
    { label: '₨ 100,000 - 150,000', min: 100000, max: 150000 },
    { label: 'Over ₨ 150,000', min: 150000, max: Infinity },
  ];
}

// ─── API Functions ──────────────────────────────────────────────────────────

export async function searchAll(
  query: string,
  filters?: SearchFilters,
  page?: number,
  limit?: number
): Promise<SearchResult> {
  const { data } = await getStoreClient().get('/search/', {
    params: { q: query, ...filters, page, page_size: limit },
  });
  return data;
}

export async function searchProducts(
  query: string,
  filters?: SearchFilters,
  page?: number,
  limit?: number
): Promise<SearchResult> {
  const { data } = await getStoreClient().get('/search/products/', {
    params: { q: query, ...filters, page, page_size: limit },
  });
  return data;
}

export async function searchCategories(
  query: string,
  page?: number,
  limit?: number
): Promise<SearchResult> {
  const { data } = await getStoreClient().get('/search/categories/', {
    params: { q: query, page, page_size: limit },
  });
  return data;
}

export async function getFacets(): Promise<SearchFacet[]> {
  const { data } = await getStoreClient().get('/search/facets/');
  return data;
}

export async function getSearchSuggestions(
  query: string,
  limit?: number,
  types?: ('product' | 'category' | 'brand')[]
): Promise<SearchSuggestion[]> {
  const { data } = await getStoreClient().get('/search/suggestions/', {
    params: { q: query, limit, types: types?.join(',') },
  });
  return data;
}

export async function saveSearchHistory(
  query: string,
  filters: SearchFilters,
  resultCount: number
): Promise<void> {
  const historyItem: SearchHistoryItem = {
    id: crypto.randomUUID(),
    query,
    filters,
    timestamp: new Date().toISOString(),
    result_count: resultCount,
  };

  if (isAuthenticated()) {
    await getStoreClient().post('/customer/search-history/', historyItem);
  } else {
    const history = getLocalHistory();
    history.unshift(historyItem);
    saveLocalHistory(history);
  }
}

export async function getSearchHistory(): Promise<SearchHistoryItem[]> {
  if (!isAuthenticated()) return getLocalHistory();

  const { data } = await getStoreClient().get('/customer/search-history/');
  return data.results ?? data;
}

export async function clearSearchHistory(searchId?: string): Promise<void> {
  if (!isAuthenticated()) {
    if (searchId) {
      const history = getLocalHistory().filter((h) => h.id !== searchId);
      saveLocalHistory(history);
    } else {
      saveLocalHistory([]);
    }
    return;
  }

  if (searchId) {
    await getStoreClient().delete(`/customer/search-history/${searchId}/`);
  } else {
    await getStoreClient().delete('/customer/search-history/');
  }
}

const searchApi = {
  searchAll,
  searchProducts,
  searchCategories,
  getFacets,
  getSearchSuggestions,
  saveSearchHistory,
  getSearchHistory,
  clearSearchHistory,
  validateSearchQuery,
  highlightMatches,
  getPriceRangeFacets,
};

export default searchApi;
