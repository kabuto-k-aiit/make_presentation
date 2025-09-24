import google.generativeai as genai
import json
import os
import time
import re
import glob
import threading
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from routers import password_reset
from routers.invite_codes import router as invite_router
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import SessionLocal, engine
from models.user import Base, User
from auth.security import (
    verify_password, get_password_hash, create_access_token, create_refresh_token,
    check_login_attempts, increment_login_attempts, reset_login_attempts,
    get_remaining_lockout_time, log_security_event, verify_refresh_token,
    invalidate_refresh_token, get_current_user, get_db
)
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

# .envファイルから環境変数を読み込む
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# JWT認証関連の設定
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")  # 本番環境では必ず環境変数から読み込む
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # アクセストークンの有効期限（分）

# Pydanticモデル
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    invite_code: str  # 招待コード必須


class Token(BaseModel):
    access_token: str
    token_type: str


# FastAPIアプリケーションの初期化
app = FastAPI()

# データベース初期化は手動で実行（起動時は無効化）
# Base.metadata.create_all(bind=engine)
print("⚠️  注意: テーブル作成は init_database.py で事前実行済み")

# Redisの設定
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost")

# パスワードリセットルーターの追加
app.include_router(password_reset.router, prefix="/auth", tags=["auth"])
app.include_router(invite_router, prefix="/api", tags=["invite"])

@app.on_event("startup")
async def startup():
    # Redisクライアントの初期化（一時的に無効化）
    try:
        redis_client = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(redis_client)
        print("✅ Redis Rate Limiter initialized")
    except Exception as e:
        print(f"⚠️  Redis initialization failed: {e}")
        print("🔄 Continuing without rate limiting")

# レート制限なしのルート（デバッグ用）
@app.get("/")
async def root():
    return {"message": "Welcome to the Presentation Generator API"}

# ヘルスチェックエンドポイント（Railway用）
@app.get("/health")
async def health_check():
    """簡単なヘルスチェック用エンドポイント"""
    return {"status": "healthy", "message": "API is running"}


# OAuth2スキーマ
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# CORS（クロスオリジン）設定を追加
origins = [
    "http://localhost:3000",    # Next.jsの開発サーバーのURL
    "http://localhost:3001",    # 代替ポート
    "http://127.0.0.1:3000",   # localhost の IP アドレス版
    "*"                        # 開発中は全てのオリジンを許可
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    expose_headers=["*"],
    max_age=600,  # プリフライトリクエストのキャッシュ時間（秒）
)

# APIキーを設定
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEYが設定されていません。'.env'ファイルを確認してください。")

# APIキーの形式を確認（最初の10文字のみ表示）
print(f"API Key format check: {GOOGLE_API_KEY[:10]}...")

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    # テスト用の簡単なプロンプトで動作確認
    test_model = genai.GenerativeModel('gemini-1.5-flash')
    test_response = test_model.generate_content("Hello")
    print("API connection test successful")
except Exception as e:
    print(f"API configuration error: {str(e)}")

# 利用可能なモデルをリスト表示
print("Available models:")
for model in genai.list_models():
    print(f"- {model.name} ({model.supported_generation_methods})")

# 出力ディレクトリの設定
OUTPUT_DIR = "output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# スライドのスタイル設定
TITLE_FONT_SIZE = Pt(44)
CONTENT_FONT_SIZE = Pt(24)
SLIDE_MARGIN = Inches(0.5)


# リクエストボディのデータモデルを定義
class SlideRequest(BaseModel):
    theme: str = Field(..., min_length=1)
    slideCount: int = Field(..., ge=1, le=20)  # 1から20枚までに制限


def create_powerpoint(slides_data, theme):
    """PowerPointファイルを作成する関数"""
    prs = Presentation()
    
    # タイトルスライドの作成
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    
    title.text = theme
    subtitle.text = "自動生成されたプレゼンテーション"
    
    # コンテンツスライドの作成
    for slide_data in slides_data:
        content_slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(content_slide_layout)
        
        # タイトルの設定
        title = slide.shapes.title
        title.text = slide_data["title"]
        
        # 本文の設定
        body = slide.placeholders[1]
        tf = body.text_frame
        
        # 箇条書きの追加
        for i, content_item in enumerate(slide_data["content"]):
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text = content_item
            p.level = 0
    
    # ファイルの保存
    filename = f"presentation_{int(time.time())}.pptx"
    filepath = os.path.join(OUTPUT_DIR, filename)
    prs.save(filepath)
    print(f"PowerPoint file saved at: {filepath}")  # デバッグ用ログ
    return filename  # パスではなくファイル名のみを返す


