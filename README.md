# 図面チェックAIシステム

設計事務所から提出される図面を自動的にチェックし、創建基準に基づいた指摘を行うAIシステムです。

## 機能

- **PDF図面の自動読み込み**: PDF形式の図面を読み込み、テキストを抽出
- **必須記載事項チェック**: 図面番号、図面名、縮尺、作成日などの必須項目をチェック
- **創建特有項目チェック**: 外断熱、第一種換気システム、釘ピッチなど創建基準をチェック
- **レポート生成**: チェック結果をテキストまたはJSON形式で出力

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 基本的な使用方法

#### コマンドラインから実行

```bash
# テキスト形式で結果を表示
python -m src.main 図面ファイル.pdf

# JSON形式で結果を出力
python -m src.main 図面ファイル.pdf --format json

# 結果をファイルに保存
python -m src.main 図面ファイル.pdf --output result.txt
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
python test_check.py
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

## 今後の拡張予定

- [ ] OCR対応（スキャン図面の処理）
- [ ] 図面要素認識（線、文字、記号の認識）
- [ ] 施工上の問題チェック
- [ ] 図面間整合性チェック
- [ ] Web UI実装
- [ ] データベース連携
- [ ] 学習機能の実装

## ライセンス

内部使用のみ

