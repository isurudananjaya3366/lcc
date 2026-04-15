'use client';

import { Phone, Mail, Users, FileText } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';

interface Communication {
  id: string;
  type: 'phone' | 'email' | 'meeting' | 'note';
  subject: string;
  date: string;
  notes?: string;
  createdBy?: string;
}

interface CommunicationTimelineProps {
  communications: Communication[];
  isLoading?: boolean;
}

const typeConfig = {
  phone: { icon: Phone, color: 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300' },
  email: { icon: Mail, color: 'bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-300' },
  meeting: {
    icon: Users,
    color: 'bg-purple-100 text-purple-600 dark:bg-purple-900 dark:text-purple-300',
  },
  note: {
    icon: FileText,
    color: 'bg-orange-100 text-orange-600 dark:bg-orange-900 dark:text-orange-300',
  },
};

export function CommunicationTimeline({ communications, isLoading }: CommunicationTimelineProps) {
  if (isLoading) {
    return (
      <div className="space-y-6">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="flex gap-4">
            <Skeleton className="h-10 w-10 rounded-full shrink-0" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-48" />
              <Skeleton className="h-3 w-32" />
              <Skeleton className="h-3 w-full" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (communications.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <Mail className="h-10 w-10 text-muted-foreground mb-3" />
        <p className="text-sm text-muted-foreground">No communication history yet.</p>
      </div>
    );
  }

  return (
    <div className="relative">
      <div className="absolute left-5 top-0 bottom-0 w-px bg-border" />
      <div className="space-y-6">
        {communications.map((comm) => {
          const config = typeConfig[comm.type] || typeConfig.note;
          const Icon = config.icon;
          return (
            <div key={comm.id} className="relative flex gap-4 pl-0">
              <div
                className={`flex items-center justify-center h-10 w-10 rounded-full shrink-0 z-10 ${config.color}`}
              >
                <Icon className="h-4 w-4" />
              </div>
              <div className="flex-1 min-w-0 pb-2">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium">{comm.subject}</p>
                  <span className="text-xs text-muted-foreground shrink-0 ml-2">
                    {new Date(comm.date).toLocaleDateString('en-LK', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })}
                  </span>
                </div>
                {comm.createdBy && (
                  <p className="text-xs text-muted-foreground">by {comm.createdBy}</p>
                )}
                {comm.notes && (
                  <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{comm.notes}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
