'use client';

import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { selectAuth, refreshToken } from '@/store/authSlice';
import { AppDispatch } from '@/store/store';
import { jwtDecode } from 'jwt-decode';

interface JWTPayload {
  exp: number;
  [key: string]: unknown;
}

export const useTokenRefresh = () => {
  const dispatch = useDispatch<AppDispatch>();
  const auth = useSelector(selectAuth);

  useEffect(() => {
    // サーバーサイドレンダリング中やトークンがない場合は何もしない
    if (typeof window === 'undefined' || !auth.token) return;

    const checkTokenExpiration = () => {
      try {
        const decoded = jwtDecode<JWTPayload>(auth.token!);
        const expirationTime = decoded.exp * 1000; // Convert to milliseconds
        const currentTime = Date.now();
        const timeUntilExpiration = expirationTime - currentTime;

        // トークンの有効期限が5分未満の場合にリフレッシュ
        if (timeUntilExpiration < 5 * 60 * 1000) {
          void dispatch(refreshToken());
        }

        // 次回のチェックをスケジュール
        return setTimeout(
          checkTokenExpiration,
          Math.min(timeUntilExpiration - 4 * 60 * 1000, 5 * 60 * 1000)
        );
      } catch (error) {
        console.error('Failed to decode token:', error);
      }
    };

    const timerId = checkTokenExpiration();

    return () => {
      if (timerId) clearTimeout(timerId);
    };
  }, [auth.token, dispatch]);
};