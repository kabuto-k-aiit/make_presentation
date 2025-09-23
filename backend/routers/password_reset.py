from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.password_reset import PasswordReset
from auth.security import get_password_hash
from uuid import uuid4
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# メール送信の設定
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

async def send_reset_email(email: str, token: str):
    """パスワードリセットメールを送信する"""
    message = MIMEMultipart()
    message["From"] = SMTP_USER
    message["To"] = email
    message["Subject"] = "パスワードリセットのご案内"

    reset_url = f"{FRONTEND_URL}/reset-password/{token}"
    body = f"""
    パスワードリセットのリクエストを受け付けました。

    以下のリンクをクリックしてパスワードをリセットしてください：
    {reset_url}

    このリンクは1時間のみ有効です。

    このメールに心当たりがない場合は、無視していただいて構いません。
    """

    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(message)
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise HTTPException(status_code=500, detail="メールの送信に失敗しました")

@router.post("/forgot-password")
async def forgot_password(email: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """パスワードリセットのリクエストを処理する"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # ユーザーが存在しない場合も成功を返す（セキュリティのため）
        return {"message": "パスワードリセットの手順をメールで送信しました"}

    # 既存のリセットトークンを削除
    db.query(PasswordReset).filter(PasswordReset.user_id == user.id).delete()

    # 新しいリセットトークンを作成
    reset_token = str(uuid4())
    password_reset = PasswordReset(
        user_id=user.id,
        token=reset_token,
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )

    db.add(password_reset)
    db.commit()

    # バックグラウンドでメール送信
    background_tasks.add_task(send_reset_email, email, reset_token)

    return {"message": "パスワードリセットの手順をメールで送信しました"}

@router.post("/reset-password/{token}")
async def reset_password(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    """パスワードリセットを実行する"""
    reset_record = db.query(PasswordReset).filter(
        PasswordReset.token == token
    ).first()

    if not reset_record or reset_record.is_expired:
        raise HTTPException(
            status_code=400,
            detail="無効または期限切れのトークンです"
        )

    # パスワードの強度チェック（フロントエンドと同じルール）
    if len(new_password) < 8:
        raise HTTPException(
            status_code=400,
            detail="パスワードは8文字以上である必要があります"
        )

    if not any(c.isupper() for c in new_password):
        raise HTTPException(
            status_code=400,
            detail="パスワードは少なくとも1つの大文字を含む必要があります"
        )

    if not any(c.islower() for c in new_password):
        raise HTTPException(
            status_code=400,
            detail="パスワードは少なくとも1つの小文字を含む必要があります"
        )

    if not any(c.isdigit() for c in new_password):
        raise HTTPException(
            status_code=400,
            detail="パスワードは少なくとも1つの数字を含む必要があります"
        )

    if not any(c in "!@#$%^&*(),.?\":{}|<>" for c in new_password):
        raise HTTPException(
            status_code=400,
            detail="パスワードは少なくとも1つの特殊文字を含む必要があります"
        )

    # パスワードをハッシュ化して更新
    user = reset_record.user
    user.hashed_password = get_password_hash(new_password)

    # リセットトークンを削除
    db.delete(reset_record)
    db.commit()

    return {"message": "パスワードが正常にリセットされました"}