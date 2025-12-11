'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Inbox, Briefcase, Calendar, Search } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ThemeToggle } from '@/components/ui/theme-toggle';

const navigation = [
  { name: 'Inbox', href: '/inbox', icon: Inbox },
  { name: 'Matters', href: '/matters', icon: Briefcase },
  { name: 'Calendar', href: '/calendar', icon: Calendar },
  { name: 'Search', href: '/search', icon: Search },
];

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <div className="fixed left-0 top-0 z-40 h-screen w-64 bg-white border-r border-slate-200">
      <div className="flex h-full flex-col">
        <div className="flex h-16 items-center px-6">
          <h1 className="text-xl font-semibold text-slate-900">Byro</h1>
        </div>
        <nav className="flex-1 space-y-1 px-4 py-4">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                  isActive
                    ? 'bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-100'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-100'
                )}
              >
                <item.icon className="mr-3 h-5 w-5" />
                {item.name}
              </Link>
            );
          })}
        </nav>
        <div className="px-4 py-4">
          <ThemeToggle />
        </div>
      </div>
    </div>
  );
}