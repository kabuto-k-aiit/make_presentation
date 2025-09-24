# 🔐 Basic認証実装オプション

## 🎯 適用範囲の選択肢

### オプション A: **全APIエンドポイント保護**
- すべてのAPIアクセスにBasic認証必須
- 最も安全だが、フロントエンドから呼び出し時に認証情報必要

### オプション B: **管理系エンドポイントのみ**（推奨）
- `/api/invite/*` (招待コード管理)
- `/admin/*` (管理系機能)
- 一般ユーザーのAPI使用は従来通りJWT認証のみ

### オプション C: **開発・デバッグ用エンドポイント**
- `/docs`, `/redoc` (Swagger UI)
- `/health`, `/metrics` (監視系)

## 🛠️ 推奨実装: オプション B

理由:
- ✅ 管理機能の不正アクセスを防止
- ✅ 一般ユーザーの利便性を保持
- ✅ フロントエンドの改修不要
- ✅ 招待コード管理の二重保護

## 📋 環境変数設定

```env
# Basic認証設定
BASIC_AUTH_ENABLED=true
BASIC_AUTH_USERNAME=admin
BASIC_AUTH_PASSWORD=your_secure_password_here

# 開発環境では無効化
# BASIC_AUTH_ENABLED=false
```

## 🔧 実装方法

```python
# 管理系エンドポイントに適用
@app.post("/api/invite/create")
async def create_invite_code(
    invite_data: InviteCodeCreate,
    current_user: User = Depends(get_current_user),
    basic_auth: bool = Depends(verify_basic_auth),  # Basic認証追加
    db: Session = Depends(get_db)
):
    # 既存のロジック
```

どのオプションで実装しましょうか？