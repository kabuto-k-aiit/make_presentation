from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import uuid
import redis

load_dotenv()

# 設定
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "your-refresh-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

# Redis接続
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=0,
    decode_responses=True
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    to_encode["jti"] = str(uuid.uuid4())  # JWT IDを追加
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    to_encode["jti"] = str(uuid.uuid4())
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_refresh_token(refresh_token: str) -> Optional[str]:
    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        jti: str = payload.get("jti")
        
        # トークンが無効化リストに含まれていないか確認
        if redis_client.sismember("invalid_refresh_tokens", jti):
            return None
            
        return username
    except JWTError:
        return None


def invalidate_refresh_token(refresh_token: str) -> None:
    """リフレッシュトークンを無効化する"""
    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if jti:
            # 無効化リストに追加（トークンの有効期限まで保持）
            exp = payload.get("exp")
            if exp:
                ttl = exp - datetime.utcnow().timestamp()
                if ttl > 0:
                    redis_client.sadd("invalid_refresh_tokens", jti)
                    redis_client.expire("invalid_refresh_tokens", int(ttl))
    except JWTError:
        pass


def check_login_attempts(username: str) -> bool:
    """ログイン試行回数をチェックする"""
    key = f"login_attempts:{username}"
    attempts = redis_client.get(key)
    
    if attempts is None:
        return True
    
    if int(attempts) >= MAX_LOGIN_ATTEMPTS:
        return False
        
    return True


def increment_login_attempts(username: str) -> None:
    """ログイン試行回数を増やす"""
    key = f"login_attempts:{username}"
    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, LOCKOUT_DURATION_MINUTES * 60)  # 15分後に自動リセット
    pipe.execute()


def reset_login_attempts(username: str) -> None:
    """ログイン試行回数をリセットする"""
    key = f"login_attempts:{username}"
    redis_client.delete(key)


def get_remaining_lockout_time(username: str) -> int:
    """アカウントロックアウトの残り時間（秒）を取得する"""
    key = f"login_attempts:{username}"
    return redis_client.ttl(key)


def log_security_event(event_type: str, username: str, details: str, ip_address: str) -> None:
    """セキュリティイベントをログに記録する"""
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "username": username,
        "details": details,
        "ip_address": ip_address
    }
    # セキュリティログをRedisリストに追加
    redis_client.lpush("security_logs", str(event))
    # 最大1万件までログを保持
    redis_client.ltrim("security_logs", 0, 9999)