def cleanup_old_files():
    """2時間以上古いPowerPointファイルを削除（容量節約のため）"""
    try:
        current_time = time.time()
        deleted_count = 0
        for filename in os.listdir(OUTPUT_DIR):
            if filename.endswith('.pptx'):
                filepath = os.path.join(OUTPUT_DIR, filename)
                if os.path.isfile(filepath):
                    file_age = current_time - os.path.getctime(filepath)
                    # 2時間以上古いファイルを削除（容量節約）
                    if file_age > (2 * 3600):
                        os.remove(filepath)
                        deleted_count += 1
                        print(f"Deleted old file: {filename}")
        
        if deleted_count > 0:
            print(f"Cleanup completed: {deleted_count} files deleted")
    except Exception as e:
        print(f"Error during cleanup: {e}")


# ファイルダウンロード用エンドポイント
@app.get("/download/{filename}")
async def download_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    # ファイル名から'output/'を取り除く
    clean_filename = filename.replace('output/', '')
    file_path = os.path.join(OUTPUT_DIR, clean_filename)
    print(f"Attempting to serve file: {file_path}")  # デバッグ用ログ
    if os.path.exists(file_path):
        return FileResponse(
            file_path,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            filename=clean_filename
        )
    raise HTTPException(status_code=404, detail="ファイルが見つかりません")

