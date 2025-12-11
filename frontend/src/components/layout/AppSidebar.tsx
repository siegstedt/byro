'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { Inbox, Briefcase, Calendar, Search, ChevronLeft, ChevronRight, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

const navigation = [
  { name: 'Inbox', href: '/inbox', icon: Inbox },
  { name: 'Matters', href: '/matters', icon: Briefcase },
  { name: 'Calendar', href: '/calendar', icon: Calendar },
  { name: 'Search', href: '/search', icon: Search },

];

interface AppSidebarProps {
  collapsed?: boolean;
  onToggleCollapsed?: () => void;
}

export function AppSidebar({ collapsed = false, onToggleCollapsed }: AppSidebarProps) {
  const pathname = usePathname();

  return (
    <div className="h-screen w-full bg-background border-r border-border">
      <div className="flex h-full flex-col">
        <div className="flex h-16 items-center px-4">
          <Link href="/">
            <Image
              src="/byro logo cropped.png"
              alt="Byro Logo"
              width={collapsed ? 40 : 80}
              height={collapsed ? 16 : 30}
              priority
            />
          </Link>
        </div>
        <nav className="flex-1 space-y-1 px-2 py-4">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                  collapsed ? 'justify-center' : '',
                  isActive
                    ? 'bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-100'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-100'
                )}
              >
                <item.icon className={cn("h-5 w-5", !collapsed && "mr-3")} />
                {!collapsed && item.name}
              </Link>
            );
          })}
        </nav>
        <div className={cn(
          "mt-auto py-4 space-y-1",
          collapsed ? "px-2" : "px-4"
        )}>
          {onToggleCollapsed && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggleCollapsed}
              className={cn(
                "w-full",
                collapsed ? "justify-center p-1" : "justify-start px-3 py-2"
              )}
            >
              {collapsed ? (
                <ChevronRight className="h-5 w-5" />
              ) : (
                <>
                  <ChevronLeft className="h-5 w-5 mr-3" />
                  <span className="text-sm font-medium text-slate-600 dark:text-slate-400">Collapse</span>
                </>
              )}
            </Button>
          )}
          <Link
            href="/settings"
            className={cn(
              'flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
              collapsed ? 'justify-center' : '',
              pathname === '/settings'
                ? 'bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-100'
                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-100'
            )}
          >
            <Settings className={cn("h-5 w-5", !collapsed && "mr-3")} />
            {!collapsed && "Settings"}
          </Link>
        </div>
      </div>
    </div>
  );
}