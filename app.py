import os
import requests
from flask import Flask, request, render_template, send_file, jsonify
from io import BytesIO
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# 환경변수에서 API 키 불러오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    try:
        text = request.form["text"]

        # OpenAI GPT 응답 생성
        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text}]
        )
        answer = response.choices[0].message.content.strip()
        print("GPT 응답:", answer)

        # ElevenLabs TTS 호출
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
            return {"error": "TTS 실패", "details": tts_response.text}, 500

        return send_file(BytesIO(tts_response.content), mimetype="audio/mpeg")

    except Exception as e:
        print(f"서버 처리 중 예외 발생: {str(e)}")
        return {"error": "서버 오류", "details": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
