# Vercel トラブルシューティングガイド

## エラー: FUNCTION_INVOCATION_FAILED

このエラーは、Serverless Functionがクラッシュしたことを示しています。

## 確認手順

### 1. Vercelのログを確認

#### Vercel CLIを使用
```bash
# ログを確認
vercel logs

# リアルタイムでログを確認
vercel logs --follow
```

#### Vercelダッシュボードで確認
1. https://vercel.com にログイン
2. プロジェクトを選択
3. **Deployments** タブを開く
4. 失敗したデプロイメントをクリック
5. **Functions** タブでログを確認

### 2. ローカルでテスト

```bash
# Vercel CLIでローカルサーバーを起動
vercel dev
```

ブラウザで `http://localhost:3000/api/health` にアクセスして動作確認。

## よくある原因と解決方法

### 原因1: インポートエラー

**症状**: `ModuleNotFoundError` が発生

**解決方法**:
1. `requirements.txt`に必要なパッケージが含まれているか確認
2. `src/`ディレクトリが正しく配置されているか確認
3. パスの問題を確認（`api/index.py`の`sys.path`設定）

**確認コマンド**:
```bash
# ローカルでインポートテスト
cd /Users/kairi.oshima/souken
python3 -c "import sys; sys.path.insert(0, '.'); from src.pdf_parser import PDFParser; print('OK')"
```

### 原因2: 依存パッケージの問題

**症状**: パッケージのインストールエラー

**解決方法**:
1. `requirements.txt`を確認
2. Vercelでサポートされていないパッケージがないか確認
3. 特に注意が必要なパッケージ:
   - `psycopg2-binary`: PostgreSQLが必要（Vercel Postgresを使用する場合のみ）
   - `opencv-python`: 大きなパッケージ（Vercelでは動作しない可能性）

**修正例**:
```txt
# Vercel用に requirements.txt を簡略化
PyPDF2>=3.0.0
pdfplumber>=0.9.0
fastapi>=0.104.0
python-multipart>=0.0.6
mangum>=0.17.0
pydantic>=2.0.0
```

### 原因3: ハンドラー関数の名前

**症状**: 関数が見つからない

**解決方法**:
- `api/index.py`で`handler`という名前の変数をエクスポートしているか確認
- Mangumの設定を確認

**正しい形式**:
```python
handler = Mangum(app, lifespan="off")
```

### 原因4: ファイルサイズの制限

**症状**: 大きなPDFファイルをアップロードするとエラー

**解決方法**:
- Vercelの制限: 最大4.5MB（リクエストボディ）
- ファイルサイズチェックを追加

### 原因5: タイムアウト

**症状**: 処理が完了する前にタイムアウト

**解決方法**:
- Hobbyプラン: 10秒のタイムアウト
- Proプラン: 60秒のタイムアウト
- 処理を最適化するか、プランをアップグレード

## デバッグ用エンドポイント

### ヘルスチェック
```bash
curl https://your-project.vercel.app/api/health
```

### ルートエンドポイント
```bash
curl https://your-project.vercel.app/
```

## 修正した内容

### 1. エラーハンドリングの改善
- インポートエラーの詳細記録
- トレースバックの出力

### 2. 遅延初期化
- グローバル変数の初期化を遅延
- メモリ使用量の削減

### 3. Mangumの設定
- `lifespan="off"`を設定
- VercelのServerless Functions環境に最適化

## 次のステップ

1. **ログを確認**
   ```bash
   vercel logs
   ```

2. **ローカルでテスト**
   ```bash
   vercel dev
   ```

3. **修正をコミット・プッシュ**
   ```bash
   git add .
   git commit -m "Fix Vercel deployment issues"
   git push
   ```

4. **再デプロイ**
   - GitHub連携の場合は自動的に再デプロイ
   - 手動の場合は `vercel --prod`

## 簡易テスト用エンドポイント

まず、以下のエンドポイントで動作確認：

```bash
# ヘルスチェック
curl https://your-project.vercel.app/api/health

# ルート
curl https://your-project.vercel.app/

# チェック項目一覧
curl https://your-project.vercel.app/api/v1/check-items
```

これらが動作すれば、基本的な設定は正しいです。

