# Vercelデプロイ手順（最新版）

## 概要
現在実装されている図面チェックAIシステムをVercelにデプロイする手順です。

## 前提条件
- Vercelアカウント（https://vercel.com）
- GitHubリポジトリへのアクセス権限
- Vercel CLI（オプション、推奨）

## デプロイ方法

### 方法1: Vercel CLIを使用（推奨）

#### 1. Vercel CLIをインストール
```bash
npm install -g vercel
```

#### 2. Vercelにログイン
```bash
vercel login
```

#### 3. プロジェクトをリンク
```bash
cd /Users/kairi.oshima/souken
vercel link
```

以下の質問に答えます：
- **Set up and deploy "~/souken"?** → `Y`
- **Which scope?** → アカウントを選択
- **Link to existing project?** → `N`（新規プロジェクトの場合）
- **What's your project's name?** → `souken` または任意の名前
- **In which directory is your code located?** → `./`

#### 4. 環境変数を設定（オプション）
```bash
# Gemini OCRを使用する場合（Vercelでは動作しない可能性が高い）
vercel env add GOOGLE_API_KEY
vercel env add USE_GEMINI_OCR
```

**注意**: VercelのServerless Functionsでは`pdf2image`と`poppler`が動作しない可能性が高いため、Gemini OCRはデフォルトで無効化されています。

#### 5. デプロイ
```bash
# プレビュー環境にデプロイ
vercel

# 本番環境にデプロイ
vercel --prod
```

### 方法2: GitHub連携を使用

#### 1. Vercelダッシュボードで設定
1. https://vercel.com にログイン
2. **Add New...** → **Project** をクリック
3. GitHubリポジトリを選択
4. プロジェクト設定：
   - **Framework Preset**: Other
   - **Root Directory**: `./`
   - **Build Command**: （空欄）
   - **Output Directory**: （空欄）
   - **Install Command**: `pip install -r requirements-vercel.txt`
5. **Environment Variables**: 必要に応じて設定
   - `GOOGLE_API_KEY`: （オプション、Gemini OCR用）
   - `USE_GEMINI_OCR`: `false`（デフォルト、Vercelでは動作しない可能性が高い）
6. **Deploy** をクリック

#### 2. 自動デプロイ
GitHubにプッシュすると自動的にデプロイされます。

## APIエンドポイント

デプロイ後、以下のエンドポイントが利用可能になります：

### ルート
- `GET /` - API情報
- `GET /api/health` - ヘルスチェック

### 図面チェック
- `POST /api/v1/check` - 図面をアップロードしてチェック
  - **Request**: multipart/form-data
    - `file`: PDFファイル
    - `check_categories`: チェックカテゴリ（オプション）
  - **Response**: JSON形式のチェック結果

### チェック項目
- `GET /api/v1/check-items` - チェック項目一覧

## 使用例

### cURL
```bash
# ヘルスチェック
curl https://your-project.vercel.app/api/health

# 図面をアップロードしてチェック
curl -X POST https://your-project.vercel.app/api/v1/check \
  -F "file=@図面ファイル.pdf"
```

### Python
```python
import requests

url = "https://your-project.vercel.app/api/v1/check"
files = {"file": open("図面ファイル.pdf", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

### JavaScript (fetch)
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('https://your-project.vercel.app/api/v1/check', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

## 制限事項

### Vercel Serverless Functionsの制限
- **実行時間**: 最大60秒（Hobbyプラン）、300秒（Proプラン）
- **メモリ**: 最大1024MB
- **ファイルサイズ**: 最大4.5MB（リクエストボディ）
- **タイムアウト**: 10秒（Hobbyプラン）、60秒（Proプラン）

### 注意点
1. **大きなPDFファイル**: 4.5MBを超えるファイルは処理できません
2. **処理時間**: 複雑なチェックはタイムアウトする可能性があります
3. **Gemini OCR**: VercelのServerless Functionsでは`pdf2image`と`poppler`が動作しない可能性が高いため、Gemini OCRはデフォルトで無効化されています
4. **依存パッケージ**: 一部のパッケージ（特にOCR関連）はVercelで動作しない可能性があります

## トラブルシューティング

### デプロイエラー
```bash
# ログを確認
vercel logs

# ローカルでテスト
vercel dev
```

### パッケージのインストールエラー
`requirements-vercel.txt`を確認し、Vercelでサポートされていないパッケージがないか確認してください。

### タイムアウトエラー
- 処理時間を短縮する
- より大きなプランにアップグレード
- 非同期処理を検討

### Gemini OCRエラー
Vercelでは`pdf2image`と`poppler`が動作しない可能性が高いため、Gemini OCRは無効化されています。必要に応じて、別のプラットフォーム（Railway、Renderなど）でデプロイすることを検討してください。

## 現在の実装状況

### ✅ 実装済み機能
- PDF解析（pdfplumber、PyPDF2）
- 必須記載事項チェック
- 基本情報チェック
- 仕上げ表チェック
- FastAPIエンドポイント

### ⚠️ 制限事項
- Gemini OCR: Vercelでは動作しない可能性が高い（デフォルトで無効化）
- Streamlit UI: Vercelでは使用しない（別途Streamlit Cloudでデプロイ可能）

## 次のステップ

1. **デプロイ確認**
   - ヘルスチェックエンドポイントで動作確認
   - 小さなPDFファイルでチェック機能をテスト

2. **Streamlit UIのデプロイ**
   - Streamlit Cloudで`app.py`をデプロイ
   - または、別のプラットフォーム（Railway、Renderなど）でデプロイ

3. **Gemini OCRの利用**
   - Railway、Renderなどのプラットフォームでデプロイ
   - または、ローカル環境で使用

## 参考リンク

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [Mangum Documentation](https://mangum.io/)
- [Streamlit Cloud](https://streamlit.io/cloud)
