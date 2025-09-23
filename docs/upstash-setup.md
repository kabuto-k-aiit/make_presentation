# Upstash Redis 設定

## 1. アカウント作成
- https://upstash.com でアカウント作成
- GitHubログインでOK

## 2. Redis データベース作成
- Console > Redis > Create Database
- リージョン選択（東京推奨）
- 無料プラン選択

## 3. 接続情報取得
Details タブで以下を取得:
```
REDIS_URL=rediss://:[PASSWORD]@[ENDPOINT]:6380
```

## 4. 環境変数更新
```env
REDIS_URL=rediss://:[PASSWORD]@[ENDPOINT]:6380
REDIS_HOST=[ENDPOINT]
REDIS_PORT=6380
REDIS_PASSWORD=[PASSWORD]
```

## 5. SSL接続設定
backend/main.py で SSL 接続確認:
```python
import redis
redis_client = redis.from_url(
    os.getenv("REDIS_URL"),
    decode_responses=True,
    ssl_cert_reqs=None
)
```