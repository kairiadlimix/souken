# Vercel設定手順

## 概要
図面チェックAIシステムをVercelにデプロイするための設定手順です。

## 前提条件
- Vercelアカウント（https://vercel.com）
- GitHubリポジトリへのアクセス権限

## 設定ファイル

### 1. vercel.json
Vercelの設定ファイル。既に作成済みです。

### 2. api/index.py
Vercel Serverless Functions用のエントリーポイント。FastAPIアプリケーションをVercelで動作させるための設定。

## デプロイ手順

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

#### 4. デプロイ
```bash
vercel
```

本番環境にデプロイする場合：
```bash
vercel --prod
```

### 方法2: GitHub連携を使用

#### 1. Vercelダッシュボードで設定
1. https://vercel.com にログイン
2. **Add New...** → **Project** をクリック
3. GitHubリポジトリ `kairiadlimix/souken` を選択
4. プロジェクト設定：
   - **Framework Preset**: Other
   - **Root Directory**: `./`
   - **Build Command**: （空欄）
   - **Output Directory**: （空欄）
5. **Environment Variables**: 必要に応じて設定
6. **Deploy** をクリック

#### 2. 自動デプロイ
GitHubにプッシュすると自動的にデプロイされます。

## 環境変数（必要に応じて）

Vercelダッシュボードで環境変数を設定できます：

```
# 例（必要に応じて）
PYTHON_VERSION=3.9
```

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
3. **依存パッケージ**: 一部のパッケージ（特にOCR関連）はVercelで動作しない可能性があります

## トラブルシューティング

### デプロイエラー
```bash
# ログを確認
vercel logs

# ローカルでテスト
vercel dev
```

### パッケージのインストールエラー
`requirements.txt`を確認し、Vercelでサポートされていないパッケージがないか確認してください。

### タイムアウトエラー
- 処理時間を短縮する
- より大きなプランにアップグレード
- 非同期処理を検討

## 次のステップ

1. **フロントエンドの追加**
   - React/Vue.jsでWeb UIを作成
   - Vercelにデプロイ

2. **データベースの追加**
   - Vercel Postgres または外部データベース
   - チェック結果の保存

3. **認証の追加**
   - Vercel Authentication
   - アクセス制御

## 参考リンク

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [Mangum Documentation](https://mangum.io/)

