# 図面チェックAI システム設計書

## 1. システム概要

### 1.1 システム名
**創建図面チェックAIシステム（Souken Drawing Check AI）**

### 1.2 システムの位置づけ
設計事務所から提出される図面を自動チェックし、創建基準に基づいた指摘を行う支援システム。

## 2. システムアーキテクチャ

### 2.1 全体構成

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Web UI)                     │
│  - 図面アップロード                                       │
│  - チェック結果表示                                       │
│  - レポートダウンロード                                    │
└──────────────────┬──────────────────────────────────────┘
                    │
┌──────────────────▼──────────────────────────────────────┐
│              Backend API (FastAPI)                        │
│  - 図面アップロード受付                                    │
│  - チェック処理のオーケストレーション                       │
│  - 結果の保存・取得                                        │
└──────────────────┬──────────────────────────────────────┘
                    │
┌──────────────────▼──────────────────────────────────────┐
│            Core Processing Engine                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  PDF Parser Module                                │   │
│  │  - PDF読み込み・解析                                │   │
│  │  - テキスト抽出                                     │   │
│  │  - OCR処理（必要に応じて）                          │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Drawing Element Recognition                      │   │
│  │  - 図面要素の認識（線、文字、記号）                  │   │
│  │  - レイヤー解析                                     │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Check Engine                                     │   │
│  │  ├─ Required Items Checker                        │   │
│  │  ├─ Souken Specific Checker                      │   │
│  │  ├─ Construction Issue Checker                   │   │
│  │  └─ Consistency Checker                          │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Report Generator                                 │   │
│  │  - レポート生成                                     │   │
│  │  - PDF/Excel出力                                    │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────┘
                    │
┌──────────────────▼──────────────────────────────────────┐
│              Database (PostgreSQL)                        │
│  - チェック結果の保存                                      │
│  - チェック項目定義                                        │
│  - 過去データの蓄積                                        │
└──────────────────────────────────────────────────────────┘
```

### 2.2 データフロー

```
1. 図面PDFアップロード
   ↓
2. PDF解析・テキスト抽出
   ↓
3. 図面要素認識
   ↓
4. 各チェックモジュール実行
   ├─ 必須記載事項チェック
   ├─ 創建特有項目チェック
   ├─ 施工問題チェック
   └─ 整合性チェック
   ↓
5. チェック結果の集約
   ↓
6. レポート生成
   ↓
7. 結果保存・返却
```

## 3. モジュール設計

### 3.1 PDF Parser Module

#### 機能
- PDFファイルの読み込み
- テキスト抽出（ベクターPDF）
- OCR処理（ラスターPDF）
- メタデータ抽出

#### 技術スタック
- `PyPDF2` / `pdfplumber`: PDF解析
- `pdf2image`: PDF→画像変換
- `pytesseract` / `EasyOCR`: OCR処理

#### インターフェース
```python
class PDFParser:
    def parse(self, pdf_path: str) -> DrawingData:
        """
        PDFを解析してDrawingDataを返す
        """
        pass
    
    def extract_text(self, pdf_path: str) -> Dict[str, str]:
        """
        各ページからテキストを抽出
        """
        pass
    
    def extract_images(self, pdf_path: str) -> List[Image]:
        """
        PDFから画像を抽出（OCR用）
        """
        pass
```

### 3.2 Drawing Element Recognition Module

#### 機能
- 図面要素の認識（線、文字、記号）
- レイヤー解析
- 図面タイプの判定（平面図、立面図、詳細図など）

#### 技術スタック
- `OpenCV`: 画像処理
- `YOLO` / `Detectron2`: オブジェクト検出（将来的に）

#### インターフェース
```python
class DrawingElementRecognizer:
    def recognize_elements(self, drawing_data: DrawingData) -> List[Element]:
        """
        図面要素を認識
        """
        pass
    
    def classify_drawing_type(self, drawing_data: DrawingData) -> str:
        """
        図面タイプを判定
        """
        pass
