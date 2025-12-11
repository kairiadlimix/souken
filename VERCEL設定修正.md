# Vercel設定の修正内容

## 問題
Vercelのデプロイで「Conflicting functions and builds configuration」エラーが発生していました。

## 原因
`vercel.json`で`builds`と`functions`の両方を定義していたため、設定が競合していました。

Vercelの最新の推奨方法では：
- **`builds`**: 古い方法（非推奨）
- **`functions`**: 新しい方法（推奨）

両方を同時に使うことはできません。

## 修正内容

### 修正前
```json
{
  "version": 2,
  "builds": [...],  // ← 古い方法
  "routes": [...],
  "functions": {...}  // ← 新しい方法（競合）
}
```

### 修正後
```json
{
  "functions": {
    "api/index.py": {
      "runtime": "@vercel/python",
      "maxDuration": 30
    }
  },
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/index.py"
    },
    {
      "source": "/(.*)",
      "destination": "/api/index.py"
    }
  ]
}
```

## 変更点

1. **`builds`を削除**: 古い設定方法を削除
2. **`routes`を`rewrites`に変更**: 最新の設定方法に統一
3. **`functions`に`runtime`を追加**: Pythonランタイムを明示的に指定

## 次のステップ

1. 変更をコミット・プッシュ
2. Vercelが自動的に再デプロイ
3. デプロイが成功するか確認

## 確認方法

```bash
# ローカルでテスト
vercel dev

# ログを確認
vercel logs
```

