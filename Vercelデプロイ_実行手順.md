# Vercelデプロイ 実行手順

## 準備完了 ✅

以下のファイルが準備済みです：
- ✅ `api/index.py` - FastAPIアプリケーション
- ✅ `vercel.json` - Vercel設定ファイル
- ✅ `requirements-vercel.txt` - Vercel用依存パッケージ

## デプロイ手順

### 1. Vercel CLIをインストール（初回のみ）
```bash
npm install -g vercel
```

### 2. Vercelにログイン（初回のみ）
```bash
vercel login
```
ブラウザが開くので、Vercelアカウントでログインしてください。

### 3. プロジェクトをデプロイ
```bash
cd /Users/kairi.oshima/souken
vercel
```

初回デプロイ時は以下の質問に答えます：
- **Set up and deploy "~/souken"?** → `Y`
- **Which scope?** → アカウントを選択
- **Link to existing project?** → `N`（新規プロジェクトの場合）
- **What's your project's name?** → `souken` または任意の名前
- **In which directory is your code located?** → `./`

### 4. 本番環境にデプロイ
```bash
vercel --prod
```

## デプロイ後の確認

### 1. ヘルスチェック
デプロイが完了すると、URLが表示されます。以下のコマンドで確認：
```bash
curl https://your-project.vercel.app/api/health
```

### 2. API情報の確認
```bash
curl https://your-project.vercel.app/
```

### 3. 図面チェックのテスト
```bash
curl -X POST https://your-project.vercel.app/api/v1/check \
  -F "file=@【仮実施図】藤原台Ⅲ25号地0911(書き込み有).pdf"
```

**注意**: 7.5MBのPDFファイルはVercelの制限（4.5MB）を超えるため、より小さなPDFファイルでテストしてください。

## 現在の実装状況

### ✅ 実装済み機能
- PDF解析（pdfplumber、PyPDF2）
- 必須記載事項チェック
- 基本情報チェック（物件タイトル、お客様氏名、設計者情報、図面種別、商品名）
- 仕上げ表チェック（敷地面積、BM・GL設定、長期優良・フラット35）
- FastAPIエンドポイント

### ⚠️ 制限事項
- **Gemini OCR**: Vercelでは`pdf2image`と`poppler`が動作しない可能性が高いため、デフォルトで無効化されています
- **ファイルサイズ**: 最大4.5MB（リクエストボディ）
- **実行時間**: 最大60秒（Hobbyプラン）

## トラブルシューティング

### デプロイエラーが発生した場合
```bash
# ログを確認
vercel logs

# ローカルでテスト
vercel dev
```

### パッケージのインストールエラー
`requirements-vercel.txt`を確認し、Vercelでサポートされていないパッケージがないか確認してください。

## 次のステップ

1. **Streamlit UIのデプロイ**
   - Streamlit Cloudで`app.py`をデプロイ
   - または、別のプラットフォーム（Railway、Renderなど）でデプロイ

2. **Gemini OCRの利用**
   - Railway、Renderなどのプラットフォームでデプロイ
   - または、ローカル環境で使用
