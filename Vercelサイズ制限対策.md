# Vercelサイズ制限対策

## 問題
VercelのServerless Functionsのサイズ制限（250MB）を超えています。

## 原因
`pdfplumber`とその依存パッケージ（特に`Pillow`、`pdfminer.six`など）が非常に大きいためです。

## 解決策

### オプション1: PyPDF2のみを使用（推奨）
`pdfplumber`を削除し、`PyPDF2`のみを使用します。`PyPDF2`は軽量ですが、テキスト抽出の精度は`pdfplumber`より低い場合があります。

### オプション2: 別のプラットフォームを使用
Vercelの制限が厳しいため、以下のプラットフォームを検討：
- **Railway**: より柔軟なサイズ制限
- **Render**: より柔軟なサイズ制限
- **Fly.io**: より柔軟なサイズ制限

### オプション3: 外部APIを使用
PDF処理を外部API（例: Adobe PDF Services API）に委譲する。

## 推奨アプローチ
`PyPDF2`のみを使用する軽量版を作成します。
