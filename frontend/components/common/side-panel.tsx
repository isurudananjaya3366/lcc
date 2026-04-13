'use client';

import * as React from 'react';
import { Loader2 } from 'lucide-react';

import { cn } from '@/lib/utils';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';

export interface SidePanelProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  side?: 'left' | 'right';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  footer?: React.ReactNode;
  showClose?: boolean;
  isLoading?: boolean;
  className?: string;
}

const sizeMap = {
  sm: 'sm:max-w-[400px]',
  md: 'sm:max-w-[500px]',
  lg: 'sm:max-w-[600px]',
  xl: 'sm:max-w-[800px]',
} as const;

export interface SidePanelSectionProps {
  title: string;
  children: React.ReactNode;
  collapsible?: boolean;
  defaultOpen?: boolean;
  icon?: React.ReactNode;
}

function SidePanelSection({
  title,
  children,
  collapsible = false,
  defaultOpen = true,
  icon,
}: SidePanelSectionProps) {
  const [open, setOpen] = React.useState(defaultOpen);

  return (
    <div className="border-b py-4 last:border-b-0">
      <button
        type="button"
        onClick={() => collapsible && setOpen(!open)}
        className={cn(
          'flex w-full items-center gap-2 text-sm font-semibold',
          collapsible && 'cursor-pointer hover:text-foreground/80'
        )}
        disabled={!collapsible}
      >
        {icon}
        {title}
        {collapsible && (
          <span className="ml-auto text-muted-foreground">
            {open ? '−' : '+'}
          </span>
        )}
      </button>
      {open && <div className="mt-3">{children}</div>}
    </div>
  );
}

function SidePanel({
  open,
  onOpenChange,
  title,
  description,
  children,
  side = 'right',
  size = 'md',
  footer,
  isLoading = false,
  className,
}: SidePanelProps) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side={side}
        className={cn(
          'flex flex-col overflow-hidden',
          sizeMap[size],
          className
        )}
      >
        <SheetHeader className="shrink-0">
          <SheetTitle>{title}</SheetTitle>
          {description && (
            <SheetDescription>{description}</SheetDescription>
          )}
        </SheetHeader>

        <div className="flex-1 overflow-y-auto py-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : (
            children
          )}
        </div>

        {footer && (
          <SheetFooter className="shrink-0 border-t pt-4">
            {footer}
          </SheetFooter>
        )}
      </SheetContent>
    </Sheet>
  );
}

export { SidePanel, SidePanelSection };
