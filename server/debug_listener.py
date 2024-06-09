import os
import dotenv
from flask import Flask, jsonify, request, render_template

dotenv.load_dotenv()

app = Flask(__name__)

# Dictionary holding the state of each LED
led_states = {18: 0, 23: 0, 24: 0, 25: 0, 8: 0, 7: 0, 1: 0}

lyrics_text = ""


@app.route('/')
def index():
    return render_template('leds.html')


@app.route('/get-led-states', methods=['GET'])
def get_led_states():
    return jsonify(led_states)


@app.route('/get-lyrics', methods=['GET'])
def get_lyrics():
    return jsonify({'lyrics': lyrics_text})


@app.route('/set-led', methods=['POST'])
def set_led():
    data = request.json
    pin = data['pin']
    power = data['power']
    if 0 <= power <= 100:
        led_states[pin] = power
        return jsonify({'status': 'success', 'pin': pin, 'power': power})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid power value'}), 400


@app.route('/display-print', methods=['POST'])
def set_lyrics():
    data = request.json
    global lyrics_text
    lyrics_text = data['message']
    return jsonify({'status': 'success', 'lyrics': lyrics_text})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('FLASK_PORT', 5000)), debug=True)
