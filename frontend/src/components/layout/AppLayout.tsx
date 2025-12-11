'use client';

import { useState } from 'react';
import { Menu } from 'lucide-react';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from '@/components/ui/sheet';
import { AppSidebar } from './AppSidebar';

export function AppLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-900">
      {/* Desktop sidebar */}
      <div className={`hidden lg:fixed lg:inset-y-0 lg:z-40 lg:flex lg:flex-col ${sidebarCollapsed ? 'lg:w-16' : 'lg:w-64'}`}>
        <AppSidebar
          collapsed={sidebarCollapsed}
          onToggleCollapsed={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
      </div>

      {/* Mobile sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <div className="lg:hidden fixed top-4 left-4 z-50 flex items-center gap-2">
          <SheetTrigger asChild>
            <Button
              variant="ghost"
              className="p-2"
              size="sm"
            >
              <Menu className="h-6 w-6" />
            </Button>
          </SheetTrigger>
          <Image
            src="/byro logo cropped.png"
            alt="Byro Logo"
            width={60}
            height={24}
            priority
          />
        </div>
        <SheetContent side="left" className="p-0 w-64">
          <SheetTitle className="sr-only">Sidebar</SheetTitle>
          <AppSidebar />
        </SheetContent>
      </Sheet>

      <main className={`flex-1 ${sidebarCollapsed ? 'lg:ml-16' : 'lg:ml-64'} overflow-auto`}>
        <div className="lg:hidden h-16" /> {/* Spacer for mobile burger */}
        {children}
      </main>
    </div>
  );
}