# Vercelデプロイ クイックスタート

## 現在の状況
- ✅ FastAPIアプリケーション（`api/index.py`）が実装済み
- ✅ Vercel設定ファイル（`vercel.json`）が準備済み
- ✅ Vercel用依存パッケージ（`requirements-vercel.txt`）が準備済み

## デプロイ手順

### ステップ1: Vercel CLIをインストール
```bash
npm install -g vercel
```

### ステップ2: Vercelにログイン
```bash
vercel login
```
ブラウザが開くので、Vercelアカウントでログインしてください。

### ステップ3: プロジェクトをデプロイ
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

### ステップ4: 本番環境にデプロイ
```bash
vercel --prod
```

## デプロイ後の確認

### 1. ヘルスチェック
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

## 注意事項

### ファイルサイズ制限
- Vercelの無料プランでは、リクエストボディの最大サイズは**4.5MB**です
- 7.5MBのPDFファイルは処理できません
- より小さなPDFファイルでテストしてください

### Gemini OCRについて
- VercelのServerless Functionsでは`pdf2image`と`poppler`が動作しない可能性が高いため、Gemini OCRはデフォルトで無効化されています
- `pdfplumber`によるテキスト抽出のみが使用されます

### タイムアウト
- 無料プランでは実行時間が最大60秒に制限されています
- 大きなPDFファイルや複雑なチェックはタイムアウトする可能性があります

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
