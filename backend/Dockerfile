FROM python:3.12-slim

WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 依存パッケージをインストール
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY backend/ .

# ポート設定（Railwayが動的に割り当て）
EXPOSE ${PORT:-8000}

# 実行コマンド
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
