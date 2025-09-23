# 無料プラン制限と対策

## 🚨 制限事項

### Railway ($5クレジット/月)
- **制限**: 約150時間稼働、1GB ストレージ
- **対策**: 
  - アイドル時自動スリープ
  - 古いPowerPointファイルの定期削除
  - 効率的なリソース使用
  - ファイル生成後の一定期間での自動削除

### Supabase
- **制限**: 500MB DB、2GB転送/月
- **対策**:
  - 定期的なデータクリーンアップ
  - 画像は外部ストレージ使用
  - インデックス最適化

### Upstash Redis
- **制限**: 10,000コマンド/日
- **対策**:
  - TTL設定でメモリ効率化
  - 重要なデータのみキャッシュ
  - バッチ処理で最適化

## 📁 ファイル管理戦略

### PowerPointファイルの保存
- **場所**: Railway内ローカルストレージ
- **容量**: 1GB制限
- **対策**:
  ```python
  # 自動削除スクリプト例
  import os
  import time
  
  def cleanup_old_files(directory, max_age_hours=24):
      current_time = time.time()
      for filename in os.listdir(directory):
          filepath = os.path.join(directory, filename)
          if os.path.isfile(filepath):
              file_age = current_time - os.path.getctime(filepath)
              if file_age > (max_age_hours * 3600):
                  os.remove(filepath)
  ```

## 📈 使用量監視

### 監視スクリプト
```python
# monitoring.py
import psutil
import redis
import os

def check_resource_usage():
    # メモリ使用量
    memory = psutil.virtual_memory()
    print(f"Memory: {memory.percent}%")
    
    # Redis使用量
    r = redis.from_url(os.getenv("REDIS_URL"))
    info = r.info()
    print(f"Redis Memory: {info['used_memory_human']}")
    
    # Database size (要Supabase API)
    # TODO: Supabase API実装

if __name__ == "__main__":
    check_resource_usage()
```

## 🔄 スケールアップパス

### 有料プランへの移行タイミング
1. **Railway**: $5クレジット不足時 → $20/月
2. **Supabase**: DB容量不足時 → $25/月
3. **Upstash**: Redis制限時 → $10/月
4. **Vercel**: 商用利用時 → $20/月

### 総コスト試算
- 無料: $0/月
- 小規模有料: $75/月
- 中規模有料: $150/月