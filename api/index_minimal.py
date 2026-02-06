"""
Vercel Serverless Function - 最小限版
FastAPIなしで動作する軽量版
"""

import sys
import os
import json
import tempfile
from pathlib import Path
from typing import Dict, Any

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.pdf_parser import PDFParser
from src.checkers import CheckEngine, CheckStatus, Importance


def handler(request):
    """
    Vercel Serverless Function ハンドラー
    
    Args:
        request: Vercelのリクエストオブジェクト
    
    Returns:
        dict: レスポンス
    """
    method = request.get('method', 'GET')
    path = request.get('path', '/')
    headers = request.get('headers', {})
    body = request.get('body', '')
    
    # CORSヘッダー
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    # OPTIONSリクエスト（CORS preflight）
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': ''
        }
    
    # ルートエンドポイント
    if path == '/' or path == '/api':
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'message': '図面チェックAIシステム API',
                'version': '1.0.0',
                'endpoints': {
                    'health': '/api/health',
                    'check': '/api/v1/check',
                    'check_items': '/api/v1/check-items'
                }
            }, ensure_ascii=False)
        }
    
    # ヘルスチェック
    if path == '/api/health':
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'status': 'ok',
                'service': '図面チェックAIシステム'
            }, ensure_ascii=False)
        }
    
    # チェック項目一覧
    if path == '/api/v1/check-items':
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'categories': [
                    {
                        'name': '必須記載事項',
                        'items': ['図面番号', '図面名', '縮尺', '作成日', '作成者']
                    },
                    {
                        'name': '創建特有項目',
                        'items': ['外断熱仕様', '第一種換気システム', '釘ピッチ', '隠蔽部分の施工方法']
                    }
                ]
            }, ensure_ascii=False)
        }
    
    # 図面チェック（POST /api/v1/check）
    if path == '/api/v1/check' and method == 'POST':
        try:
            # リクエストボディをパース
            if isinstance(body, str):
                body_data = json.loads(body) if body else {}
            else:
                body_data = body
            
            # ファイルアップロードの処理（Vercelではbase64エンコードされたファイルが送られてくる可能性）
            # 注意: VercelのServerless Functionsでは、multipart/form-dataの処理が複雑
            # ここでは簡易的な実装
            
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({
                    'error': 'ファイルアップロードは現在サポートされていません。FastAPI版を使用してください。'
                }, ensure_ascii=False)
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': cors_headers,
                'body': json.dumps({
                    'error': f'エラーが発生しました: {str(e)}'
                }, ensure_ascii=False)
            }
    
    # 404
    return {
        'statusCode': 404,
        'headers': cors_headers,
        'body': json.dumps({
            'error': 'Not Found'
        }, ensure_ascii=False)
    }
