'use client';

import { formatDistanceToNow } from 'date-fns';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Package,
  Edit,
  Tag,
  Image as ImageIcon,
  DollarSign,
  Archive,
  RotateCcw,
  type LucideIcon,
} from 'lucide-react';

export interface ActivityItem {
  id: string;
  type:
    | 'created'
    | 'updated'
    | 'price_changed'
    | 'stock_updated'
    | 'image_added'
    | 'archived'
    | 'restored'
    | 'tagged';
  description: string;
  user?: string;
  timestamp: string;
  details?: string;
}

interface ProductActivityTimelineProps {
  activities: ActivityItem[];
}

const activityIcons: Record<ActivityItem['type'], LucideIcon> = {
  created: Package,
  updated: Edit,
  price_changed: DollarSign,
  stock_updated: Package,
  image_added: ImageIcon,
  archived: Archive,
  restored: RotateCcw,
  tagged: Tag,
};

const activityColors: Record<ActivityItem['type'], string> = {
  created: 'bg-green-500',
  updated: 'bg-blue-500',
  price_changed: 'bg-amber-500',
  stock_updated: 'bg-purple-500',
  image_added: 'bg-indigo-500',
  archived: 'bg-gray-500',
  restored: 'bg-emerald-500',
  tagged: 'bg-pink-500',
};

export function ProductActivityTimeline({ activities }: ProductActivityTimelineProps) {
  if (activities.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-500 dark:text-gray-400">No activity recorded yet.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-3.5 top-0 bottom-0 w-px bg-gray-200 dark:bg-gray-700" />

          <div className="space-y-4">
            {activities.map((activity) => {
              const Icon = activityIcons[activity.type];
              const colorClass = activityColors[activity.type];

              return (
                <div key={activity.id} className="relative flex gap-3">
                  <div
                    className={`relative z-10 flex h-7 w-7 shrink-0 items-center justify-center rounded-full ${colorClass}`}
                  >
                    <Icon className="h-3.5 w-3.5 text-white" />
                  </div>
                  <div className="flex-1 min-w-0 pt-0.5">
                    <p className="text-sm">
                      {activity.description}
                      {activity.user && (
                        <span className="text-gray-500 dark:text-gray-400">
                          {' '}
                          by {activity.user}
                        </span>
                      )}
                    </p>
                    {activity.details && (
                      <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">
                        {activity.details}
                      </p>
                    )}
                    <p className="mt-0.5 text-xs text-gray-400 dark:text-gray-500">
                      {formatDistanceToNow(new Date(activity.timestamp), {
                        addSuffix: true,
                      })}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
