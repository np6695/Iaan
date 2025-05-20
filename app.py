import os
import logging
import traceback
from flask import Flask, request, render_template, send_file
from dotenv import load_dotenv
import openai
import requests
from io import BytesIO

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)

# 환경변수 로딩
load_dotenv()

# API 키 세팅
openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

# Flask 앱 생성
app = Flask(__name__)

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    try:
        # 사용자 입력 텍스트
        user_input = request.form.get("text")
        app.logger.debug(f"사용자 입력: {user_input}")

        # GPT 응답 생성
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )
        answer = completion.choices[0].message.content
        app.logger.debug(f"GPT 응답: {answer}")

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

        app.logger.debug(f"TTS 응답 상태 코드: {tts_response.status_code}")

        if tts_response.status_code != 200:
            app.logger.error(f"TTS 실패: {tts_response.text}")
            return {"error": "TTS 실패", "details": tts_response.text}, 500

        return send_file(BytesIO(tts_response.content), mimetype="audio/mpeg")

    except Exception as e:
        traceback.print_exc()
        app.logger.error(f"서버 처리 중 예외 발생: {str(e)}")
        return {"error": "서버 오류", "details": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

