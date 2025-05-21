import os
from flask import Flask, request, render_template, send_file
import requests
from io import BytesIO
from dotenv import load_dotenv
import base64
import openai

# 환경변수 불러오기
load_dotenv()
GOOGLE_TTS_API_KEY = os.getenv("GOOGLE_TTS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    try:
        user_text = request.form.get("text")

        # GPT에게 응답 생성 요청
        chat_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 사용자에게 따뜻하고 존댓말을 사용하는 한국어 남성 비서입니다."
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ]
        )
        gpt_reply = chat_response["choices"][0]["message"]["content"]

        # Google TTS 요청
        endpoint = "https://texttospeech.googleapis.com/v1/text:synthesize"
        headers = {
            "X-Goog-Api-Key": GOOGLE_TTS_API_KEY,
            "Content-Type": "application/json; charset=utf-8"
        }
        body = {
            "input": {"text": gpt_reply},
            "voice": {
                "languageCode": "ko-KR",
                "name": "ko-KR-Neural2-C"  # 한국어 남성 음성
            },
            "audioConfig": {"audioEncoding": "MP3"}
        }

        response = requests.post(endpoint, headers=headers, json=body)
        result = response.json()

        if "audioContent" not in result:
            return {"error": "TTS 변환 실패", "details": result}, 500

        # base64 → mp3 디코딩
        audio_data = base64.b64decode(result["audioContent"])
        audio_stream = BytesIO(audio_data)
        audio_stream.seek(0)

        return send_file(audio_stream, mimetype="audio/mpeg")

    except Exception as e:
        return {"error": "서버 오류", "details": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
