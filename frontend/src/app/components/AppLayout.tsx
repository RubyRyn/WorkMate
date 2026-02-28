import { useEffect, useState, type ReactNode } from 'react';
import { useLocation } from 'react-router-dom';
import { Menu } from 'lucide-react';
import { Button } from './ui/button';
import { Sheet, SheetContent, SheetTitle } from './ui/sheet';
import { useIsMobile } from './ui/use-mobile';
import { SidebarContent } from './Sidebar';

interface AppLayoutProps {
  children: ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const isMobile = useIsMobile();
  const [sheetOpen, setSheetOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setSheetOpen(false);
  }, [location.pathname]);

  if (!isMobile) {
    return (
      <div className="flex h-screen overflow-hidden bg-white dark:bg-slate-900">
        <SidebarContent />
        {children}
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-white dark:bg-slate-900">
      {/* Mobile top bar */}
      <div className="flex items-center gap-3 border-b border-slate-200 dark:border-slate-700 px-4 py-3">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setSheetOpen(true)}
          className="h-8 w-8 text-slate-600 dark:text-slate-400"
        >
          <Menu className="h-5 w-5" />
        </Button>
        <h1 className="text-lg font-bold text-purple-700 dark:text-purple-400">WorkMate</h1>
      </div>

      {/* Sheet sidebar */}
      <Sheet open={sheetOpen} onOpenChange={setSheetOpen}>
        <SheetContent side="left" className="w-80 p-0">
          <SheetTitle className="sr-only">Navigation</SheetTitle>
          <SidebarContent onNavigate={() => setSheetOpen(false)} />
        </SheetContent>
      </Sheet>

      {/* Page content */}
      <div className="flex-1 overflow-hidden">{children}</div>
    </div>
  );
}
