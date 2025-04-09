import './globals.css';
import { Inter } from 'next/font/google';
import { ThemeProvider } from '@/components/ThemeProvider';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'bAIby Core Dashboard',
  description: 'Dashboard para monitoreo de transacciones y sentinels de bAIby Core',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body className={`${inter.className}`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {/* Eliminamos el header global, ya que la página tiene su propio encabezado con el toggle de tema */}
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
