import os
import json
import re
import threading
from flask import Flask, request, jsonify
from slack_utils import send_slack_message, get_thread_messages, format_thread_for_summary
from vertex_ai_utils import generate_response, generate_thread_summary
from dotenv import load_dotenv

# .envファイルから環境変数をロード
load_dotenv()

app = Flask(__name__)

@app.route('/', methods=['POST'])
def root_handler():
    return handle_slack_event()

@app.route('/demo-data', methods=['POST'])
def handle_demo_data():
    return handle_slack_event()

def process_llm_response(channel_id, message, thread_ts=None):
    """LLMを使用して応答を生成し、Slackに送信"""
    try:
        # メッセージが要約コマンドかどうかを確認
        if re.search(r'summarize|要約', message.lower()):
            # スレッドが存在するか確認
            if thread_ts:
                # 処理中メッセージを送信
                processing_message = send_slack_message(channel_id, "スレッドを要約しています...", thread_ts)
                
                # スレッドのメッセージを取得
                thread_messages = get_thread_messages(channel_id, thread_ts)
                
                if thread_messages:
                    # メッセージをLLM用にフォーマット
                    formatted_thread = format_thread_for_summary(thread_messages)
                    
                    # 要約を生成
                    summary = generate_thread_summary(formatted_thread)
                    
                    # 要約をSlackに送信
                    send_slack_message(channel_id, summary, thread_ts)
                    
                    # 処理中メッセージを削除（オプション）
                    # client.chat_delete(channel=channel_id, ts=processing_message['ts'])
                else:
                    send_slack_message(channel_id, "スレッドのメッセージを取得できませんでした。", thread_ts)
            else:
                send_slack_message(channel_id, "このコマンドはスレッド内でのみ使用できます。", thread_ts)
        else:
            # 通常の応答
            ai_response = generate_response(message)
            send_slack_message(channel_id, ai_response, thread_ts)
    except Exception as e:
        error_message = f"エラーが発生しました: {str(e)}"
        send_slack_message(channel_id, error_message, thread_ts)

def handle_slack_event():
    # リクエストデータを取得
    if request.is_json:
        data = request.get_json()
    else:
        # JSONでない場合はテキストデータとして取得を試みる
        try:
            data = json.loads(request.data.decode('utf-8'))
        except:
            return jsonify({"error": "Invalid request format"}), 400
    
    # SlackのURL検証チャレンジに応答
    if data.get('challenge'):
        return jsonify({"challenge": data.get('challenge')})
    
    # イベントタイプの確認
    if data.get('type') == 'event_callback':
        event = data.get('event', {})
        
        # app_mentionイベントの処理
        if event.get('type') == 'app_mention':
            # メッセージテキストを取得
            message_text = event.get('text', '')
            # メンション部分（<@USERID>）を削除してクリーンなメッセージを取得
            clean_message = re.sub(r'<@[A-Z0-9]+>', '', message_text).strip()
            
            # チャンネルIDを取得
            channel_id = event.get('channel')
            
            # スレッドの返信先IDを取得（存在する場合）
            thread_ts = event.get('thread_ts') or event.get('ts')
            
            # 処理中メッセージを送信
            send_slack_message(channel_id, "考え中です...", thread_ts)
            
            # LLM応答を別スレッドで処理
            thread = threading.Thread(
                target=process_llm_response,
                args=(channel_id, clean_message, thread_ts)
            )
            thread.daemon = True
            thread.start()
            
            return jsonify({"status": "processing"}), 200
    
    # その他のイベントは無視
    return jsonify({"status": "ignored"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))