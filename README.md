# 図面チェックAIシステム

設計事務所から提出される図面を自動的にチェックし、創建基準に基づいた指摘を行うAIシステムです。

## 機能

- **PDF図面の自動読み込み**: PDF形式の図面を読み込み、テキストを抽出
- **必須記載事項チェック**: 図面番号、図面名、縮尺、作成日などの必須項目をチェック
- **創建特有項目チェック**: 外断熱、第一種換気システム、釘ピッチなど創建基準をチェック
- **レポート生成**: チェック結果をテキストまたはJSON形式で出力

## セットアップ

### 1. プロジェクトディレクトリに移動

```bash
cd /Users/kairi.oshima/souken
```

**重要**: 必ずプロジェクトルート（`souken`ディレクトリ）に移動してから実行してください。

### 2. 依存パッケージのインストール

```bash
# macOS/Linuxの場合
pip3 install -r requirements.txt
# または
python3 -m pip install -r requirements.txt

# Windowsの場合
pip install -r requirements.txt
```

### 3. 基本的な使用方法

#### 🌐 Webアプリケーション（推奨・最も簡単）

ブラウザから簡単に使えるWebアプリケーションです。

```bash
# Streamlitアプリを起動
streamlit run app.py
```

起動後、自動的にブラウザが開きます（通常は http://localhost:8501）

**使い方**:
1. PDFファイルをアップロード
2. 「チェック実行」ボタンをクリック
3. 結果を確認・ダウンロード

詳細は [`ユーザー向け使い方.md`](ユーザー向け使い方.md) を参照してください。

#### 🔧 APIサーバー（開発者向け）

```bash
# プロジェクトルートから実行（ポート8000）
python3 run_local.py

# または直接uvicornを使用
python3 -m uvicorn api.index:app --reload --host 0.0.0.0 --port 8000
```

起動後、以下のURLでアクセスできます：
- APIルート: http://localhost:8000/
- ヘルスチェック: http://localhost:8000/api/health
- APIドキュメント: http://localhost:8000/docs (Swagger UI)
- 代替APIドキュメント: http://localhost:8000/redoc (ReDoc)

#### コマンドラインから実行

```bash
# テキスト形式で結果を表示
python3 -m src.main 図面ファイル.pdf

# JSON形式で結果を出力
python3 -m src.main 図面ファイル.pdf --format json

# 結果をファイルに保存
python3 -m src.main 図面ファイル.pdf --output result.txt
```

#### APIを使用してチェック

```bash
# ヘルスチェック
curl http://localhost:8000/api/health

# 図面をアップロードしてチェック
curl -X POST "http://localhost:8000/api/v1/check" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@図面ファイル.pdf"

# チェック項目一覧を取得
curl http://localhost:8000/api/v1/check-items
```

#### Pythonスクリプトから使用

```python
from src.pdf_parser import PDFParser
from src.checkers import CheckEngine

# PDF解析
parser = PDFParser()
drawing_data = parser.parse("図面ファイル.pdf")

# チェック実行
check_engine = CheckEngine()
results = check_engine.check_all(drawing_data)
summary = check_engine.get_summary(results)

# 結果表示
print(f"総チェック数: {summary['total']}")
print(f"NG: {summary['ng']}")
for result in results:
    if result.status.value != "OK":
        print(f"- {result.item}: {result.message}")
```

## テスト実行

```bash
python3 test_check.py
```

## チェック項目

### 必須記載事項
- 図面番号
- 図面名
- 縮尺
- 作成日
- 作成者

### 創建特有項目
- 外断熱仕様
- 第一種換気システム
- 釘ピッチ（150mm以下）
- 隠蔽部分の施工方法

## プロジェクト構成

```
souken/
├── src/
│   ├── __init__.py
│   ├── pdf_parser.py      # PDF解析モジュール
│   ├── checkers.py        # チェックエンジン
│   └── main.py            # メインスクリプト
├── requirements.txt       # 依存パッケージ
├── test_check.py          # テストスクリプト
├── 図面チェックAI_要件定義.md
├── 図面チェックAI_システム設計.md
└── README.md
```

## デプロイ

### Streamlit Cloud（推奨）

最も簡単にデプロイできます。詳細は [`STREAMLIT_デプロイ手順.md`](STREAMLIT_デプロイ手順.md) を参照してください。

1. https://share.streamlit.io/ にアクセス
2. GitHubアカウントでログイン
3. リポジトリを選択してデプロイ

### Railway

詳細は [`RAILWAY_デプロイ手順.md`](RAILWAY_デプロイ手順.md) を参照してください。

## 今後の拡張予定

- [x] Web UI実装（Streamlit）
- [ ] OCR対応（スキャン図面の処理）
- [ ] 図面要素認識（線、文字、記号の認識）
- [ ] 施工上の問題チェック
- [ ] 図面間整合性チェック
- [ ] データベース連携
- [ ] 学習機能の実装

## ライセンス

内部使用のみ