```

### 3.3 Check Engine

#### 3.3.1 Required Items Checker

##### チェック項目
- 図面番号
- 図面名
- 縮尺
- 作成日・改訂日
- 作成者・承認者
- 特記事項欄

##### 実装例
```python
class RequiredItemsChecker:
    def check(self, drawing_data: DrawingData) -> List[CheckResult]:
        results = []
        
        # 図面番号チェック
        if not self._has_drawing_number(drawing_data):
            results.append(CheckResult(
                category="必須記載事項",
                item="図面番号",
                status="NG",
                message="図面番号が記載されていません"
            ))
        
        # 縮尺チェック
        if not self._has_scale(drawing_data):
            results.append(CheckResult(
                category="必須記載事項",
                item="縮尺",
                status="NG",
                message="縮尺が記載されていません"
            ))
        
        return results
```

#### 3.3.2 Souken Specific Checker

##### チェック項目
- 外断熱仕様の記載
- 第一種換気システムの記載
- 釘ピッチの記載（150mm基準）
- 創建品質基準の遵守
- 隠蔽部分の施工方法記載
- 写真記録の指示

##### 実装例
```python
class SoukenSpecificChecker:
    def check(self, drawing_data: DrawingData) -> List[CheckResult]:
        results = []
        
        # 外断熱チェック
        if not self._has_external_insulation_spec(drawing_data):
            results.append(CheckResult(
                category="創建特有項目",
                item="外断熱仕様",
                status="NG",
                message="外断熱仕様が記載されていません",
                importance="必須"
            ))
        
        # 第一種換気システムチェック
        if not self._has_first_class_ventilation(drawing_data):
            results.append(CheckResult(
                category="創建特有項目",
                item="第一種換気システム",
                status="NG",
                message="第一種換気システムの記載がありません",
                importance="必須"
            ))
        
        # 釘ピッチチェック
        nail_pitch = self._extract_nail_pitch(drawing_data)
        if nail_pitch and nail_pitch > 150:
            results.append(CheckResult(
                category="創建特有項目",
                item="釘ピッチ",
                status="NG",
                message=f"釘ピッチが{nail_pitch}mmです。創建基準は150mm以下です。",
                importance="必須"
            ))
        
        return results
```

#### 3.3.3 Construction Issue Checker

##### チェック項目
- 寸法の整合性
- 構造上の問題
- 設備の配置合理性
- 法規制遵守の確認

##### 実装例
```python
class ConstructionIssueChecker:
    def check(self, drawing_data: DrawingData) -> List[CheckResult]:
        results = []
        
        # 寸法整合性チェック
        dimension_issues = self._check_dimension_consistency(drawing_data)
        results.extend(dimension_issues)
        
        # 構造問題チェック
        structural_issues = self._check_structural_issues(drawing_data)
        results.extend(structural_issues)
        
        return results
```

#### 3.3.4 Consistency Checker

##### チェック項目
- 平面図と立面図の整合
- 詳細図と全体図の整合
- 寸法の一貫性
- 仕様の統一性

##### 実装例
```python
class ConsistencyChecker:
    def check(self, drawing_set: List[DrawingData]) -> List[CheckResult]:
        results = []
        
        # 図面間の整合性チェック
        if len(drawing_set) > 1:
            consistency_issues = self._check_cross_drawing_consistency(drawing_set)
            results.extend(consistency_issues)
        
        return results
```

### 3.4 Report Generator

#### 機能
- チェック結果の集約
- レポート生成（PDF/Excel）
- 図面へのマーキング

#### インターフェース
```python
class ReportGenerator:
    def generate_pdf_report(self, check_results: List[CheckResult]) -> bytes:
        """
        PDFレポートを生成
        """
        pass
    
    def generate_excel_report(self, check_results: List[CheckResult]) -> bytes:
        """
        Excelレポートを生成
        """
        pass
    
    def mark_drawing(self, drawing_path: str, issues: List[Issue]) -> bytes:
        """
        図面に指摘箇所をマーキング
        """
        pass
