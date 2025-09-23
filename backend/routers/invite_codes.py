from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
from backend.database import get_db
from backend.models.invite_codes import InviteCode
from backend.models.user import User
from backend.auth.security import get_current_user
from pydantic import BaseModel


router = APIRouter(prefix="/invite", tags=["invite"])


class InviteCodeVerify(BaseModel):
    code: str


class InviteCodeCreate(BaseModel):
    expires_hours: int = 168  # デフォルト1週間


@router.post("/verify")
async def verify_invite_code(
    invite_data: InviteCodeVerify,
    db: Session = Depends(get_db)
):
    """招待コードの有効性を確認"""
    invite = db.query(InviteCode).filter(
        InviteCode.code == invite_data.code,
        InviteCode.is_used.is_(False)
    ).first()
    
    if not invite:
        raise HTTPException(
            status_code=400,
            detail="Invalid invite code"
        )
    
    if invite.expires_at and invite.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="Invite code has expired"
        )
    
    return {
        "valid": True,
        "message": "Invite code is valid",
        "code": invite_data.code
    }


@router.post("/create")
async def create_invite_code(
    invite_data: InviteCodeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """新しい招待コードを作成（管理者のみ）"""
    # 管理者チェック（ここでは最初のユーザーを管理者とする）
    first_user = db.query(User).first()
    if not first_user or current_user.id != first_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only admin can create invite codes"
        )
    
    # 招待コード生成
    code = secrets.token_urlsafe(12)
    expires_at = datetime.utcnow() + timedelta(hours=invite_data.expires_hours)
    
    invite = InviteCode(
        code=code,
        expires_at=expires_at,
        created_by=current_user.email
    )
    
    db.add(invite)
    db.commit()
    db.refresh(invite)
    
    return {
        "invite_code": code,
        "expires_at": expires_at,
        "created_by": current_user.email
    }


@router.get("/list")
async def list_invite_codes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """招待コード一覧（管理者のみ）"""
    # 管理者チェック
    first_user = db.query(User).first()
    if not first_user or current_user.id != first_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only admin can view invite codes"
        )
    
    invites = db.query(InviteCode).order_by(InviteCode.created_at.desc()).all()
    
    return {
        "invite_codes": [
            {
                "id": invite.id,
                "code": invite.code,
                "is_used": invite.is_used,
                "used_by_email": invite.used_by_email,
                "created_at": invite.created_at,
                "expires_at": invite.expires_at,
                "created_by": invite.created_by
            }
            for invite in invites
        ]
    }


def use_invite_code(code: str, user_email: str, db: Session):
    """招待コードを使用済みにマーク"""
    invite = db.query(InviteCode).filter(
        InviteCode.code == code,
        InviteCode.is_used.is_(False)
    ).first()
    
    if invite:
        invite.is_used = True
        invite.used_by_email = user_email
        invite.used_at = datetime.utcnow()
        db.commit()
        return True
    
    return False