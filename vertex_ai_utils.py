import os
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from dotenv import load_dotenv

# 環境変数のロード
load_dotenv()

# Vertex AI の初期化
def init_vertex_ai():
    """Vertex AI を初期化"""
    project_id = os.environ.get("VERTEX_AI_PROJECT_ID")
    location = os.environ.get("VERTEX_AI_LOCATION", "us-central1")
    
    print(f"Initializing Vertex AI with project_id={project_id}, location={location}")
    
    vertexai.init(
        project=project_id,
        location=location,
    )

# Gemini モデルを使用して回答を生成
def generate_response(prompt, temperature=0.2):
    """Vertex AI を使用して回答を生成"""
    try:
        # Vertex AI を初期化
        init_vertex_ai()
        
        # モデルID
        model_id = os.environ.get("VERTEX_AI_MODEL_ID", "gemini-2.5-pro-preview-03-25")
        
        # モデルのインスタンス化
        # 注意: locationパラメータは使用しない（エラーの原因になる）
        model = GenerativeModel(model_name=model_id)
        
        print(f"Using model: {model_id}")
        
        # 生成パラメータ
        generation_config = {
            "temperature": temperature,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        # システムプロンプトを追加
        system_prompt = """あなたはSlackボットとして動作する便利なアシスタントです。
質問に対して簡潔かつ丁寧に回答してください。
企業内での使用を想定しているため、専門的かつ礼儀正しい言葉遣いを心がけてください。"""
        
        # 応答の生成（位置引数としてcontentを渡す）
        content = [Part.from_text(system_prompt), Part.from_text(prompt)]
        # 注意: contentは名前付き引数でなく位置引数として渡す
        response = model.generate_content(content, generation_config=generation_config)
        
        return response.text
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Vertex AI Error: {str(e)}\n{error_details}")
        return f"エラーが発生しました: {str(e)}"

def generate_thread_summary(thread_messages, temperature=0.2):
    """スレッドの会話を要約"""
    try:
        # Vertex AI を初期化
        init_vertex_ai()
        
        # モデルID
        model_id = os.environ.get("VERTEX_AI_MODEL_ID", "gemini-2.5-pro-preview-03-25")
        
        # モデルのインスタンス化
        # 注意: locationパラメータは使用しない（エラーの原因になる）
        model = GenerativeModel(model_name=model_id)
        
        # 生成パラメータ
        generation_config = {
            "temperature": temperature,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        # システムプロンプト
        system_prompt = """あなたはSlackのスレッドを要約する専門家です。
以下のルールに従って要約を作成してください：
1. スレッドの主要な議論や決定事項を中心に要約する
2. 重要な事実や数字は正確に保持する
3. 箇条書きで要点をまとめる
4. 専門的かつ客観的な言葉遣いを使用する
5. 要約は簡潔にし、元の会話の10%以下の長さに収める"""
        
        # 会話形式に整形
        formatted_thread = thread_messages
        
        # 応答の生成（位置引数としてcontentを渡す）
        content = [Part.from_text(system_prompt), Part.from_text(formatted_thread)]
        # 注意: contentは名前付き引数でなく位置引数として渡す
        response = model.generate_content(content, generation_config=generation_config)
        
        # 要約の前に簡単な説明を追加
        return f"📝 *スレッド要約*\n\n{response.text}"
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Vertex AI Error: {str(e)}\n{error_details}")
        return f"要約の生成中にエラーが発生しました: {str(e)}"