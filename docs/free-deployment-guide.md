# 無料デプロイ手順（最小構成）

## 🚀 ステップバイステップ

### 必要なサービス
1. **Supabase** - PostgreSQL データベース
2. **Upstash** - Redis キャッシュ 
3. **Railway** - バックエンドAPI + ファイル保存
4. **Vercel** - フロントエンド

### Step 1: データベース (Supabase)
```bash
# 1. Supabaseプロジェクト作成
# 2. 接続文字列取得
# 3. ローカルマイグレーション実行
cd backend
alembic upgrade head
```

### Step 2: キャッシュ (Upstash)
```bash
# 1. Upstash Redis作成
# 2. 接続URL取得
# 3. 接続テスト
```

### Step 3: バックエンド (Railway)
```bash
# 1. Railway プロジェクト作成
railway init

# 2. 環境変数設定
railway variables set DATABASE_URL=...
railway variables set REDIS_URL=...

# 3. デプロイ
railway up
```

### Step 4: フロントエンド (Vercel)
```bash
# 1. Vercel連携
# 2. 環境変数設定
# 3. 自動デプロイ確認
```

## ✅ 動作確認チェックリスト

- [ ] データベース接続OK
- [ ] Redis接続OK
- [ ] ファイルアップロードOK
- [ ] API疎通OK
- [ ] フロントエンド表示OK
- [ ] 認証フローOK
- [ ] プレゼン生成OK

## 🔧 トラブルシューティング

### よくある問題
1. **CORS エラー**: 環境変数のURLチェック
2. **DB接続失敗**: SSL設定確認
3. **Redis接続失敗**: TLS設定確認
4. **ファイルアップロード失敗**: R2権限確認

## 📱 運用コマンド

```bash
# ログ確認
railway logs

# 環境変数確認
railway variables

# ローカルテスト
railway run npm start

# デプロイ状況確認
railway status
```