'use client';

import { useTokenRefresh } from '@/hooks/useTokenRefresh';
import { ReactNode } from 'react';

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  // トークンリフレッシュのロジックを使用
  useTokenRefresh();

  return <>{children}</>;
};