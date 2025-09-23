FROM node:18-alpine AS builder

# セキュリティ更新を実行
RUN apk update && apk upgrade

WORKDIR /app

# 依存パッケージをインストール
COPY package.json package-lock.json ./
RUN npm install

# アプリケーションコードをコピー
COPY . .

# ビルド
RUN npm run build

# 実行時の設定
EXPOSE 3000
CMD ["npm", "start"]
