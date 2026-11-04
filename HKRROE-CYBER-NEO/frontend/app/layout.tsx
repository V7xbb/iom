import './globals.css';
import type { Metadata } from 'next';
export const metadata: Metadata = {
  title: 'HKRROE | Building Smart Digital Experiences',
  description: 'HKRROE — تطوير بوتات Telegram وحلول الذكاء الاصطناعي والبرمجيات.',
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://example.com'),
  applicationName: 'HKRROE',
};
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="ar" dir="rtl"><body>{children}</body></html>;
}
