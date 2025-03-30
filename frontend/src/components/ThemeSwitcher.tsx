'use client';

import { Moon, Sun, Monitor } from 'lucide-react';
import { useTheme } from '@/providers/ThemeProvider';

export function ThemeSwitcher() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="flex items-center gap-2 p-2 rounded-lg bg-gray-100 dark:bg-gray-800">
      <button
        onClick={() => setTheme('light')}
        className={`p-2 rounded-md ${
          theme === 'light'
            ? 'bg-white text-black shadow-sm dark:bg-gray-700 dark:text-white'
            : 'text-gray-500 dark:text-gray-400'
        }`}
      >
        <Sun className="h-5 w-5" />
        <span className="sr-only">Light Mode</span>
      </button>
      <button
        onClick={() => setTheme('dark')}
        className={`p-2 rounded-md ${
          theme === 'dark'
            ? 'bg-white text-black shadow-sm dark:bg-gray-700 dark:text-white'
            : 'text-gray-500 dark:text-gray-400'
        }`}
      >
        <Moon className="h-5 w-5" />
        <span className="sr-only">Dark Mode</span>
      </button>
      <button
        onClick={() => setTheme('system')}
        className={`p-2 rounded-md ${
          theme === 'system'
            ? 'bg-white text-black shadow-sm dark:bg-gray-700 dark:text-white'
            : 'text-gray-500 dark:text-gray-400'
        }`}
      >
        <Monitor className="h-5 w-5" />
        <span className="sr-only">System Theme</span>
      </button>
    </div>
  );
} 