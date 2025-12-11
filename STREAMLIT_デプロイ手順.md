# Streamlit Cloud デプロイ手順

## 概要

Streamlit Cloudを使用して、Webアプリケーションを無料でデプロイできます。

## デプロイ手順

### 1. Streamlit Cloudアカウントの作成

1. https://share.streamlit.io/ にアクセス
2. 「Sign up」をクリック
3. GitHubアカウントでログイン

### 2. アプリケーションのデプロイ

1. Streamlit Cloudダッシュボードで「New app」をクリック
2. 以下の情報を入力：
   - **Repository**: `kairiadlimix/souken`
   - **Branch**: `main`
   - **Main file path**: `app.py`
3. 「Deploy!」をクリック

### 3. デプロイの確認

- デプロイが完了すると、URLが表示されます
- 例: `https://souken-app.streamlit.app`
- このURLを共有すれば、誰でもアクセスできます

## 注意事項

### ファイルサイズ制限

- Streamlit Cloudでは、アップロードできるファイルサイズに制限があります
- 大きなPDFファイル（50MB以上）は処理できない可能性があります

### 依存パッケージ

- `requirements.txt`に必要なパッケージが含まれていることを確認
- Streamlit Cloudは自動的に`requirements.txt`を読み込みます

### 環境変数

- 必要に応じて、Streamlit Cloudの設定で環境変数を追加できます

## 代替案: Railway

Streamlit Cloudが使えない場合、Railwayでもデプロイできます。

### Railwayでのデプロイ

1. https://railway.app にアクセス
2. GitHubリポジトリを接続
3. 新しいプロジェクトを作成
4. サービスを追加し、以下の設定：
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
   - **環境変数**: 必要に応じて設定

## ローカル開発

デプロイ前に、ローカルで動作確認：

```bash
# プロジェクトディレクトリに移動
cd /Users/kairi.oshima/souken

# Streamlitアプリを起動
streamlit run app.py
```

## 更新方法

GitHubにプッシュすると、Streamlit Cloudが自動的に再デプロイします：

```bash
git add .
git commit -m "Update app"
git push origin main
```

