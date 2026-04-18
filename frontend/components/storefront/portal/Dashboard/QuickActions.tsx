'use client';

import Link from 'next/link';
import { ShoppingBag, MapPin, Settings, MessageCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const actions = [
  {
    label: 'Browse Products',
    href: '/products',
    icon: ShoppingBag,
    external: false,
  },
  {
    label: 'My Addresses',
    href: '/account/addresses',
    icon: MapPin,
    external: false,
  },
  {
    label: 'Account Settings',
    href: '/account/settings',
    icon: Settings,
    external: false,
  },
  {
    label: 'Need Help?',
    href: 'https://wa.me/94771234567',
    icon: MessageCircle,
    external: true,
  },
];

export function QuickActions() {
  return (
    <Card>
      <CardContent className="pt-6">
        <h3 className="text-sm font-semibold mb-3">Quick Actions</h3>
        <div className="grid grid-cols-2 gap-3">
          {actions.map(({ label, href, icon: Icon, external }) => (
            <Button
              key={label}
              variant="outline"
              className="h-auto flex flex-col items-center gap-2 py-4"
              asChild
            >
              {external ? (
                <a href={href} target="_blank" rel="noopener noreferrer">
                  <Icon className="h-5 w-5" />
                  <span className="text-xs">{label}</span>
                </a>
              ) : (
                <Link href={href}>
                  <Icon className="h-5 w-5" />
                  <span className="text-xs">{label}</span>
                </Link>
              )}
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
