# Git コミットメッセージテンプレートガイド

このプロジェクトでは、統一されたコミットメッセージ形式を使用しています。

## 設定方法

### 1. テンプレートの設定

プロジェクトルートで以下のコマンドを実行：

```bash
git config commit.template .gitmessage
```

### 2. コミット時の使用

```bash
git commit
# エディタが開き、テンプレートが表示されます
```

または手動でメッセージを指定：

```bash
git commit -m "コミットメッセージ"
```

## コミットメッセージ形式

```
<type>: <subject>
## <変更の概要>
### <ファイルパス>
- <具体的な変更内容>
- <具体的な変更内容>

### <ファイルパス>
- <具体的な変更内容>

## 影響範囲
- <影響する機能や範囲>

## <その他のセクション（必要に応じて）>
- <追加の詳細情報>

## ユーザー体験向上/システム改善
- <変更によるメリットや効果>
```

### Type の種類

| Type | 説明 | 例 |
|------|------|-----|
| `feat` | 新機能 | `feat: ユーザー登録機能を追加` |
| `fix` | バグ修正 | `fix: ログインエラーを修正` |
| `docs` | ドキュメント | `docs: README更新` |
| `style` | フォーマット | `style: コードフォーマット統一` |
| `refactor` | リファクタリング | `refactor: 認証ロジックの整理` |
| `perf` | パフォーマンス | `perf: DB クエリの最適化` |
| `test` | テスト | `test: ユニットテスト追加` |
| `chore` | その他 | `chore: 依存関係の更新` |

## セクション別ガイドライン

### ## <変更の概要>
- 変更の大きなカテゴリを記述
- 例：「バックエンドエラーメッセージ日本語化」「認証システム強化」

### ### <ファイルパス>
- 具体的なファイル名を記述
- 相対パスで記載（例：`backend/main.py`）

### - <具体的な変更内容>
- 変更前後の詳細を記述
- 例：`'Error' → 'エラーが発生しました'`
- 新機能の場合は機能の詳細を記述

### ## 影響範囲
- この変更が影響する機能やシステム部分
- ユーザーに見える影響
- 他のシステムへの影響

### ## ユーザー体験向上/システム改善
- 変更による効果や利点
- ユーザーにとってのメリット
- システム全体への改善効果

## 実例

```
feat: ログイン等のエラーメッセージを全て日本語化
## バックエンドエラーメッセージ日本語化
### backend/main.py
- ファイルダウンロードエラー: 'File not found' → 'ファイルが見つかりません'
- API設定エラー: 'API key is not configured' → 'APIキーが設定されていません'
- セキュリティログメッセージ日本語化:
  - 'Invalid username or password' → 'ユーザー名またはパスワードが間違っています'
  - 'Successful login' → 'ログイン成功'
  - 'Invalid refresh token' → '無効なリフレッシュトークン'
  - 'Token refreshed successfully' → 'トークン更新成功'

### backend/routers/invite_codes.py
- 招待コード検証成功メッセージ: 'Invite code is valid' → '招待コードは有効です'

## フロントエンドエラーメッセージ日本語化
### frontend/src/store/authSlice.ts
- ユーザー登録失敗: 'Registration failed' → 'ユーザー登録に失敗しました'
- ログイン失敗: 'Login failed' → 'ログインに失敗しました'
- トークン更新失敗: 'Token refresh failed' → 'トークンの更新に失敗しました'

## 影響範囲
- ユーザー認証関連の全エラーメッセージ
- APIエラーレスポンス
- セキュリティイベントログ
- プレゼンテーション生成エラー

## 確認済み日本語化済みファイル
- backend/auth/security.py: 既に日本語化済み
- backend/routers/password_reset.py: 既に日本語化済み
- frontend/src/utils/passwordValidation.ts: 既に日本語化済み
- frontend/src/store/presentationSlice.ts: 既に日本語化済み

## ユーザー体験向上
- 全てのエラーメッセージが日本語で表示されるため、ユーザーが理解しやすい
- セキュリティログも日本語で記録され、管理が容易
```

## 注意事項

- 不要なセクションは削除してください
- 各項目は具体的に記述してください
- 変更の影響や目的を最後に記載してください
- 50文字以内の簡潔な subject を心がけてください

## VSCode での設定

VSCode を使用している場合、以下の設定でより便利に使用できます：

```json
{
  "git.inputValidation": "warn",
  "git.inputValidationLength": 50,
  "git.inputValidationSubjectLength": 50
}
```