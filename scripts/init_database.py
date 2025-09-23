#!/usr/bin/env python3
"""
データベース初期化スクリプト
Supabaseに必要なテーブルを作成します
"""
import os
import sys
from pathlib import Path

# バックエンドのパスを追加
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

from sqlalchemy import create_engine, text
from database import Base
from models.user import User
from models.password_reset import PasswordReset
from models.invite_codes import InviteCode


def init_database():
    """データベースを初期化してテーブルを作成"""
    
    # 環境変数から接続文字列を取得
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL環境変数が設定されていません")
        print("例: export DATABASE_URL='postgresql://postgres:password@db.xxx.supabase.co:5432/postgres'")
        return False
    
    try:
        print(f"🔄 データベースに接続中...")
        
        # エンジンを作成
        engine = create_engine(database_url)
        
        # 接続テスト
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()
            print(f"✅ 接続成功: {version[0][:50]}...")
        
        print(f"🏗️ テーブル作成中...")
        
        # 全テーブルを作成
        Base.metadata.create_all(bind=engine)
        
        # 作成されたテーブルを確認
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = result.fetchall()
            
            print(f"✅ テーブル作成完了!")
            print(f"📊 作成されたテーブル ({len(tables)}個):")
            for table in tables:
                print(f"   📝 {table[0]}")
        
        # テーブル構造を確認
        print(f"\n🔍 テーブル構造確認:")
        
        for table_name in ['app_users', 'password_resets', 'invite_codes']:
            print(f"\n📋 {table_name} テーブル:")
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position
                """))
                columns = result.fetchall()
                
                for col in columns:
                    nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                    default = f"DEFAULT {col[3]}" if col[3] else ""
                    print(f"   - {col[0]}: {col[1]} {nullable} {default}")
        
        print(f"\n🎉 データベース初期化が完了しました！")
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        print("\n🔧 確認事項:")
        print("1. DATABASE_URL が正しく設定されているか")
        print("2. データベースに接続できるか")
        print("3. 必要な権限があるか")
        return False


if __name__ == "__main__":
    print("🚀 データベース初期化スクリプト開始")
    print("=" * 50)
    
    success = init_database()
    
    if success:
        print("\n✨ 準備完了！アプリケーションを起動できます")
    else:
        print("\n💡 エラーを修正して再度実行してください")
        sys.exit(1)