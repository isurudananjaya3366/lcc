'use client';

import { ReactNode } from 'react';
import { SettingsSidebar } from './SettingsSidebar';

interface SettingsLayoutProps {
  children: ReactNode;
}

export function SettingsLayout({ children }: SettingsLayoutProps) {
  return (
    <div className="flex min-h-[calc(100vh-4rem)] gap-8">
      <aside className="hidden w-64 shrink-0 border-r pr-6 lg:block">
        <div className="sticky top-20">
          <h2 className="mb-6 text-lg font-semibold">Settings</h2>
          <SettingsSidebar />
        </div>
      </aside>
      <main className="flex-1 pb-10">{children}</main>
    </div>
  );
}
