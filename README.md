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
├── backend/          # FastAPI バックエンド
├── docs/            # ドキュメント
│   ├── analytics-setup.md           # GA4導入ガイド
│   ├── invite-code-management.md    # 招待コード運用ガイド
│   ├── git-commit-template.md       # コミットテンプレートガイド
│   └── ...           # その他のドキュメント
├── .gitmessage      # Git コミットテンプレート
└── docker/          # Docker関連ファイル
```

## Docker環境での開発

### 1. Docker環境の起動

```bash
docker-compose up -d

# ログを確認
docker-compose logs -f
```

### 2. コンテナの停止

```bash
docker-compose down
```

### 3. コンテナとボリュームの完全削除

```bash
docker-compose down -v
```

### 4. 個別のサービスの再起動

```bash
# フロントエンドの再起動
docker-compose restart frontend

# バックエンドの再起動
docker-compose restart backend
```

### 5. コンテナ内でのコマンド実行

```bash
# バックエンドでのマイグレーション実行
docker-compose exec backend alembic upgrade head

# フロントエンドでのパッケージインストール
docker-compose exec frontend npm install

# データベースへの接続
docker-compose exec db psql -U postgres -d presentation_db
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
- **Google Analytics 4** (ユーザー行動分析)

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
- レート制限による保護（プレゼンテーション生成: 5回/時間、本番環境）
- アカウントロックアウト機能

### 開発環境でのレート制限解除

開発時はレート制限を解除して効率的にテストできます：

```env
# .envファイルに追加
DISABLE_RATE_LIMIT=true
```

これにより、レート制限が事実上無効化され（1000回/時間）、開発がスムーズになります。

## アナリティクス

Google Analytics 4 (GA4) を導入しており、以下のユーザー行動を分析できます：

- **認証イベント**: ログイン/ログアウトの追跡
- **プレゼンテーション生成**: テーマ、スライド数の分析
- **ファイルダウンロード**: ダウンロード数の計測
- **ユーザーエンゲージメント**: ページビュー、滞在時間

### セットアップ方法

1. [Google Analytics](https://analytics.google.com/) でGA4プロパティを作成
2. **本番用ストリーム**: 実際のドメインで作成（localhostは使用不可）
3. 測定IDを取得して `.env` の `NEXT_PUBLIC_GA_MEASUREMENT_ID` に設定
4. **開発時は** `NEXT_PUBLIC_ENABLE_GA=false` でGA4を無効化
5. **本番時は** `NEXT_PUBLIC_ENABLE_GA=true` でGA4を有効化

詳細は [アナリティクス導入ガイド](./docs/analytics-setup.md) を参照してください。

## API ドキュメント

バックエンドサーバー起動後、以下のURLでSwagger UIを確認できます：
- http://localhost:8000/docs
- http://localhost:8000/redoc

### 認証API

#### リフレッシュトークン
```http
POST /refresh
Content-Type: application/json

{
  "current_token": "your_refresh_token_here"
}
```

リフレッシュトークンを使用して新しいアクセストークンを取得します。トークンの有効期限が切れた場合に使用してください。

## コントリビューション

### Git コミットメッセージ

このプロジェクトでは統一されたコミットメッセージ形式を使用しています：

```bash
# テンプレート設定
git config commit.template .gitmessage

# コミット時にテンプレートが表示されます
git commit
```

詳細は [Git コミットテンプレートガイド](./docs/git-commit-template.md) を参照してください。

### プルリクエスト手順

1. このリポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (テンプレートに従って `git commit`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## ライセンス

[MITライセンス](LICENSE)
