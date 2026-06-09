import type { Metadata } from 'next';
import './globals-compiled.css';
import { Providers } from '../components/providers';

export const metadata: Metadata = {
  title: 'Agent OnboardX - AI Goal Operating System',
  description: 'A production-grade SaaS workspace to sequence, track, and adapt goals dynamically.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased min-h-screen bg-[#0b0f19]">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
