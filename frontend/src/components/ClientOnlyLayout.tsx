'use client';

import { useEffect, useState } from 'react';
import Navigation from './Navigation';
import { AuthProvider } from './AuthProvider';

interface ClientOnlyLayoutProps {
  children: React.ReactNode;
}

export const ClientOnlyLayout = ({ children }: ClientOnlyLayoutProps) => {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient) {
    // SSR中は基本的なレイアウトのみ
    return <div suppressHydrationWarning>{children}</div>;
  }

  // クライアントサイドでは完全な機能を提供
  return (
    <AuthProvider>
      <Navigation />
      {children}
    </AuthProvider>
  );
};