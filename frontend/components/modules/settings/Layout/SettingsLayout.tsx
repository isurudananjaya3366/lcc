'use client';

import { ReactNode, useState } from 'react';
import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';
import { SettingsSidebar } from './SettingsSidebar';

interface SettingsLayoutProps {
  children: ReactNode;
}

export function SettingsLayout({ children }: SettingsLayoutProps) {
  const [open, setOpen] = useState(false);

  return (
    <div className="flex min-h-[calc(100vh-4rem)] gap-8">
      {/* Desktop sidebar */}
      <aside className="hidden w-64 shrink-0 border-r pr-6 lg:block">
        <div className="sticky top-20">
          <h2 className="mb-6 text-lg font-semibold">Settings</h2>
          <SettingsSidebar />
        </div>
      </aside>

      {/* Mobile sidebar drawer */}
      <div className="lg:hidden fixed bottom-4 right-4 z-50">
        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger asChild>
            <Button size="icon" className="rounded-full shadow-lg">
              <Menu className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-72 p-6">
            <SheetHeader>
              <SheetTitle>Settings</SheetTitle>
            </SheetHeader>
            <div className="mt-4">
              <SettingsSidebar onNavigate={() => setOpen(false)} />
            </div>
          </SheetContent>
        </Sheet>
      </div>

      <main className="flex-1 pb-10">{children}</main>
    </div>
  );
}
