# Make Presentation

プレゼンテーション自動生成アプリケーション

## システム要件

- Node.js 18.0.0以上
- Python 3.12以上
- PostgreSQL 14以上
- Redis 6以上

## プロジェクト構成

```
make_presentation/
├── frontend/          # Next.js フロントエンド
├── backend/           # FastAPI バックエンド
└── docs/             # 追加のドキュメント
```

## 開発環境のセットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/kabuto-k-aiit/make_presentation.git
cd make_presentation
```

### 2. 環境変数の設定

`.env`ファイルをプロジェクトルートに作成:

```env
# PostgreSQL設定
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/presentation_db"

# Redis設定
REDIS_HOST="localhost"
REDIS_PORT="6379"

# JWT設定
SECRET_KEY="your-secure-secret-key"
REFRESH_SECRET_KEY="your-secure-refresh-key"
```

### 3. データベースのセットアップ

```bash
# PostgreSQLのインストール
brew install postgresql@14
brew services start postgresql@14

# データベースの作成
createdb presentation_db
```

### 4. Redisのセットアップ

```bash
# Redisのインストール
brew install redis
brew services start redis
```

### 5. バックエンドのセットアップ

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 6. フロントエンドのセットアップ

```bash
cd frontend
npm install
npm run dev
```

## 使用技術

### フロントエンド
- Next.js 14
- TypeScript
- Redux Toolkit
- Material-UI

### バックエンド
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- JWT認証

## セキュリティ

- JWTベースの認証システム
- リフレッシュトークンによるセッション管理
- パスワードのハッシュ化（bcrypt）
- レート制限による保護
- アカウントロックアウト機能

## API ドキュメント

バックエンドサーバー起動後、以下のURLでSwagger UIを確認できます：
- http://localhost:8000/docs
- http://localhost:8000/redoc

## コントリビューション

1. このリポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## ライセンス

[MITライセンス](LICENSE)
