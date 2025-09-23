# Supabase環境設定

## 1. Supabaseプロジェクト作成
- https://supabase.com にアクセス
- "Start your project" でアカウント作成
- 新しいプロジェクト作成

## 2. 接続情報取得
Settings > Database > Connection string
```
postgresql://postgres:[YOUR-PASSWORD]@[HOST]:5432/postgres
```

## 3. 環境変数更新
```env
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
SUPABASE_URL=https://[PROJECT-ID].supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

## 4. マイグレーション実行
```bash
# ローカルでマイグレーション
cd backend
alembic upgrade head
```