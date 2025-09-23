# パスワードリセットトークンの生成と保存のためのモデル
from datetime import datetime, timedelta
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from database import Base

class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("app_users.id"), nullable=False)
    token = Column(String(100), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="password_resets")

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at