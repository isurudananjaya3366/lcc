'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Lock, User, Settings } from 'lucide-react';
import { AddNoteForm } from './AddNoteForm';
import type { OrderNote } from '@/types/sales';

interface OrderNotesProps {
  notes: OrderNote[];
  orderId: string;
  onAddNote?: (data: { type: 'internal' | 'customer'; content: string }) => Promise<void>;
  isLoading?: boolean;
}

function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString('en-LK', { month: 'short', day: 'numeric' });
}

export function OrderNotes({ notes, orderId, onAddNote, isLoading }: OrderNotesProps) {
  const [filter, setFilter] = useState<'all' | 'internal' | 'customer'>('all');

  const filteredNotes = notes.filter((note) => {
    if (filter === 'all') return true;
    if (filter === 'internal') return !note.isCustomerVisible;
    return note.isCustomerVisible;
  });

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Notes</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="h-16 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">Notes</CardTitle>
          <div className="flex gap-1">
            {(['all', 'internal', 'customer'] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`rounded px-2 py-1 text-xs capitalize ${
                  filter === f
                    ? 'bg-gray-200 font-medium dark:bg-gray-700'
                    : 'text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Notes List */}
        <div className="max-h-[400px] space-y-3 overflow-y-auto">
          {filteredNotes.length === 0 ? (
            <p className="py-4 text-center text-sm text-gray-500">No notes yet</p>
          ) : (
            filteredNotes.map((note) => (
              <div key={note.id} className="rounded-md border p-3">
                <div className="mb-1 flex items-center gap-2">
                  {note.isCustomerVisible ? (
                    <Badge variant="secondary" className="bg-blue-100 text-blue-800 text-xs">
                      <User className="mr-1 h-3 w-3" />
                      Customer
                    </Badge>
                  ) : (
                    <Badge variant="secondary" className="bg-gray-100 text-gray-800 text-xs">
                      <Lock className="mr-1 h-3 w-3" />
                      Internal
                    </Badge>
                  )}
                </div>
                <p className="text-sm text-gray-700 dark:text-gray-300">{note.note}</p>
                <p className="mt-1 text-xs text-gray-400">
                  by {note.createdBy} · {formatRelativeTime(note.createdAt)}
                </p>
              </div>
            ))
          )}
        </div>

        {/* Add Note Form */}
        {onAddNote && <AddNoteForm orderId={orderId} onSubmit={onAddNote} />}
      </CardContent>
    </Card>
  );
}
