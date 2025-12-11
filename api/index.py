"""
Vercel Serverless Function for 図面チェックAIシステム
FastAPIアプリケーションをVercelで動作させるためのエントリーポイント
"""

import sys
import os
from pathlib import Path
import traceback

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from fastapi import FastAPI, UploadFile, File, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import json
    from typing import Optional

    from src.pdf_parser import PDFParser
    from src.checkers import CheckEngine, CheckStatus, Importance
    
    # MangumはVercelデプロイ時のみ必要（ローカル実行時は不要）
    try:
        from mangum import Mangum
        MANGUM_AVAILABLE = True
    except ImportError:
        MANGUM_AVAILABLE = False
except ImportError as e:
    # インポートエラーを詳細に記録
    error_msg = f"Import error: {str(e)}\n{traceback.format_exc()}"
    print(error_msg, file=sys.stderr)
    raise

# FastAPIアプリケーションの作成
app = FastAPI(
    title="図面チェックAIシステム API",
    description="設計事務所から提出される図面を自動的にチェックするAIシステム",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切なオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# グローバル変数（初期化を遅延させる）
pdf_parser = None
check_engine = None

def get_parser():
    """PDFパーサーを取得（遅延初期化）"""
    global pdf_parser
    if pdf_parser is None:
        pdf_parser = PDFParser()
    return pdf_parser

def get_check_engine():
    """チェックエンジンを取得（遅延初期化）"""
    global check_engine
    if check_engine is None:
        check_engine = CheckEngine()
    return check_engine


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "図面チェックAIシステム API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "check": "/api/v1/check",
            "check_items": "/api/v1/check-items"
        }
    }


@app.get("/api/health")
async def health_check():
    """ヘルスチェック"""
    try:
        # モジュールのインポート確認
        parser_status = "ok" if pdf_parser is not None else "not initialized"
        engine_status = "ok" if check_engine is not None else "not initialized"
        
        return {
            "status": "ok",
            "service": "図面チェックAIシステム",
            "modules": {
                "pdf_parser": parser_status,
                "check_engine": engine_status
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@app.post("/api/v1/check")
async def check_drawing(
    file: UploadFile = File(...),
    check_categories: Optional[str] = None
):
    """
    図面をアップロードしてチェックを実行
    
    Args:
        file: アップロードされたPDFファイル
        check_categories: チェックカテゴリ（カンマ区切り、例: "required,souken_specific"）
    
    Returns:
        チェック結果
    """
    try:
        # ファイル形式の確認
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="PDFファイルのみ対応しています"
            )
        
        # ファイルを一時的に保存
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # PDF解析
            parser = get_parser()
            drawing_data = parser.parse(tmp_path)
            
            # チェック実行
            engine = get_check_engine()
            results = engine.check_all(drawing_data)
            summary = engine.get_summary(results)
            
            # 結果をフォーマット
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'category': result.category,
                    'item': result.item,
                    'status': result.status.value,
                    'message': result.message,
                    'importance': result.importance.value,
                    'page_number': result.page_number,
                    'suggestion': result.suggestion
                })
            
            return JSONResponse({
                'file_name': file.filename,
                'status': 'completed',
                'summary': summary,
                'results': formatted_results
            })
        
        finally:
            # 一時ファイルを削除
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except HTTPException:
        raise
    except Exception as e:
        # エラーの詳細をログに記録
        error_trace = traceback.format_exc()
        print(f"Error in check_drawing: {str(e)}\n{error_trace}", file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail=f"エラーが発生しました: {str(e)}"
        )


@app.get("/api/v1/check-items")
async def get_check_items():
    """チェック項目一覧を取得"""
    return {
        "categories": [
            {
                "name": "必須記載事項",
                "items": [
                    "図面番号",
                    "図面名",
                    "縮尺",
                    "作成日",
                    "作成者"
                ]
            },
            {
                "name": "創建特有項目",
                "items": [
                    "外断熱仕様",
                    "第一種換気システム",
                    "釘ピッチ",
                    "隠蔽部分の施工方法"
                ]
            }
        ]
    }


# Vercel用のハンドラー（Vercelデプロイ時のみ使用）
# Mangumを使用してASGIアプリケーションをAWS Lambda形式に変換
# VercelのPython Serverless Functionsは、この形式を期待しています
# ローカル実行時は不要（uvicornが直接appを使用）
if MANGUM_AVAILABLE:
    handler = Mangum(app, lifespan="off")
else:
    # ローカル実行時はhandlerを定義しない（uvicornがappを直接使用）
    handler = None

