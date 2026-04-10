# SNS自動化システム セットアップガイド

## ステップ1: Python環境セットアップ（5分）

```bash
cd sns-automation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## ステップ2: APIキー取得・設定

### 2-1. Anthropic APIキー（必須・最優先）
1. https://console.anthropic.com/ にアクセス
2. アカウント作成（またはログイン）
3. API Keys → Create Key
4. クレジットを追加（$5〜で十分スタートできる）

### 2-2. Stability AI APIキー（画像生成用）
1. https://platform.stability.ai/ にアクセス
2. アカウント作成
3. API Keys からキーを取得
4. 無料クレジットあり（25クレジット）

### 2-3. .envファイル作成
```bash
cp .env.example .env
# .env を開いて取得したAPIキーを貼り付け
```

## ステップ3: ツールインストール

### ffmpeg（動画生成用）
```bash
brew install ffmpeg
```

### VOICEVOX（音声生成用）
1. https://voicevox.hiroshiba.jp/ からダウンロード
2. アプリを起動しておく（バックグラウンドでOK）
3. http://localhost:50021 でAPIが動く

## ステップ4: 動作確認

```bash
# ダッシュボードを起動
python run.py

# ブラウザで http://localhost:5555 を開く
# 「台本を一括生成」ボタンを押す
```

## 日常の使い方

### パターンA: ダッシュボードで操作（おすすめ）
```bash
python run.py
# → ブラウザで確認・承認・投稿
```

### パターンB: コマンドラインで一括実行
```bash
python run.py generate   # 台本生成
python run.py images     # 画像生成
python run.py audio      # 音声生成
python run.py video      # 動画組み立て
python run.py all        # 全部一気に
```

## 優先順位（何から登録すべきか）

| 順番 | サービス | 必要度 | 目的 |
|------|---------|--------|------|
| 1 | Anthropic API | 必須 | 台本・キャプション生成 |
| 2 | ffmpeg | 必須 | 動画組み立て |
| 3 | Stability AI | 高 | AI画像生成 |
| 4 | VOICEVOX | 高 | ナレーション音声 |
| 5 | Instagram Business | 中 | 自動投稿（後で） |
| 6 | TikTok API | 中 | 自動投稿（後で） |
