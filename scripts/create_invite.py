#!/usr/bin/env python3
"""
管理者用招待コード発行スクリプト
新しいユーザーを招待するための招待コードを生成します
"""
import os
import sys
import secrets
from datetime import datetime, timedelta
from pathlib import Path

# バックエンドのパスを追加
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.invite_codes import InviteCode


def create_invite_code(expires_hours=168, description=""):
    """招待コードを作成"""
    
    # 環境変数から接続文字列を取得
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL環境変数が設定されていません")
        return False
    
    try:
        # エンジンとセッションを作成
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # 招待コード生成（12文字の安全なランダム文字列）
        code = secrets.token_urlsafe(12)
        expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
        
        # 招待コードオブジェクト作成
        invite = InviteCode(
            code=code,
            expires_at=expires_at,
            created_by="admin_script"
        )
        
        # データベースに保存
        db.add(invite)
        db.commit()
        db.refresh(invite)
        
        print("✅ 招待コードが正常に作成されました！")
        print("=" * 50)
        print(f"📋 招待コード: {code}")
        print(f"⏰ 有効期限: {expires_at} UTC")
        print(f"⌛ 有効時間: {expires_hours}時間")
        if description:
            print(f"📝 説明: {description}")
        print("=" * 50)
        print("\n📤 この招待コードをユーザーに共有してください")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False


def list_invite_codes():
    """現在の招待コード一覧を表示"""
    
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL環境変数が設定されていません")
        return False
    
    try:
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # 全ての招待コードを取得
        invites = db.query(InviteCode).order_by(InviteCode.created_at.desc()).all()
        
        if not invites:
            print("📭 招待コードはまだ作成されていません")
            return True
        
        print(f"📋 招待コード一覧 ({len(invites)}個)")
        print("=" * 80)
        
        for invite in invites:
            status = "❌ 使用済み" if invite.is_used else "✅ 有効"
            if invite.expires_at and invite.expires_at < datetime.utcnow():
                status = "⏰ 期限切れ"
            
            print(f"コード: {invite.code}")
            print(f"ステータス: {status}")
            print(f"作成日時: {invite.created_at}")
            print(f"有効期限: {invite.expires_at}")
            if invite.is_used:
                print(f"使用者: {invite.used_by_email}")
                print(f"使用日時: {invite.used_at}")
            print("-" * 40)
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False


def main():
    print("🎫 招待コード管理ツール")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python scripts/create_invite.py create [時間] [説明]")
        print("  python scripts/create_invite.py list")
        print("")
        print("例:")
        print("  python scripts/create_invite.py create 168 '友人用'")
        print("  python scripts/create_invite.py create 72")
        print("  python scripts/create_invite.py list")
        return
    
    command = sys.argv[1]
    
    if command == "create":
        expires_hours = 168  # デフォルト1週間
        description = ""
        
        if len(sys.argv) > 2:
            try:
                expires_hours = int(sys.argv[2])
            except ValueError:
                print("❌ 有効時間は数値で指定してください")
                return
        
        if len(sys.argv) > 3:
            description = sys.argv[3]
        
        create_invite_code(expires_hours, description)
        
    elif command == "list":
        list_invite_codes()
        
    else:
        print(f"❌ 不明なコマンド: {command}")
        print("利用可能なコマンド: create, list")


if __name__ == "__main__":
    main()