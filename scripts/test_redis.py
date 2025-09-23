#!/usr/bin/env python3
"""
Upstash Redis接続テストスクリプト
"""
import os
import sys
import redis
from pathlib import Path
from dotenv import load_dotenv


def test_redis_connection():
    """Redis接続をテスト"""
    # .envファイルから環境変数をロード
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
    
    # 環境変数から接続情報を取得
    redis_url = os.getenv('REDIS_URL')
    redis_host = os.getenv('REDIS_HOST')
    redis_port = os.getenv('REDIS_PORT')
    redis_password = os.getenv('REDIS_PASSWORD')
    
    if not redis_url:
        print("❌ REDIS_URL環境変数が設定されていません")
        print("例: REDIS_URL='rediss://:password@endpoint:6380'")
        return False
    
    try:
        print(f"🔄 Redis接続テスト中...")
        print(f"📍 Host: {redis_host}")
        print(f"🔌 Port: {redis_port}")
        
        # Redis クライアント作成
        redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            ssl_cert_reqs=None  # Upstash用SSL設定
        )
        
        # 接続テスト
        redis_client.ping()
        print("✅ Redis接続成功!")
        
        # 基本的な操作テスト
        print("\n🧪 基本操作テスト:")
        
        # SET/GET テスト
        test_key = "test:connection"
        test_value = "Hello Upstash Redis!"
        
        redis_client.set(test_key, test_value, ex=30)  # 30秒で期限切れ
        retrieved_value = redis_client.get(test_key)
        
        if retrieved_value == test_value:
            print(f"✅ SET/GET 成功: {retrieved_value}")
        else:
            print(f"❌ SET/GET 失敗")
            return False
        
        # Redis情報取得
        info = redis_client.info()
        print(f"📊 Redis Version: {info.get('redis_version', 'Unknown')}")
        print(f"📝 Used Memory: {info.get('used_memory_human', 'Unknown')}")
        print(f"🔗 Connected Clients: {info.get('connected_clients', 'Unknown')}")
        
        # キー数確認
        db_size = redis_client.dbsize()
        print(f"🗃️ 総キー数: {db_size}")
        
        # テストキーを削除
        redis_client.delete(test_key)
        print("🧹 テストキー削除完了")
        
        return True
        
    except redis.ConnectionError as e:
        print(f"❌ Redis接続エラー: {e}")
        print("\n🔧 確認事項:")
        print("1. REDIS_URL が正しく設定されているか")
        print("2. Upstashでデータベースが作成されているか")
        print("3. ネットワーク接続が有効か")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Upstash Redis接続テスト開始")
    print("=" * 50)
    
    success = test_redis_connection()
    
    if success:
        print("\n🎉 全ての Redis テストが完了しました！")
        print("💡 Redis は正常に動作しています")
    else:
        print("\n💡 設定を確認して再度お試しください")
        sys.exit(1)