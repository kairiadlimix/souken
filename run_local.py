"""
ローカル実行用スクリプト
FastAPIアプリケーションをローカルで起動します
"""

import uvicorn
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    # ローカル実行用の設定
    uvicorn.run(
        "api.index:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 開発時に自動リロード
        log_level="info"
    )

