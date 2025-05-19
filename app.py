import os
from flask import Flask, request, send_file, jsonify
from openai import OpenAI
import requests
from io import BytesIO
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

@app.route("/")
def index():
    return "이안 백엔드 작동 중입니다."

@app.route("/process", methods=["POST"])
def process():
    try:
        user_input = request.form.get("text", "")
        if not user_input:
            return jsonify({"error": "No text provided"}), 400

        # GPT 응답 생성
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "너는 친절하고 따뜻한 남성 비서야."},
                {"role": "user", "content": user_input}
            ]
        )

        answer = completion.choices[0].message.content.strip()

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

        if tts_response.status_code != 200:
            return jsonify({"error": "TTS 요청 실패", "details": tts_response.text}), 500

        audio_data = BytesIO(tts_response.content)
        return send_file(audio_data, mimetype="audio/mpeg")

    except Exception as e:
        return jsonify({"error": "서버 처리 중 오류 발생", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
