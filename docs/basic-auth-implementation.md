# Basic認証実装完了

## 実装内容

### 1. Basic認証インフラ（`backend/auth/security.py`）
- HTTPBasic、HTTPBasicCredentialsのimport追加
- `verify_basic_auth()` 関数: Basic認証を検証
- `get_basic_auth_user()` 関数: 管理者認証用エンドポイント
- 環境変数設定:
  - `BASIC_AUTH_ENABLED`: Basic認証の有効/無効
  - `BASIC_AUTH_USERNAME`: 管理者ユーザー名
  - `BASIC_AUTH_PASSWORD`: 管理者パスワード
- セキュリティ: 定数時間比較（secrets.compare_digest）を使用

### 2. 管理エンドポイント保護（`backend/routers/invite_codes.py`）
適用したエンドポイント:
- `POST /api/invite/create` - 招待コード作成
- `GET /api/invite/list` - 招待コード一覧

両エンドポイントでBasic認証が必須：
```python
basic_auth: bool = Depends(verify_basic_auth)
```

### 3. 環境変数設定（`railway-env-vars.txt`）
Railway本番環境用の環境変数設定追加:
```
BASIC_AUTH_ENABLED=true
BASIC_AUTH_USERNAME=admin
BASIC_AUTH_PASSWORD=your-secure-admin-password-change-this
```

### 4. Docker環境設定（`docker-compose.dev.yml`）
開発環境用のBasic認証設定追加:
```yaml
environment:
  - BASIC_AUTH_ENABLED=true
  - BASIC_AUTH_USERNAME=admin
  - BASIC_AUTH_PASSWORD=test123
```

## 使用方法

### 管理エンドポイントへのアクセス
```bash
# 招待コード作成
curl -X POST "http://localhost:8000/api/invite/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46dGVzdDEyMw==" \
  -d '{"expires_at": "2024-12-31T23:59:59"}'

# 招待コード一覧
curl -X GET "http://localhost:8000/api/invite/list" \
  -H "Authorization: Basic YWRtaW46dGVzdDEyMw=="
```

### Base64エンコード
- `admin:test123` → `YWRtaW46dGVzdDEyMw==`
- 本番環境では強力なパスワードに変更必要

## セキュリティ効果

### 1. 不正アクセス防止
- 招待コード管理機能への不正アクセスを防止
- システム全体ではなく管理機能のみを保護（Option B方式）

### 2. 多層防御
- JWT認証: 一般ユーザー認証
- Basic認証: 管理者機能保護
- 招待コード: ユーザー登録制限

### 3. 簡単な実装・運用
- 追加のデータベーステーブル不要
- 環境変数での簡単設定
- 標準的なHTTP Basic認証

## デプロイメント

### 本番環境（Railway）
1. Railway Dashboardで環境変数設定:
   - `BASIC_AUTH_ENABLED=true`
   - `BASIC_AUTH_USERNAME=admin`  
   - `BASIC_AUTH_PASSWORD=[強力なパスワード]`

2. デプロイ後の動作確認:
   ```bash
   curl -X GET "https://your-app.railway.app/api/invite/list" \
     -H "Authorization: Basic [Base64エンコード]"
   ```

### ローカル開発環境
```bash
export BASIC_AUTH_ENABLED=true
export BASIC_AUTH_USERNAME=admin
export BASIC_AUTH_PASSWORD=test123
```

または `.env` ファイルに設定

## 注意事項

1. **パスワード管理**: 本番環境では強力なパスワードを使用
2. **HTTPS必須**: 本番環境ではHTTPS必須（平文送信防止）
3. **定期更新**: パスワードの定期変更推奨
4. **ログ管理**: Basic認証失敗のログ監視

## 完了状態
✅ Basic認証インフラ実装完了  
✅ 管理エンドポイント保護完了  
✅ 環境変数設定完了  
✅ Docker設定完了  
✅ ドキュメント作成完了