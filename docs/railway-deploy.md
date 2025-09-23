# Railway デプロイ設定

## 1. Railway アカウント作成
- https://railway.app でGitHubログイン
- $5/月の無料クレジット取得

## 2. プロジェクト作成
```bash
# Railway CLI インストール
npm install -g @railway/cli

# ログイン
railway login

# プロジェクト初期化
railway init
```

## 3. 環境変数設定
Railway Dashboard > Variables:
```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
SECRET_KEY=your-secret-key
REFRESH_SECRET_KEY=your-refresh-secret-key
CORS_ORIGINS=https://your-frontend.vercel.app
PORT=8000
```

## 4. Dockerデプロイ
```bash
# backend/Dockerfile がそのまま使用される
railway up
```

## 5. カスタムドメイン（オプション）
- Railway Dashboard > Settings > Domains
- カスタムドメイン追加可能