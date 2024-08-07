from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
from dotenv import load_dotenv
import os
import sounddevice as sd
import json
import numpy as np

# .envファイルから環境変数を読み込む
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

logging.basicConfig(level=logging.DEBUG)

# 環境変数からAPIキーとURLを取得する
DIFY_API_KEY = os.getenv('DIFY_API_KEY')
DIFY_API_URL = os.getenv('DIFY_API_URL')

host = "127.0.0.1"
port = "50021"
speaker = 4

def post_audio_query(text: str) -> dict:
    params = {"text": text, "speaker": speaker}
    res = requests.post(
        f"http://{host}:{port}/audio_query",
        params=params,
    )
    query_data = res.json()
    return query_data

def post_synthesis(query_data: dict) -> bytes:
    params = {"speaker": speaker}
    headers = {"content-type": "application/json"}
    res = requests.post(
        f"http://{host}:{port}/synthesis",
        data=json.dumps(query_data),
        params=params,
        headers=headers,
    )
    return res.content

def play_wavfile(wav_data: bytes):
    sample_rate = 24000
    wav_array = np.frombuffer(wav_data, dtype=np.int16)
    sd.play(wav_array, sample_rate, blocking=True)

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    app.logger.debug(f"Received request: {request.json}")

    try:
        data = request.json
        message = data['message']

        headers = {
            'Authorization': f'Bearer {DIFY_API_KEY}',
            'Content-Type': 'application/json'
        }

        payload = {
            'inputs': {},
            'query': message,
            'response_mode': 'blocking',
            'conversation_id': '',
            'user': 'user'
        }

        response = requests.post(DIFY_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        app.logger.debug(f"Dify API response: {response.text}")
        dify_response = response.json()

        # 生成された応答メッセージを取得
        answer = dify_response['answer']

        # VoicevoxのAPIを使用して音声を生成
        query_data = post_audio_query(answer)
        wav_data = post_synthesis(query_data)
        play_wavfile(wav_data)

        return jsonify({'response': answer})
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error calling Dify API: {e}")
        return jsonify({'error': f'Failed to get response from Dify API: {str(e)}'}), 500
    except KeyError as e:
        app.logger.error(f"KeyError: {e}")
        return jsonify({'error': f'Invalid response format from Dify API: {str(e)}'}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
