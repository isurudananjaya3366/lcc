'use client';

import * as React from 'react';
import {
  LayoutDashboard,
  Package,
  Users,
  ShoppingCart,
  FileText,
  BarChart3,
  Settings,
  Calculator,
  Plus,
  RefreshCw,
  Upload,
  Download,
  UserCog,
  Palette,
  Globe,
  LogOut,
  BookOpen,
  Keyboard,
  MessageCircle,
  Bug,
  Info,
  Clock,
} from 'lucide-react';

import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from '@/components/ui/command';

interface CommandItem {
  id: string;
  label: string;
  icon?: React.ComponentType<{ className?: string }>;
  shortcut?: string;
  onSelect?: () => void;
}

interface CommandGroup {
  heading: string;
  items: CommandItem[];
}

const defaultGroups: CommandGroup[] = [
  {
    heading: 'Pages',
    items: [
      { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, shortcut: '⌘D' },
      { id: 'products', label: 'Products', icon: Package },
      { id: 'customers', label: 'Customers', icon: Users },
      { id: 'orders', label: 'Orders', icon: ShoppingCart },
      { id: 'invoices', label: 'Invoices', icon: FileText },
      { id: 'reports', label: 'Reports', icon: BarChart3 },
      { id: 'settings', label: 'Settings', icon: Settings },
      { id: 'accounting', label: 'Accounting', icon: Calculator },
    ],
  },
  {
    heading: 'Actions',
    items: [
      { id: 'new-product', label: 'New Product', icon: Plus },
      { id: 'new-customer', label: 'New Customer', icon: Plus },
      { id: 'new-order', label: 'New Order', icon: Plus, shortcut: '⌘N' },
      { id: 'new-invoice', label: 'New Invoice', icon: Plus },
      { id: 'refresh', label: 'Refresh', icon: RefreshCw, shortcut: '⌘R' },
      { id: 'import', label: 'Import Data', icon: Upload },
      { id: 'export', label: 'Export Data', icon: Download },
    ],
  },
  {
    heading: 'Settings',
    items: [
      { id: 'profile', label: 'Profile', icon: UserCog },
      { id: 'theme', label: 'Theme', icon: Palette },
      { id: 'language', label: 'Language', icon: Globe },
      { id: 'logout', label: 'Logout', icon: LogOut },
    ],
  },
  {
    heading: 'Help',
    items: [
      { id: 'docs', label: 'Documentation', icon: BookOpen },
      { id: 'shortcuts', label: 'Keyboard Shortcuts', icon: Keyboard },
      { id: 'support', label: 'Support Chat', icon: MessageCircle },
      { id: 'report-issue', label: 'Report Issue', icon: Bug },
      { id: 'about', label: 'About', icon: Info },
    ],
  },
];

export interface CommandPaletteProps {
  groups?: CommandGroup[];
  onSelect?: (id: string) => void;
}

function CommandPalette({
  groups = defaultGroups,
  onSelect,
}: CommandPaletteProps) {
  const [open, setOpen] = React.useState(false);
  const [recentItems, setRecentItems] = React.useState<string[]>([]);

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
    };
    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  const handleSelect = (id: string) => {
    setRecentItems((prev) => {
      const next = [id, ...prev.filter((i) => i !== id)].slice(0, 10);
      return next;
    });
    onSelect?.(id);
    setOpen(false);
  };

  const allItems = groups.flatMap((g) => g.items);
  const recentGroup =
    recentItems.length > 0
      ? recentItems
          .map((id) => allItems.find((item) => item.id === id))
          .filter(Boolean)
          .slice(0, 5)
      : [];

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>

        {recentGroup.length > 0 && (
          <>
            <CommandGroup heading="Recent">
              {recentGroup.map(
                (item) =>
                  item && (
                    <CommandItem
                      key={`recent-${item.id}`}
                      value={item.label}
                      onSelect={() => handleSelect(item.id)}
                    >
                      {item.icon ? (
                        <>
                          <Clock className="mr-2 h-4 w-4 text-muted-foreground" />
                          <item.icon className="mr-2 h-4 w-4" />
                        </>
                      ) : (
                        <Clock className="mr-2 h-4 w-4 text-muted-foreground" />
                      )}
                      <span>{item.label}</span>
                    </CommandItem>
                  )
              )}
            </CommandGroup>
            <CommandSeparator />
          </>
        )}

        {groups.map((group, gi) => (
          <React.Fragment key={group.heading}>
            <CommandGroup heading={group.heading}>
              {group.items.map((item) => (
                <CommandItem
                  key={item.id}
                  value={item.label}
                  onSelect={() => handleSelect(item.id)}
                >
                  {item.icon && <item.icon className="mr-2 h-4 w-4" />}
                  <span>{item.label}</span>
                  {item.shortcut && (
                    <CommandShortcut>{item.shortcut}</CommandShortcut>
                  )}
                </CommandItem>
              ))}
            </CommandGroup>
            {gi < groups.length - 1 && <CommandSeparator />}
          </React.Fragment>
        ))}
      </CommandList>
    </CommandDialog>
  );
}

export { CommandPalette };
