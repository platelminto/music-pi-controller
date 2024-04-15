import os
import dotenv
from flask import Flask, jsonify, request, render_template

dotenv.load_dotenv()

app = Flask(__name__)

# Dictionary holding the state of each LED
led_states = {18: 0, 23: 0, 24: 0, 25: 0, 8: 0, 7: 0, 1: 0}


@app.route('/')
def index():
    return render_template('leds.html')


@app.route('/get-led-states', methods=['GET'])
def get_led_states():
    return jsonify(led_states)


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('FLASK_PORT', 5000)), debug=True)
