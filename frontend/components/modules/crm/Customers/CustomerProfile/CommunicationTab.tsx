'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { customerKeys } from '@/lib/queryKeys';
import { apiClient } from '@/services/api/apiClient';
import { CommunicationTimeline } from './CommunicationTimeline';
import { AddCommunicationForm } from './AddCommunicationForm';

interface CommunicationTabProps {
  customerId: string;
}

type CommType = 'all' | 'phone' | 'email' | 'meeting' | 'note';

const CUSTOMER_ENDPOINT = '/api/v1/customers';

const typeFilters: { value: CommType; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'phone', label: 'Phone Calls' },
  { value: 'email', label: 'Emails' },
  { value: 'meeting', label: 'Meetings' },
  { value: 'note', label: 'Notes' },
];

export function CommunicationTab({ customerId }: CommunicationTabProps) {
  const [filter, setFilter] = useState<CommType>('all');
  const [showAddForm, setShowAddForm] = useState(false);

  const { data, isLoading, refetch } = useQuery({
    queryKey: [...customerKeys.detail(customerId), 'communications'],
    queryFn: async () => {
      const response = await apiClient.get(`${CUSTOMER_ENDPOINT}/${customerId}/communications/`);
      return response.data;
    },
    enabled: !!customerId,
  });

  const communications = (data?.data ?? []) as Array<{
    id: string;
    type: 'phone' | 'email' | 'meeting' | 'note';
    subject: string;
    date: string;
    notes?: string;
    createdBy?: string;
  }>;

  const filtered =
    filter === 'all' ? communications : communications.filter((c) => c.type === filter);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {typeFilters.map((tf) => (
            <Button
              key={tf.value}
              variant={filter === tf.value ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter(tf.value)}
            >
              {tf.label}
            </Button>
          ))}
        </div>
        <Button size="sm" onClick={() => setShowAddForm(true)}>
          <Plus className="h-4 w-4 mr-1" />
          Add Entry
        </Button>
      </div>

      <CommunicationTimeline communications={filtered} isLoading={isLoading} />

      <AddCommunicationForm
        customerId={customerId}
        isOpen={showAddForm}
        onClose={() => setShowAddForm(false)}
        onSuccess={() => refetch()}
      />
    </div>
  );
}
