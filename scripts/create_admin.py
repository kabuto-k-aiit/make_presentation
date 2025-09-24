#!/usr/bin/env python3
"""
管理者ユーザーと初期招待コードを作成するスクリプト
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# バックエンドのパスを追加
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

from database import SessionLocal, engine
from models.user import Base, User
from models.password_reset import PasswordReset
from models.invite_codes import InviteCode
from auth.security import get_password_hash

def create_admin_and_invite():
    """管理者ユーザーと初期招待コードを作成"""
    
    # DATABASE_URLを明示的に設定
    os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@db:5432/presentation_db'
    
    # セッション作成
    db = SessionLocal()
        # 管理者ユーザーが既に存在するか確認
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("✅ 管理者ユーザーは既に存在します")
            admin_user = existing_admin
        else:
            # 管理者ユーザー作成
            hashed_password = get_password_hash("admin123!@#")
            admin_user = User(
                email="admin@example.com",
                username="admin",
                hashed_password=hashed_password
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("✅ 管理者ユーザーを作成しました: admin / admin123!@#")

        # 初期招待コードが既に存在するか確認
        existing_invite = db.query(InviteCode).filter(InviteCode.code == "ADMIN2025").first()
        if existing_invite:
            print("✅ 初期招待コードは既に存在します")
        else:
            # 初期招待コード作成
            expires_at = datetime.utcnow() + timedelta(days=365)  # 1年間有効
            invite_code = InviteCode(
                code="ADMIN2025",
                expires_at=expires_at,
                created_by=admin_user.email
            )
            db.add(invite_code)
            db.commit()
            print("✅ 初期招待コードを作成しました: ADMIN2025")

        # 現在のユーザー一覧を表示
        users = db.query(User).all()
        print(f"\n👥 現在のユーザー一覧 ({len(users)}人):")
        for user in users:
            print(f"   - ID: {user.id}, Username: {user.username}, Email: {user.email}")

        # 現在の招待コード一覧を表示
        invites = db.query(InviteCode).all()
        print(f"\n🎫 現在の招待コード一覧 ({len(invites)}個):")
        for invite in invites:
            status = "✅ 使用済み" if invite.is_used else "⏳ 未使用"
            print(f"   - Code: {invite.code}, Status: {status}, Expires: {invite.expires_at}")

        print("\n🎉 セットアップ完了！")

    except Exception as e:
        print(f"❌ エラー: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 管理者ユーザーと初期招待コード作成スクリプト開始")
    print("=" * 60)

    create_admin_and_invite()