```

## 4. データモデル

### 4.1 DrawingData
```python
@dataclass
class DrawingData:
    file_path: str
    pages: List[PageData]
    metadata: Dict[str, Any]
    extracted_text: Dict[int, str]  # page_num -> text
    elements: List[Element]
    drawing_type: str  # "平面図", "立面図", "詳細図"など
```

### 4.2 CheckResult
```python
@dataclass
class CheckResult:
    category: str  # "必須記載事項", "創建特有項目"など
    item: str  # チェック項目名
    status: str  # "OK", "NG", "WARNING"
    message: str  # 指摘内容
    importance: str  # "必須", "推奨", "参考"
    location: Optional[Tuple[float, float]]  # 図面上の位置
    page_number: Optional[int]  # 該当ページ
    suggestion: Optional[str]  # 修正提案
```

### 4.3 データベーススキーマ

#### check_results テーブル
```sql
CREATE TABLE check_results (
    id SERIAL PRIMARY KEY,
    drawing_file_name VARCHAR(255),
    uploaded_at TIMESTAMP,
    check_date TIMESTAMP,
    total_issues INTEGER,
    status VARCHAR(50),  -- "PASS", "FAIL", "WARNING"
    report_path VARCHAR(500)
);
```

#### check_items テーブル
```sql
CREATE TABLE check_items (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100),
    item_name VARCHAR(255),
    importance VARCHAR(50),
    check_rule TEXT,  -- JSON形式でルールを保存
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### check_result_details テーブル
```sql
CREATE TABLE check_result_details (
    id SERIAL PRIMARY KEY,
    check_result_id INTEGER REFERENCES check_results(id),
    check_item_id INTEGER REFERENCES check_items(id),
    status VARCHAR(50),
    message TEXT,
    location_x FLOAT,
    location_y FLOAT,
    page_number INTEGER
);
```

## 5. API設計

### 5.1 エンドポイント

#### POST /api/v1/check
図面をアップロードしてチェックを実行

**Request:**
```json
{
  "file": <multipart/form-data>,
  "options": {
    "check_categories": ["required", "souken_specific", "construction", "consistency"],
    "strict_mode": true
  }
}
```

**Response:**
```json
{
  "check_id": "uuid",
  "status": "completed",
  "summary": {
    "total_checks": 50,
    "passed": 45,
    "failed": 5,
    "warnings": 0
  },
  "results": [
    {
      "category": "創建特有項目",
      "item": "外断熱仕様",
      "status": "NG",
      "message": "外断熱仕様が記載されていません",
      "importance": "必須"
    }
  ],
  "report_url": "/api/v1/reports/{check_id}"
}
```

#### GET /api/v1/reports/{check_id}
チェック結果レポートを取得

#### GET /api/v1/check-items
チェック項目一覧を取得

#### POST /api/v1/check-items
チェック項目を追加

## 6. 実装計画

### Phase 1: MVP（最小実用製品）
1. PDF読み込み・テキスト抽出
2. 基本的な必須項目チェック
3. 簡単なレポート出力
4. Web UI（基本的なアップロード・結果表示）

**期間**: 2-3週間

### Phase 2: 機能拡張
1. OCR対応
2. 創建特有項目チェックの実装
3. 図面要素認識の実装
4. 詳細レポート生成

**期間**: 4-6週間

### Phase 3: 高度な機能
1. 施工上の問題チェック
2. 図面間整合性チェック
3. 学習機能の実装
4. パフォーマンス最適化

**期間**: 6-8週間

## 7. 技術スタック

### Backend
- Python 3.9+
- FastAPI
- PostgreSQL
- Celery (非同期処理用)

### Frontend
- React / Vue.js
- または Streamlit（プロトタイプ用）

### AI/ML
- PyTorch / TensorFlow（将来的に）
- OpenCV
- Tesseract OCR / EasyOCR

### インフラ
- Docker
- AWS / GCP（将来的に）

## 8. セキュリティ考慮事項

- 図面データの暗号化保存
- アクセス制御（認証・認可）
- データの保持期間管理
- 個人情報の取り扱い

