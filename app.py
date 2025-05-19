import os
from flask import Flask, request, send_file, render_template
from openai import OpenAI
import requests
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    try:
        user_input = request.form.get("text", "")
        if not user_input:
            return {"error": "No input provided."}, 400

        # Get GPT response
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "너는 친절하고 다정한 남성 비서야."},
                {"role": "user", "content": user_input}
            ]
        )

        answer = completion.choices[0].message.content.strip()

        # TTS with ElevenLabs
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
            return {"error": "TTS 실패", "details": tts_response.text}, 500

        return send_file(BytesIO(tts_response.content), mimetype="audio/mpeg")

    except Exception as e:
        return {"error": "서버 오류", "details": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
