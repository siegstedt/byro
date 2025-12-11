import { ThemeToggle } from '@/components/ui/theme-toggle';

export default function SettingsPage() {
  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold mb-6">Settings</h1>
      <div className="space-y-6">
        <div>
          <h2 className="text-lg font-semibold mb-2">Theme</h2>
          <p className="text-sm text-muted-foreground mb-4">
            Choose your preferred theme for the application.
          </p>
          <ThemeToggle />
        </div>
      </div>
    </div>
  );
}