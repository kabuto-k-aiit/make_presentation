import google.generativeai as genai
import json
import os
import time
import re
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

# .envファイルから環境変数を読み込む
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# FastAPIアプリケーションの初期化
app = FastAPI()

# CORS（クロスオリジン）設定を追加
origins = [
    "http://localhost:3000",    # Next.jsの開発サーバーのURL
    "http://localhost:3001",    # 代替ポート
    "http://127.0.0.1:3000",   # localhost の IP アドレス版
    "*"                        # 開発中は全てのオリジンを許可
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    expose_headers=["*"],
    max_age=600,  # プリフライトリクエストのキャッシュ時間（秒）
)

# APIキーを設定
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEYが設定されていません。'.env'ファイルを確認してください。")

# APIキーの形式を確認（最初の10文字のみ表示）
print(f"API Key format check: {GOOGLE_API_KEY[:10]}...")

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    # テスト用の簡単なプロンプトで動作確認
    test_model = genai.GenerativeModel('gemini-1.5-flash')
    test_response = test_model.generate_content("Hello")
    print("API connection test successful")
except Exception as e:
    print(f"API configuration error: {str(e)}")

# 利用可能なモデルをリスト表示
print("Available models:")
for model in genai.list_models():
    print(f"- {model.name} ({model.supported_generation_methods})")

# 出力ディレクトリの設定
OUTPUT_DIR = "output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# スライドのスタイル設定
TITLE_FONT_SIZE = Pt(44)
CONTENT_FONT_SIZE = Pt(24)
SLIDE_MARGIN = Inches(0.5)


# リクエストボディのデータモデルを定義
class SlideRequest(BaseModel):
    theme: str = Field(..., min_length=1)
    slideCount: int = Field(..., ge=1, le=20)  # 1から20枚までに制限


def create_powerpoint(slides_data, theme):
    """PowerPointファイルを作成する関数"""
    prs = Presentation()
    
    # タイトルスライドの作成
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    
    title.text = theme
    subtitle.text = "自動生成されたプレゼンテーション"
    
    # コンテンツスライドの作成
    for slide_data in slides_data:
        content_slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(content_slide_layout)
        
        # タイトルの設定
        title = slide.shapes.title
        title.text = slide_data["title"]
        
        # 本文の設定
        body = slide.placeholders[1]
        tf = body.text_frame
        
        # 箇条書きの追加
        for i, content_item in enumerate(slide_data["content"]):
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text = content_item
            p.level = 0
    
    # ファイルの保存
    filename = f"presentation_{int(time.time())}.pptx"
    filepath = os.path.join(OUTPUT_DIR, filename)
    prs.save(filepath)
    print(f"PowerPoint file saved at: {filepath}")  # デバッグ用ログ
    return filename  # パスではなくファイル名のみを返す


# ファイルダウンロード用エンドポイント
@app.get("/download/{filename}")
async def download_file(filename: str):
    # ファイル名から'output/'を取り除く
    clean_filename = filename.replace('output/', '')
    file_path = os.path.join(OUTPUT_DIR, clean_filename)
    print(f"Attempting to serve file: {file_path}")  # デバッグ用ログ
    if os.path.exists(file_path):
        return FileResponse(
            file_path,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            filename=clean_filename
        )
    raise HTTPException(status_code=404, detail="File not found")

# APIエンドポイントの定義
@app.post("/generate-slides")
async def generate_slides(request: SlideRequest):
    try:
        # APIキーの存在確認とログ出力
        print(f"API Key exists: {bool(GOOGLE_API_KEY)}")
        if not GOOGLE_API_KEY:
            raise HTTPException(status_code=500, detail="API key is not configured")

        # リクエストデータのログ出力
        print(f"Received request - Theme: {request.theme}, Slide Count: {request.slideCount}")

        # プロンプトを設定
        prompt = f"""
あなたは優秀なプレゼンテーション専門家です。
以下のテーマと要件に基づいて、プロフェッショナルなプレゼンテーションの構成と内容を作成してください。

**テーマ:** {request.theme}

**目的:** 企業の経営層に対し、AI導入の価値と具体的なメリットを伝え、導入検討を促す。

**ターゲット:** AIに関する専門知識が少ない企業の経営層

**要件:**
* 全{request.slideCount}枚のスライドで構成してください。
* 各スライドは以下のJSON形式で返してください：
{{
  "slides": [
    {{
      "title": "スライドのタイトル",
      "content": ["箇条書きの内容1", "箇条書きの内容2"]
    }}
  ]
}}

以上の要件に基づいて、具体的で説得力のあるプレゼンテーションの内容を、指定された形式のJSONで生成してください。
"""

        # Gemini APIを呼び出し
        print("Initializing Gemini model...")
        # より軽量なモデルを使用
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("Generating content with Gemini API...")
        max_retries = 3
        retry_delay = 20  # 秒
        attempt = 0

        while attempt < max_retries:
            try:
                response = model.generate_content(prompt)
                print(f"Received response from Gemini API: {response.text[:100]}...")
                break  # 成功したらループを抜ける
            except Exception as api_error:
                error_str = str(api_error)
                print(f"Error calling Gemini API: {error_str}")
                
                # レート制限エラーの場合
                if "429" in error_str and attempt < max_retries - 1:
                    retry_seconds = 20
                    if "retry_delay" in error_str:
                        # エラーメッセージから待機時間を抽出
                        delay_match = re.search(r'retry in (\d+\.?\d*)', error_str)
                        if delay_match:
                            retry_seconds = float(delay_match.group(1))
                    
                    print(f"Rate limit exceeded. Waiting {retry_seconds} seconds before retry...")
                    time.sleep(retry_seconds)
                    attempt += 1
                    continue
                
                raise HTTPException(
                    status_code=500,
                    detail=f"Gemini APIの呼び出しに失敗しました: {error_str}"
                )
        
        if not response.text:
            print("Empty response from API")
            raise HTTPException(
                status_code=500,
                detail="APIからの応答が空でした"
            )

        # レスポンステキストからJSONを抽出
        try:
            # JSONブロックを探す
            json_text = response.text
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            elif "```" in json_text:
                json_text = json_text.split("```")[1].strip()
            
            slide_data = json.loads(json_text)
            
            # 基本的な検証
            if not isinstance(slide_data, dict) or "slides" not in slide_data:
                raise ValueError("Invalid JSON structure")
            # PowerPointファイルの生成
            pptx_file = create_powerpoint(slide_data["slides"], request.theme)
                
            return {
                "message": "スライド生成用のデータが正常に作成されました。",
                "data": slide_data,
                "pptxFile": pptx_file
            }
            
        except json.JSONDecodeError as je:
            raise HTTPException(
                status_code=500,
                detail=f"JSONの解析に失敗しました: {str(je)}"
            )
        except ValueError as ve:
            raise HTTPException(
                status_code=500,
                detail=f"無効なデータ構造です: {str(ve)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"予期せぬエラーが発生しました: {str(e)}"
        )