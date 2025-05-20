import os
from flask import Flask, request, send_file, jsonify
import openai
import requests
from io import BytesIO

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# 환경 변수에서 키 불러오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

openai.api_key = OPENAI_API_KEY

@app.route('/')
def index():
    return "이안 백엔드 작동 중입니다."

@app.route('/process', methods=['POST'])
def process():
    try:
        user_input = request.form.get("text")
        print(f"[입력된 텍스트] {user_input}")

        # GPT 응답 생성
        gpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}],
        )
        answer = gpt_response.choices[0].message.content.strip()
        print(f"[GPT 응답] {answer}")

        # ElevenLabs TTS 요청
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        tts_response = requests.post(
            tts_url,
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "text": answer,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.4,
                    "similarity_boost": 0.8
                }
            }
        )

        print(f"[TTS 응답 코드] {tts_response.status_code}")

        if tts_response.status_code != 200:
            print(f"[TTS 실패 응답] {tts_response.text}")
            return {"error": "TTS 실패", "details": tts_response.text}, 500

        return send_file(BytesIO(tts_response.content), mimetype="audio/mpeg")

    except Exception as e:
        import traceback
        print("=== 서버 처리 중 예외 발생 ===")
        traceback.print_exc()
        return {"error": "서버 오류", "details": str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
