# 🔒 アクセス制限・リソース保護戦略

## 📊 現在の制限と対策案

### 🚨 無料プラン制限
1. **Railway**: $5クレジット/月（約150時間稼働）
2. **Supabase**: 500MB DB、2GB転送/月
3. **Upstash Redis**: 10,000コマンド/日
4. **Vercel**: 100GB転送/月（実質無制限）

---

## 🛡️ 実装可能な保護機能

### 1. 📧 **招待コード制限**（推奨）
**メリット**: 完全にアクセス制御、容量保護
**実装**: 
- 新規登録時に招待コード必須
- 管理者のみコード発行可能
- コード使用後は無効化

**実装手順**:
1. InviteCode モデル作成 ✅
2. 登録フォームに招待コード入力欄追加
3. バックエンドで招待コード検証
4. 管理者用コード発行機能

### 2. ⏱️ **厳格なレート制限**
**現在**: 10回/分
**提案**: 
- プレゼンテーション生成: 3回/時間
- ログイン試行: 5回/15分
- API全体: 30回/分

### 3. 🏃 **アイドル時自動停止**
**Railway アプリの自動スリープ**:
```python
# 30分間リクエストなしで自動停止
@app.middleware("http")
async def auto_shutdown_middleware(request: Request, call_next):
    global last_request_time
    last_request_time = time.time()
    
    response = await call_next(request)
    return response

# バックグラウンドタスクで監視
async def check_idle_shutdown():
    while True:
        if time.time() - last_request_time > 1800:  # 30分
            # アプリケーション停止ロジック
            pass
        await asyncio.sleep(300)  # 5分ごとにチェック
```

### 4. 📁 **ファイル自動削除**
**PowerPoint ファイルの自動クリーンアップ**:
```python
# 生成後24時間で削除
import os
import time
from datetime import datetime, timedelta

def auto_cleanup_files():
    output_dir = "output"
    current_time = time.time()
    
    for filename in os.listdir(output_dir):
        filepath = os.path.join(output_dir, filename)
        if os.path.isfile(filepath):
            file_age = current_time - os.path.getctime(filepath)
            if file_age > 86400:  # 24時間 = 86400秒
                os.remove(filepath)
                print(f"Deleted old file: {filename}")
```

### 5. 👥 **ユーザー数制限**
**最大登録ユーザー数**: 50人
```python
@app.post("/register")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # ユーザー数確認
    user_count = db.query(User).count()
    if user_count >= 50:
        raise HTTPException(
            status_code=429, 
            detail="Registration limit reached. Please contact admin."
        )
```

### 6. 📈 **使用量監視ダッシュボード**
**リソース使用量を監視**:
```python
@app.get("/admin/stats")
async def get_usage_stats(current_user: User = Depends(get_admin_user)):
    return {
        "total_users": db.query(User).count(),
        "presentations_today": get_daily_presentations(),
        "database_size": get_db_size(),
        "redis_usage": get_redis_usage(),
        "railway_usage": get_railway_usage()
    }
```

---

## 🎯 推奨実装順序

### Phase 1: 招待コード制限（即効性）
1. InviteCode モデル追加
2. 登録時の招待コード検証
3. 管理者用コード発行機能

### Phase 2: レート制限強化
1. プレゼンテーション生成制限
2. ファイルダウンロード制限
3. API全体の制限強化

### Phase 3: 自動化・監視
1. ファイル自動削除
2. 使用量監視
3. アラート設定

---

## 💡 追加のコスト削減策

### 1. **効率的なAI使用**
```python
# リクエスト最適化
def optimize_gemini_request(topic: str, slide_count: int):
    # より短いプロンプトでトークン数削減
    prompt = f"Create {slide_count} slides about {topic}. Be concise."
    return prompt
```

### 2. **キャッシュ活用**
```python
# 類似プレゼンテーションのキャッシュ
@lru_cache(maxsize=100)
def get_cached_presentation(topic_hash: str):
    # Redis でプレゼンテーション内容をキャッシュ
    pass
```

### 3. **圧縮・最適化**
```python
# PowerPoint ファイル圧縮
def compress_pptx(filepath: str):
    # 画像圧縮、不要要素削除
    pass
```

---

## 🔧 実装コード例

### 招待コード検証
```python
@app.post("/verify-invite")
async def verify_invite_code(code: str, db: Session = Depends(get_db)):
    invite = db.query(InviteCode).filter(
        InviteCode.code == code,
        InviteCode.is_used == False
    ).first()
    
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid invite code")
    
    if invite.expires_at and invite.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invite code expired")
    
    return {"valid": True, "message": "Invite code is valid"}
```

### 管理者用招待コード発行
```python
@app.post("/admin/create-invite")
async def create_invite_code(
    expires_hours: int = 168,  # 1週間
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    import secrets
    
    code = secrets.token_urlsafe(12)
    expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
    
    invite = InviteCode(
        code=code,
        expires_at=expires_at,
        created_by=current_user.email
    )
    
    db.add(invite)
    db.commit()
    
    return {"invite_code": code, "expires_at": expires_at}
```

---

どの保護機能から実装しますか？**招待コード制限**が最も効果的でおすすめです！