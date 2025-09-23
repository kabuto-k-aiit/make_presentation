'use client';

import { useTokenRefresh } from '@/hooks/useTokenRefresh';
import { ReactNode, useEffect, useState } from 'react';

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  return (
    <>
      {isClient && <ClientOnlyTokenRefresh />}
      {children}
    </>
  );
};

const ClientOnlyTokenRefresh = () => {
  useTokenRefresh();
  return null;
};