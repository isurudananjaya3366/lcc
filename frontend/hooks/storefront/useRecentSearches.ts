'use client';

import { useState, useEffect, useCallback } from 'react';

const STORAGE_KEY = 'lcc-recent-searches';
const MAX_ITEMS = 10;

function getStoredSearches(): string[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function persist(searches: string[]) {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(searches));
  } catch {
    // storage full or unavailable
  }
}

export function useRecentSearches() {
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  useEffect(() => {
    setRecentSearches(getStoredSearches());
  }, []);

  const addSearch = useCallback((query: string) => {
    const trimmed = query.trim();
    if (!trimmed) return;
    setRecentSearches((prev) => {
      const filtered = prev.filter((s) => s.toLowerCase() !== trimmed.toLowerCase());
      const next = [trimmed, ...filtered].slice(0, MAX_ITEMS);
      persist(next);
      return next;
    });
  }, []);

  const removeSearch = useCallback((query: string) => {
    setRecentSearches((prev) => {
      const next = prev.filter((s) => s !== query);
      persist(next);
      return next;
    });
  }, []);

  const clearAll = useCallback(() => {
    setRecentSearches([]);
    persist([]);
  }, []);

  return { recentSearches, addSearch, removeSearch, clearAll };
}
