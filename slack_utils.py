import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# .envファイルから環境変数をロード
load_dotenv()

def send_slack_message(channel_id, message, thread_ts=None):
    """Slackにメッセージを送信"""
    client = WebClient(token=os.environ.get('SLACK_BOT_TOKEN'))
    
    try:
        # スレッドの返信として送信するかどうかを判定
        if thread_ts:
            response = client.chat_postMessage(
                channel=channel_id,
                text=message,
                thread_ts=thread_ts
            )
        else:
            response = client.chat_postMessage(
                channel=channel_id,
                text=message
            )
        return response
    except SlackApiError as e:
        print(f"Error sending message: {e}")
        return None

def get_thread_messages(channel_id, thread_ts):
    """指定されたスレッドのメッセージを取得する"""
    client = WebClient(token=os.environ.get('SLACK_BOT_TOKEN'))
    
    try:
        # スレッドの返信を取得
        response = client.conversations_replies(
            channel=channel_id,
            ts=thread_ts
        )
        
        # ボット自身のIDを取得
        bot_info = client.auth_test()
        bot_id = bot_info['user_id']
        
        # メッセージの整形（ボット自身のメッセージを除外）
        messages = []
        for msg in response['messages']:
            # ボット自身のメッセージまたは「考え中です...」のメッセージは除外
            if 'user' in msg and msg['user'] == bot_id:
                if '考え中です...' in msg.get('text', ''):
                    continue
            
            # メッセージの送信者とテキストを取得
            user_info = None
            if 'user' in msg:
                try:
                    user_info = client.users_info(user=msg['user'])
                except SlackApiError:
                    pass
            
            sender = user_info['user']['real_name'] if user_info else "不明なユーザー"
            messages.append({
                'sender': sender,
                'text': msg.get('text', ''),
                'timestamp': msg.get('ts', '')
            })
        
        return messages
    except SlackApiError as e:
        print(f"Error fetching thread messages: {e}")
        return []

def format_thread_for_summary(messages):
    """スレッドのメッセージをLLMに送信する形式にフォーマット"""
    formatted_text = "以下のSlackスレッドの会話を要約してください:\n\n"
    
    for i, msg in enumerate(messages):
        formatted_text += f"{msg['sender']}: {msg['text']}\n\n"
    
    return formatted_text