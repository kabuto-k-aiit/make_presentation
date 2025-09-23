# Vercel デプロイ設定

## 1. Vercel アカウント
- https://vercel.com でGitHubログイン
- リポジトリ連携

## 2. プロジェクト設定
- Import Git Repository
- Framework Preset: Next.js
- Root Directory: `frontend`

## 3. 環境変数設定
Vercel Dashboard > Settings > Environment Variables:
```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

## 4. ビルド設定
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install"
}
```

## 5. カスタムドメイン（オプション）
- Project Settings > Domains
- 独自ドメイン追加可能

## 6. 自動デプロイ
- main ブランチプッシュで自動デプロイ
- プレビューデプロイ対応