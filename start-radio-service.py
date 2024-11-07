from flask import Flask, request, jsonify
from pydub import AudioSegment
from pydub.playback import play
import threading
import requests
import io

app = Flask(__name__)
player_thread = None
is_playing = False

def play_stream(url):
    global is_playing
    try:
        # Получаем аудио поток
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            audio_data = io.BytesIO(response.content)
            audio = AudioSegment.from_file(audio_data, format="mp3")
            is_playing = True
            play(audio)
        else:
            print("Failed to fetch audio stream.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        is_playing = False

@app.route('/play', methods=['POST'])
def start_playing():
    global player_thread, is_playing
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    if is_playing:
        return jsonify({"message": "Radio is already playing"}), 200

    player_thread = threading.Thread(target=play_stream, args=(url,))
    player_thread.start()
    return jsonify({"message": f"Started playing radio from {url}"}), 200

@app.route('/stop', methods=['POST'])
def stop_playing():
    global is_playing
    if is_playing:
        is_playing = False
        return jsonify({"message": "Radio stopped"}), 200
    else:
        return jsonify({"message": "Radio is not playing"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
