import os
import requests
from flask import Flask, request, send_file, jsonify
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

@app.route('/')
def index():
    return "이안 백엔드 작동 중입니다."

@app.route('/process', methods=['POST'])
def process():
    try:
        user_text = request.form['text']
        print(f"입력된 텍스트: {user_text}")

        # GPT 응답 생성
        gpt_response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "너는 친절하고 다정한 남성 비서야."},
                    {"role": "user", "content": user_text}
                ]
            }
        )
        gpt_response.raise_for_status()
        answer = gpt_response.json()['choices'][0]['message']['content']
        print(f"GPT 응답: {answer}")

        # ElevenLabs TTS 요청
        tts_response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
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

        print(f"TTS 응답 코드: {tts_response.status_code}")
        if tts_response.status_code != 200:
            print(f"TTS 실패: {tts_response.text}")
            return jsonify({"error": "TTS 실패", "details": tts_response.text}), 500

        # 음성 데이터 전송
        audio_stream = BytesIO(tts_response.content)
        audio_stream.seek(0)
        return send_file(audio_stream, mimetype="audio/mpeg")

    except Exception as e:
        print(f"서버 처리 중 예외 발생: {str(e)}")
        return jsonify({"error": "서버 오류", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
