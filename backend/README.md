# make_presentation

プレゼン資料の作成

### python 環境の構築

```
python -m venv venv
```

立ち上げ

```
source venv/bin/activate
```
終了
```
deactivate
```

ライブラリのインストール
```
pip install -r requirements.txt
```
ライブラリを追加した後に実行
```
pip freeze > requirements.txt
```

サーバー起動
```
uvicorn main:app --reload
```