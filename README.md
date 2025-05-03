# Slack スレッド要約ボット

Vertex AI Gemini を利用して Slack スレッドを自動要約する Bot です。スレッド内で「@bot 要約」または「@bot summarize」と入力するだけで、AIがスレッドの内容をコンパクトにまとめます。

## 概要

- スレッド内の会話を自動要約（Vertex AI Gemini 利用）
- Slack ワークスペース内で簡単に導入可能

## システム要件

- Python 3.9+
- Google Cloud Platform アカウント（Vertex AI API 有効化済み）
- Slack ワークスペースの管理者権限またはアプリ作成権限

## 簡易セットアップ

1. 環境変数の設定
```
# .env ファイルを修正

2. 依存関係のインストール
```
pip install -r requirements.txt
```

3. アプリケーションの実行
```
python app.py
```

## 使用方法

1. ボットをチャンネルに招待: `/invite @your_bot_name`
2. スレッド内でボットを呼び出す: `@your_bot_name 要約` または `@your_bot_name summarize`

## ファイル構成

- `app.py`: メインアプリケーション
- `slack_utils.py`: Slack API 関連機能
- `vertex_ai_utils.py`: Vertex AI 関連機能
- `nginx/`: Nginx 設定ファイル（本番環境用）
- `systemd/`: Systemd サービス設定（本番環境用）

## ライセンス

MIT