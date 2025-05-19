from flask import Flask, render_template, request, send_file
from openai import OpenAI
import requests
from tempfile import NamedTemporaryFile
import os
from dotenv import load_dotenv

# .env 불러오기
load_dotenv()

# === 환경변수에서 키 불러오기 ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    print(">>> /process 요청 받음")

    user_input = request.form["text"]
    print(f">>> 사용자 입력: {user_input[:100]}...")

    if len(user_input) > 3000:
        print(">>> 입력 너무 김")
        return "질문이 너무 길어요. 3000자 이하로 줄여주세요.", 400

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "너는 다정하고 따뜻한 남성 비서 '이안'이야."},
                {"role": "user", "content": user_input}
            ],
            timeout=120
        )
        reply_text = response.choices[0].message.content
        try:
            print(f">>> GPT 응답: {reply_text[:100]}...")
        except UnicodeEncodeError:
            print(">>> GPT 응답: (출력 불가)")
    except Exception as e:
        print(">>> GPT 오류:", e)
        return "GPT Error", 500

    try:
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "text": reply_text,
            "voice_settings": {
                "stability": 0.7,
                "similarity_boost": 0.8
            }
        }
        tts_response = requests.post(tts_url, headers=headers, json=data)
        if tts_response.status_code != 200:
            print(">>> TTS 오류:", tts_response.status_code, tts_response.text)
            return "TTS Error", 500

        with NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            temp_audio.write(tts_response.content)
            return send_file(temp_audio.name, mimetype="audio/mpeg")

    except Exception as e:
        print(">>> ElevenLabs 오류:", e)
        return "TTS Error", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)