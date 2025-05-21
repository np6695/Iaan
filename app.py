import os
from flask import Flask, request, render_template, send_file
import requests
from io import BytesIO
from dotenv import load_dotenv
import base64

load_dotenv()
GOOGLE_TTS_API_KEY = os.getenv("GOOGLE_TTS_API_KEY")

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    try:
        user_text = request.form.get("text")

        endpoint = "https://texttospeech.googleapis.com/v1/text:synthesize"
        headers = {
            "X-Goog-Api-Key": GOOGLE_TTS_API_KEY,
            "Content-Type": "application/json; charset=utf-8"
        }
        body = {
            "input": {"text": user_text},
            "voice": {
                "languageCode": "ko-KR",
                "name": "ko-KR-Neural2-A" # 남성 음성
            },
            "audioConfig": {"audioEncoding": "MP3"}
        }

        response = requests.post(endpoint, headers=headers, json=body)
        result = response.json()

        if "audioContent" not in result:
            return {"error": "TTS 변환 실패", "details": result}, 500

        # base64 디코딩
        audio_data = base64.b64decode(result["audioContent"])
        audio_stream = BytesIO(audio_data)
        audio_stream.seek(0)

        return send_file(audio_stream, mimetype="audio/mpeg")

    except Exception as e:
        return {"error": "서버 오류", "details": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
