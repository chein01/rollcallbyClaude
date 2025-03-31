import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import './globals.css';
import { Providers } from './providers';
import Header from '@/components/Header';
import { Toaster } from 'sonner';
import { ThemeProvider } from '@/providers/ThemeProvider';

const geistSans = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

const geistMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
});

export const metadata: Metadata = {
  title: "RollCallByCusor",
  description: "A modern attendance tracking system",
  icons: {
    icon: [
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      }
    ],
  }
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                let theme = 'system';
                try {
                  theme = localStorage.getItem('theme') || 'system';
                } catch (e) {}

                if (theme === 'system') {
                  theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
                }

                document.documentElement.classList.add(theme);
              })();
            `,
          }}
        />
      </head>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased font-hartwell`} suppressHydrationWarning>
        <ThemeProvider>
          <div className="min-h-screen bg-background">
            <Providers>
              <Header />
              {children}
            </Providers>
          </div>
        </ThemeProvider>
        <Toaster richColors position="top-right" />
      </body>
    </html>
  );
}
