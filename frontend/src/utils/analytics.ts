// Google Analytics 4 イベント送信ユーティリティ
declare global {
  interface Window {
    gtag: (...args: any[]) => void;
  }
}

export const GA_MEASUREMENT_ID = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID;
export const ENABLE_GA = process.env.NEXT_PUBLIC_ENABLE_GA === 'true';

// GA4イベント送信関数
export const sendGAEvent = (
  action: string,
  parameters: Record<string, any> = {}
) => {
  if (ENABLE_GA && typeof window !== 'undefined' && window.gtag && GA_MEASUREMENT_ID) {
    window.gtag('event', action, {
      ...parameters,
      custom_parameter_1: 'presentation_app'
    });
  }
};

// ページビュー送信
export const sendGAPageView = (url: string) => {
  if (ENABLE_GA && typeof window !== 'undefined' && window.gtag && GA_MEASUREMENT_ID) {
    window.gtag('config', GA_MEASUREMENT_ID, {
      page_path: url,
    });
  }
};

// プレゼンテーション関連イベント
export const trackPresentationEvent = (eventType: string, details?: Record<string, any>) => {
  sendGAEvent(`presentation_${eventType}`, {
    ...details,
    category: 'presentation'
  });
};

// ユーザー認証関連イベント
export const trackAuthEvent = (eventType: string, details?: Record<string, any>) => {
  sendGAEvent(`auth_${eventType}`, {
    ...details,
    category: 'authentication'
  });
};

// 招待コード関連イベント
export const trackInviteEvent = (eventType: string, details?: Record<string, any>) => {
  sendGAEvent(`invite_${eventType}`, {
    ...details,
    category: 'invitation'
  });
};