# 認証エンドポイント
@app.post("/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # 招待コード検証
    from models.invite_codes import InviteCode
    invite = db.query(InviteCode).filter(
        InviteCode.code == user.invite_code,
        InviteCode.is_used.is_(False)
    ).first()
    
    if not invite:
        raise HTTPException(
            status_code=400,
            detail="無効な招待コードです"
        )
    
    if invite.expires_at and invite.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="招待コードの有効期限が切れています"
        )
    
    # ユーザー数制限チェック（50人まで）
    user_count = db.query(User).count()
    if user_count >= 50:
        raise HTTPException(
            status_code=429,
            detail="登録可能なユーザー数の上限に達しています"
        )
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="このメールアドレスは既に登録されています"
        )
    
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="このユーザー名は既に使用されています"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 招待コードを使用済みにマーク
    invite.is_used = True
    invite.used_by_email = user.email
    invite.used_at = datetime.utcnow()
    db.commit()
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/token", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # ログイン試行回数をチェック
    if not check_login_attempts(form_data.username):
        remaining_time = get_remaining_lockout_time(form_data.username)
        raise HTTPException(
            status_code=429,
            detail=f"アカウントがロックされています。{remaining_time}秒後に再試行してください。"
        )

    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        # ログイン失敗を記録
        increment_login_attempts(form_data.username)
        log_security_event(
            "login_failed",
            form_data.username,
            "ユーザー名またはパスワードが間違っています",
            request.client.host
        )
        raise HTTPException(
            status_code=400,
            detail="ユーザー名またはパスワードが間違っています"
        )
    
    # ログイン成功：試行回数をリセット
    reset_login_attempts(form_data.username)
    log_security_event(
        "login_success",
        user.username,
        "ログイン成功",
        request.client.host
    )

    # アクセストークンとリフレッシュトークンを生成
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@app.post("/refresh", response_model=Token)
async def refresh_token(request: Request, current_token: str):
    """リフレッシュトークンを使用して新しいアクセストークンを取得する"""
    username = verify_refresh_token(current_token)
    if not username:
        log_security_event(
            "token_refresh_failed",
            "unknown",
            "無効なリフレッシュトークン",
            request.client.host
        )
        raise HTTPException(
            status_code=401,
            detail="無効なリフレッシュトークンです"
        )

    # 現在のリフレッシュトークンを無効化
    invalidate_refresh_token(current_token)

    # 新しいトークンを生成
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": username})

    log_security_event(
        "token_refresh_success",
        username,
        "トークン更新成功",
        request.client.host
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# スライド生成APIエンドポイント（レート制限: 3回/時間）
@app.post("/generate-slides")
async def generate_slides(
    request: SlideRequest,
    current_user: User = Depends(get_current_user),
    rate_limit: bool = Depends(RateLimiter(times=3, hours=1))
):
    try:
        # 古いファイルを削除
        cleanup_old_files()
        
        # Gemini API key check
        print(f"API Key exists: {bool(GOOGLE_API_KEY)}")
        if not GOOGLE_API_KEY:
            raise HTTPException(status_code=500, detail="APIキーが設定されていません")

        # リクエストデータのログ出力
        print(f"Received request - Theme: {request.theme}, Slide Count: {request.slideCount}")

        # プロンプトを設定
        prompt = f"""
あなたは優秀なプレゼンテーション専門家です。
以下のテーマと要件に基づいて、プロフェッショナルなプレゼンテーションの構成と内容を作成してください。

**テーマ:** {request.theme}

**目的:** 企業の経営層に対し、AI導入の価値と具体的なメリットを伝え、導入検討を促す。

**ターゲット:** AIに関する専門知識が少ない企業の経営層

**要件:**
* 全{request.slideCount}枚のスライドで構成してください。
* 各スライドは以下のJSON形式で返してください：
{{
  "slides": [
    {{
      "title": "スライドのタイトル",
      "content": ["箇条書きの内容1", "箇条書きの内容2"]
    }}
  ]
}}

以上の要件に基づいて、具体的で説得力のあるプレゼンテーションの内容を、指定された形式のJSONで生成してください。
"""

        # Gemini APIを呼び出し
        print("Initializing Gemini model...")
        # より軽量なモデルを使用
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("Generating content with Gemini API...")
        max_retries = 3
        retry_delay = 20  # 秒
        attempt = 0

        while attempt < max_retries:
            try:
                response = model.generate_content(prompt)
                print(f"Received response from Gemini API: {response.text[:100]}...")
                break  # 成功したらループを抜ける
            except Exception as api_error:
                error_str = str(api_error)
                print(f"Error calling Gemini API: {error_str}")
                
                # レート制限エラーの場合
                if "429" in error_str and attempt < max_retries - 1:
                    retry_seconds = 20
                    if "retry_delay" in error_str:
                        # エラーメッセージから待機時間を抽出
                        delay_match = re.search(r'retry in (\d+\.?\d*)', error_str)
                        if delay_match:
                            retry_seconds = float(delay_match.group(1))
                    
                    print(f"Rate limit exceeded. Waiting {retry_seconds} seconds before retry...")
                    time.sleep(retry_seconds)
                    attempt += 1
                    continue
                
                raise HTTPException(
                    status_code=500,
                    detail=f"Gemini APIの呼び出しに失敗しました: {error_str}"
                )
        
        if not response.text:
            print("Empty response from API")
            raise HTTPException(
                status_code=500,
                detail="APIからの応答が空でした"
            )

        # レスポンステキストからJSONを抽出
        try:
            # JSONブロックを探す
            json_text = response.text
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            elif "```" in json_text:
                json_text = json_text.split("```")[1].strip()
            
            slide_data = json.loads(json_text)
            
            # 基本的な検証
            if not isinstance(slide_data, dict) or "slides" not in slide_data:
                raise ValueError("Invalid JSON structure")
            # PowerPointファイルの生成
            pptx_file = create_powerpoint(slide_data["slides"], request.theme)
                
            return {
                "message": "スライド生成用のデータが正常に作成されました。",
                "data": slide_data,
                "pptxFile": pptx_file
            }
            
        except json.JSONDecodeError as je:
            raise HTTPException(
                status_code=500,
                detail=f"JSONの解析に失敗しました: {str(je)}"
            )
        except ValueError as ve:
            raise HTTPException(
                status_code=500,
                detail=f"無効なデータ構造です: {str(ve)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"予期せぬエラーが発生しました: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)