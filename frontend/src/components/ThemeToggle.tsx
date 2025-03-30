import { Moon, Sun, Monitor } from 'lucide-react';
import { useTheme } from '@/providers/ThemeProvider';
import { useState, useEffect, useRef } from 'react';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [showThemeMenu, setShowThemeMenu] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Xử lý đóng menu khi click ra ngoài
  useEffect(() => {
    function handleOutsideClick(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowThemeMenu(false);
      }
    }
    
    if (showThemeMenu) {
      document.addEventListener('mousedown', handleOutsideClick);
    }
    
    return () => {
      document.removeEventListener('mousedown', handleOutsideClick);
    };
  }, [showThemeMenu]);

  const themeIcon = theme === 'dark' ? <Moon className="h-5 w-5" /> : 
                   theme === 'light' ? <Sun className="h-5 w-5" /> : 
                   <Monitor className="h-5 w-5" />;

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setShowThemeMenu(!showThemeMenu)}
        className="p-2 rounded-md hover:bg-accent hover:text-accent-foreground transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-1"
        aria-label="Chuyển đổi giao diện"
      >
        {themeIcon}
      </button>
      
      {showThemeMenu && (
        <div className="absolute right-0 mt-2 w-48 py-2 bg-card text-card-foreground border border-border rounded-lg shadow-lg z-50 animate-in fade-in-50 slide-in-from-top-5 duration-200">
          <button
            onClick={() => {
              setTheme('light');
              setShowThemeMenu(false);
            }}
            className="flex items-center w-full px-4 py-2 text-sm hover:bg-accent hover:text-accent-foreground font-medium transition-colors"
          >
            <Sun className="h-4 w-4 mr-2" />
            Light
          </button>
          <button
            onClick={() => {
              setTheme('dark');
              setShowThemeMenu(false);
            }}
            className="flex items-center w-full px-4 py-2 text-sm hover:bg-accent hover:text-accent-foreground font-medium transition-colors"
          >
            <Moon className="h-4 w-4 mr-2" />
            Dark
          </button>
          <button
            onClick={() => {
              setTheme('system');
              setShowThemeMenu(false);
            }}
            className="flex items-center w-full px-4 py-2 text-sm hover:bg-accent hover:text-accent-foreground font-medium transition-colors"
          >
            <Monitor className="h-4 w-4 mr-2" />
            System
          </button>
        </div>
      )}
    </div>
  );
} 