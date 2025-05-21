import os
import logging
from flask import Flask, render_template, request, send_file
from io import BytesIO
from dotenv import load_dotenv
import openai
from google.cloud import texttospeech

# .env 로드
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_TTS_CREDENTIALS")

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    print("== 요청 수신 ==")

    try:
        user_input = request.form["text"]
        print("사용자 입력:", user_input)

        # GPT 응답
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )
        answer = response.choices[0].message.content.strip()
        print("GPT 응답:", answer)

        # Google TTS
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=answer)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ko-KR",
            name="ko-KR-Neural2-C" # 남성 목소리
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        print("TTS 요청 전송 중...")
        tts_response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        print("TTS 응답 수신 완료")

        return send_file(BytesIO(tts_response.audio_content), mimetype="audio/mpeg")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"서버 처리 중 예외 발생: {str(e)}")
        return {"error": "서버 오류", "details": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
