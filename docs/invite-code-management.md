# 招待コード管理ガイド

## 概要

このシステムでは、ユーザー登録を招待コード制としており、管理者のみが招待コードを作成・管理できます。本ドキュメントでは、招待コード付与システムの運用手順について説明します。

## 管理者アカウント

### 管理者アカウントの概要

- **ユーザー名**: `admin` (固定)
- **メールアドレス**: `admin@example.com` (初期設定)
- **パスワード**: 環境変数またはデータベースから取得
- **権限**: 招待コードの作成・管理

⚠️ **セキュリティ注意**: 実際の管理者パスワードはGitにコミットせず、環境変数や安全な設定ファイルで管理してください。

### 管理者アカウントの作成

初回起動時に管理者アカウントを作成する場合：

```bash
# スクリプト実行
docker exec -e PYTHONPATH=/app make_presentation-backend-1 python scripts/create_admin.py
```

または、データベースに直接作成：

```bash
# PostgreSQLに接続して管理者作成
docker exec make_presentation-db-1 psql -U postgres -d presentation_db
```

```sql
-- 管理者ユーザー作成例
INSERT INTO app_users (username, email, hashed_password)
VALUES ('admin', 'admin@example.com', '$2b$12$your_secure_hash_here');
```

### 管理者アカウントの確認方法

#### 1. データベース直接確認
```bash
# 管理者アカウントの存在確認
docker exec make_presentation-db-1 psql -U postgres -d presentation_db -c "SELECT id, username, email FROM app_users WHERE username = 'admin';"
```

#### 2. 全ユーザー一覧の確認
```bash
# 全ユーザーを確認
docker exec make_presentation-db-1 psql -U postgres -d presentation_db -c "SELECT id, username, email FROM app_users ORDER BY id;"
```

#### 3. 定期確認スクリプト
```bash
# 管理者アカウントの状態確認
docker exec make_presentation-db-1 psql -U postgres -d presentation_db -c "SELECT COUNT(*) FROM app_users WHERE username = 'admin';" | grep -v COUNT
```

## 招待コードの作成手順

### 1. 管理者ログイン

管理者アカウントでログインしてJWTトークンを取得します。

```bash
# ログインリクエスト（実際のパスワードを使用）
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=YOUR_ADMIN_PASSWORD"
```

**レスポンス例:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

⚠️ **注意**: `YOUR_ADMIN_PASSWORD` は実際の管理者パスワードに置き換えてください。

### 2. 招待コード作成

取得したアクセストークンを使用して招待コードを作成します。

```bash
# 招待コード作成リクエスト
curl -X POST "http://localhost:8000/api/invite/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"expires_hours": 168}'
```

**パラメータ:**
- `expires_hours`: 招待コードの有効期限（時間単位、デフォルト: 168 = 1週間）

**レスポンス例:**
```json
{
  "invite_code": "SACmZ1OmElR6Of7h",
  "expires_at": "2025-10-01T17:12:46.627210",
  "created_by": "admin@example.com"
}
```

### 3. 招待コードの配布

生成された招待コードを新規ユーザーに提供します。

- **招待コード**: `SACmZ1OmElR6Of7h`
- **有効期限**: `2025-10-01T17:12:46.627210`
- **作成者**: `admin@example.com`

## 招待コードの一覧表示

### 管理者権限での一覧表示

```bash
# 招待コード一覧取得
curl -X GET "http://localhost:8000/api/invite/list" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**レスポンス例:**
```json
{
  "invite_codes": [
    {
      "id": 1,
      "code": "ADMIN2025",
      "is_used": true,
      "used_by_email": "admin2@example.com",
      "created_at": "2025-09-24T16:39:15.561762+00:00",
      "expires_at": "2026-09-24T16:39:15.564032+00:00",
      "created_by": "admin@example.com"
    }
  ]
}
```

## ユーザー登録フロー

### 1. 招待コードの検証

ユーザーが招待コードの有効性を確認できます。

```bash
# 招待コード検証
curl -X POST "http://localhost:8000/api/invite/verify" \
  -H "Content-Type: application/json" \
  -d '{"code": "SACmZ1OmElR6Of7h"}'
```

### 2. ユーザー登録

有効な招待コードを使用してアカウント登録を行います。

```bash
# ユーザー登録
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "newuser",
    "password": "password123",
    "invite_code": "SACmZ1OmElR6Of7h"
  }'
```

## トラブルシューティング

### 管理者権限エラー (403 Forbidden)

**原因**: 管理者以外のアカウントで招待コード作成を試行
**解決**: adminアカウントでログインして操作

### 招待コード無効エラー (400 Bad Request)

**原因**: 無効/期限切れ/使用済みの招待コード
**解決**:
- コードの有効性を `/api/invite/verify` で確認
- 新しい招待コードを作成

### データベース接続エラー

**確認方法**:
```bash
# データベース接続確認
docker exec make_presentation-db-1 psql -U postgres -d presentation_db -c "SELECT version();"
```

### ログ確認

```bash
# バックエンドログ確認
docker logs make_presentation-backend-1 --tail 50

# データベースログ確認
docker logs make_presentation-db-1 --tail 20
```

## セキュリティ考慮事項

### ⚠️ 重要: 機密情報の管理

- **管理者パスワードはGitにコミットしない**
  - 環境変数や安全な設定ファイルで管理
  - `.env` ファイルは `.gitignore` に追加
- **招待コードの安全な配布**
  - コードは安全な方法でユーザーに提供
  - 使用済みコードは自動的に無効化
- **ログの監視**
  - 不審なアクセスを定期的に確認
  - セキュリティイベントをログで追跡

### 環境変数の設定例

```bash
# .envファイル（Gitにコミットしない）
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password_here
ADMIN_EMAIL=admin@example.com
```

### .gitignoreの設定

`.gitignore` に以下のエントリを追加：

```
# 環境変数ファイル
.env
.env.local
.env.*.local

# 機密情報
secrets/
*.key
*.pem
```

## 運用チェックリスト

### 日次チェック
- [ ] 管理者アカウントの存在確認
- [ ] システムログの確認
- [ ] データベース接続状態
- [ ] 機密ファイルのGitコミット状況確認

### 週次チェック
- [ ] 招待コードの有効期限確認
- [ ] ユーザー登録数の確認
- [ ] システムリソースの使用状況
- [ ] パスワードポリシーの確認

### 月次チェック
- [ ] 管理者パスワードの変更
- [ ] セキュリティログのレビュー
- [ ] バックアップの確認
- [ ] アクセス権限の監査