# Google Analytics 4 (GA4) 導### 2. ストリーム設定

GA4では本番環境のドメインでのみストリームを作成します：

#### ストリーム作成
1. **本番用ストリーム**:
   - URL: `https://your-app.vercel.app` （実際のドメイン）
   - ストリーム名: `Production`

**注意**: localhostはGA4のポリシーで許可されていないため、開発時はGA4を無効化します。

#### 測定IDの設定
```env
# .envファイル
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX  # 本番用ストリームID
NEXT_PUBLIC_ENABLE_GA=false                 # 開発時はfalse
```

### 3. 環境別設定

#### 開発環境
```env
NEXT_PUBLIC_ENABLE_GA=false  # GA4無効
```

#### 本番環境
```env
NEXT_PUBLIC_ENABLE_GA=true   # GA4有効
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX
```ドキュメントでは、プレゼンテーション自動生成アプリケーションにGoogle Analytics 4を導入する方法について説明します。

## 概要

Google Analytics 4 (GA4) を導入することで、以下のユーザー行動を分析できます：

- ユーザー認証（ログイン/ログアウト）
- プレゼンテーション生成（テーマ、スライド数）
- ファイルダウンロード（形式、サイズ）
- 招待コード使用状況
- ページビューとユーザーエンゲージメント

## 導入手順

### 1. Google Analytics 4 プロパティの作成

1. [Google Analytics](https://analytics.google.com/) にアクセス
2. 「測定を開始」をクリック
3. アカウント名を入力（例: "Make Presentation App"）
4. プロパティ名を入力（例: "Make Presentation GA4"）
5. レポートのタイムゾーンと通貨を設定
6. 「ウェブ」を選択して続行
7. ウェブサイトのURLを入力（例: `http://localhost:3000` または本番URL）
8. ストリーム名を入力（例: "Development" または "Production"）
9. 「測定ID」をコピー（`G-XXXXXXXXXX` 形式）

### 2. 環境変数の設定

`.env` ファイルを編集して、取得した測定IDを設定：

```env
# Google Analytics 4
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

### 3. アプリケーションの起動

環境変数を設定後、アプリケーションを起動：

```bash
# Docker環境の場合
docker-compose up -d

# またはローカル開発の場合
cd frontend && npm run dev
```

## 実装内容

### トラッキングイベント

以下のイベントが自動的に送信されます：

#### 認証関連イベント
- `auth_login_success`: ログイン成功時
  - パラメータ: `method` (認証方法)

#### プレゼンテーション関連イベント
- `presentation_generate_slide`: スライド生成時
  - パラメータ: `theme`, `slide_count`, `method`
- `presentation_download_presentation`: プレゼンテーションダウンロード時
  - パラメータ: `file_name`, `slide_count`, `format`

### カスタムイベントの追加

新しいイベントを追加するには、`src/utils/analytics.ts` の関数を使用：

```typescript
import { trackPresentationEvent, trackAuthEvent, trackInviteEvent } from '@/utils/analytics';

// 例: カスタムプレゼンテーションイベント
trackPresentationEvent('custom_action', {
  custom_param: 'value'
});
```

## レポートの確認

GA4ダッシュボードで以下のレポートを確認できます：

1. **リアルタイムレポート**: 現在のユーザー行動
2. **ユーザー取得レポート**: ユーザーの流入元
3. **エンゲージメントレポート**: ページビュー、イベント数
4. **コンバージョンレポート**: 目標達成状況

## プライバシーとコンプライアンス

### GDPR 対応

GA4を使用する際は、以下の点を考慮してください：

1. **Cookie同意バナー**: ユーザーの同意を得る
2. **データ保持期間**: 必要最小限に設定
3. **IP匿名化**: 自動的に有効

### 開発環境での注意

- 開発環境では `localhost` のデータはGA4に送信されます
- 本番環境のみを分析したい場合は、環境変数で制御可能

## トラブルシューティング

### イベントが送信されない場合

1. 測定IDが正しく設定されているか確認
2. ブラウザの開発者ツールでネットワークタブを確認
3. GA4リアルタイムレポートでイベントを確認

### デバッグモード

開発中にイベント送信を確認するには：

```typescript
// src/utils/analytics.ts にデバッグログを追加
console.log('GA Event:', action, parameters);
```

## 拡張機能

### 追加のトラッキング

必要に応じて以下のイベントを追加できます：

- ユーザー登録
- パスワードリセット
- 招待コード作成/使用
- エラートラッキング
- パフォーマンス監視

### A/Bテスト

GA4の機能を使用して、UI/UXの改善をテストできます。

## 参考リンク

- [Google Analytics 4 公式ドキュメント](https://developers.google.com/analytics/devguides/collection/ga4)
- [GA4イベントリファレンス](https://developers.google.com/analytics/devguides/collection/ga4/reference/events)
- [Next.js Analyticsガイド](https://nextjs.org/docs/app/building-your-application/optimizing/analytics)