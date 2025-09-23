from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from backend.database import Base


class InviteCode(Base):
    __tablename__ = "invite_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    is_used = Column(Boolean, default=False)
    used_by_email = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(String(100), default="admin")
    max_uses = Column(Integer, default=1)  # 1回のみ使用可能
    expires_at = Column(DateTime(timezone=True), nullable=True)