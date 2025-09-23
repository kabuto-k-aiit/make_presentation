#!/usr/bin/env python3
"""
Supabase接続テストスクリプト
"""
import os
import sys
import psycopg2
from pathlib import Path
from dotenv import load_dotenv


def test_supabase_connection():
    # .envファイルから環境変数をロード
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
    
    # 環境変数から接続文字列を取得
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL環境変数が設定されていません")
        print("例: export DATABASE_URL='postgresql://postgres:password@db.xxx.supabase.co:5432/postgres'")
        return False
    
    try:
        print(f"🔄 接続テスト中: {database_url[:50]}...")
        
        # データベースに接続
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # 簡単なクエリを実行
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"✅ 接続成功!")
        print(f"📊 PostgreSQL Version: {version[0][:100]}")
        
        # テーブル一覧を取得
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        print(f"📝 既存テーブル数: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        print("\n🔧 確認事項:")
        print("1. PROJECT-REF が正しいか")
        print("2. PASSWORD が正しいか") 
        print("3. ネットワーク接続が有効か")
        return False

if __name__ == "__main__":
    print("🚀 Supabase接続テスト開始")
    print("=" * 50)
    
    success = test_supabase_connection()
    
    if success:
        print("\n🎉 全ての接続テストが完了しました！")
    else:
        print("\n💡 接続情報を確認して再度お試しください")
        sys.exit(1)