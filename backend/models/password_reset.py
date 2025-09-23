# パスワードリセットトークンの生成と保存のためのモデル
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    token = Column(String(100), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="password_resets")

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at