# SSH鍵設定手順

## 既存のSSH鍵を確認

既存のSSH鍵が見つかりました：
- ファイル: `~/.ssh/id_ed25519.pub`

## GitHubにSSH鍵を登録する手順

### 1. 公開鍵をコピー

以下のコマンドで公開鍵を表示してコピーします：

```bash
cat ~/.ssh/id_ed25519.pub
```

または、クリップボードに直接コピー：

```bash
cat ~/.ssh/id_ed25519.pub | pbcopy
```

### 2. GitHubに公開鍵を登録

1. GitHubにログイン
2. 右上のプロフィール画像をクリック → **Settings**
3. 左メニューから **SSH and GPG keys** を選択
4. **New SSH key** ボタンをクリック
5. 以下を入力：
   - **Title**: 任意の名前（例: "MacBook Pro"）
   - **Key**: コピーした公開鍵を貼り付け
6. **Add SSH key** をクリック

### 3. リモートURLをSSHに変更

```bash
cd /Users/kairi.oshima/souken
git remote set-url origin git@github.com:kairiadlimix/souken.git
```

### 4. 接続テスト

```bash
ssh -T git@github.com
```

初回は以下のようなメッセージが表示されます：
```
The authenticity of host 'github.com (xxx.xxx.xxx.xxx)' can't be established.
Are you sure you want to continue connecting (yes/no)?
```
`yes` と入力してください。

成功すると以下のメッセージが表示されます：
```
Hi kairiadlimix! You've successfully authenticated, but GitHub does not provide shell access.
```

### 5. プッシュ

```bash
git push -u origin main
```

## 新しいSSH鍵を生成する場合（既存の鍵を使わない場合）

もし新しいSSH鍵を生成したい場合は：

```bash
# SSH鍵を生成（ed25519形式を推奨）
ssh-keygen -t ed25519 -C "your_email@example.com"

# または、RSA形式（古いシステムとの互換性が必要な場合）
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

生成時に以下を聞かれます：
- **ファイルの保存場所**: Enterキーでデフォルト（`~/.ssh/id_ed25519`）を使用
- **パスフレーズ**: 任意（セキュリティのため設定推奨）

生成後、上記の手順2から実行してください。

## トラブルシューティング

### SSH接続が失敗する場合

1. **SSHエージェントを起動**
   ```bash
   eval "$(ssh-agent -s)"
   ```

2. **SSH鍵をエージェントに追加**
   ```bash
   ssh-add ~/.ssh/id_ed25519
   ```

3. **接続テストを再実行**
   ```bash
   ssh -T git@github.com
   ```

### 複数のSSH鍵がある場合

`~/.ssh/config` ファイルを作成して設定：

```bash
# ~/.ssh/config
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
```

