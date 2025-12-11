# Railway デプロイ手順

## 概要

RailwayはFastAPIを直接サポートしており、Vercelよりも簡単にデプロイできます。

## デプロイ手順

### 1. Railwayアカウントの作成

1. https://railway.app にアクセス
2. 「Start a New Project」をクリック
3. GitHubアカウントでログイン

### 2. プロジェクトの作成

1. 「New Project」をクリック
2. 「Deploy from GitHub repo」を選択
3. `kairiadlimix/souken`リポジトリを選択
4. 「Deploy Now」をクリック

### 3. 設定

Railwayは自動的にPythonプロジェクトを検出しますが、必要に応じて以下を設定：

#### 環境変数（必要に応じて）
- Railwayダッシュボードで「Variables」タブを開く
- 必要な環境変数を追加

#### ポート設定
- Railwayは自動的に`$PORT`環境変数を設定
- FastAPIアプリは`$PORT`を使用するように設定する必要があります

### 4. コードの修正（必要に応じて）

`api/index.py`を修正して、Railwayのポートを使用するようにします：

```python
# Railway用の設定（既存のコードで問題ない場合が多い）
# Railwayは自動的にポートを設定するため、通常は修正不要
```

### 5. デプロイの確認

1. Railwayダッシュボードで「Deployments」タブを確認
2. デプロイが成功したら、「Settings」タブでドメインを確認
3. ブラウザで `https://your-app.railway.app/api/health` にアクセス

## トラブルシューティング

### デプロイが失敗する場合

1. **ログを確認**
   - Railwayダッシュボードで「Deployments」→ 失敗したデプロイ → 「View Logs」

2. **依存パッケージの確認**
   - `requirements.txt`に必要なパッケージが含まれているか確認

3. **ポート設定の確認**
   - Railwayは自動的に`$PORT`を設定
   - アプリが`$PORT`を使用しているか確認

### よくあるエラー

1. **ModuleNotFoundError**
   - `requirements.txt`に必要なパッケージを追加

2. **ポートエラー**
   - Railwayは自動的にポートを設定するため、通常は問題なし

3. **インポートエラー**
   - `api/index.py`の`sys.path`設定を確認

## メリット

- ✅ FastAPIを直接サポート
- ✅ 簡単なデプロイ（GitHub連携）
- ✅ 無料プランあり（$5/月のクレジット）
- ✅ 環境変数の簡単な管理
- ✅ ログの確認が容易
- ✅ 自動デプロイ（GitHub pushで自動デプロイ）

## 次のステップ

1. Railwayでデプロイ
2. 動作確認
3. 必要に応じて環境変数を設定
4. 本番環境として使用

