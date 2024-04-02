import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pyaudio
import numpy as np
import threading
import collections

# Define the maximum number of data points to display on the graph
MAX_POINTS = 50

# Initialize the queue to hold audio data, using a deque for efficient removal of old data
data_queue = collections.deque(maxlen=MAX_POINTS)

# Initialize PyAudio parameters
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
CHUNK = 2048

def calculate_band_intensity(data, rate, band):
    fft_vals = np.fft.rfft(data)
    fft_freq = np.fft.rfftfreq(len(data), 1.0 / rate)
    if band == 'bass':
        low, high = 20, 250
    elif band == 'mid':
        low, high = 250, 4000
    elif band == 'treble':
        low, high = 4000, 20000
    band_indices = np.where((fft_freq >= low) & (fft_freq <= high))[0]
    intensity = np.sum(np.abs(fft_vals[band_indices]))
    return intensity

def process_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.float32)
            bass = calculate_band_intensity(audio_data, RATE, 'bass')
            mid = calculate_band_intensity(audio_data, RATE, 'mid')
            treble = calculate_band_intensity(audio_data, RATE, 'treble')
            data_queue.append((bass, mid, treble))
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

app = dash.Dash(__name__)
app.layout = html.Div([
    dcc.Graph(id='live-graph', animate=False),
    dcc.Interval(id='graph-update', interval=CHUNK / RATE, n_intervals=0),
])

@app.callback(Output('live-graph', 'figure'), [Input('graph-update', 'n_intervals')])
def update_graph_scatter(n):
    data = list(data_queue)
    if not data:
        return go.Figure()

    # Unpack the data
    bass, mid, treble = zip(*data)
    x = list(range(len(bass)))

    traces = [
        go.Scatter(x=x, y=bass, mode='lines+markers', name='Bass'),
        go.Scatter(x=x, y=mid, mode='lines+markers', name='Mid'),
        go.Scatter(x=x, y=treble, mode='lines+markers', name='Treble'),
    ]

    # Set a fixed range for the y-axis and let the x-axis only show the last N points
    return {'data': traces, 'layout': go.Layout(xaxis=dict(range=[0, MAX_POINTS-1]),
                                                yaxis=dict(range=[0, 500]),  # Adjust the range based on expected intensity values
                                                title='Real-time Audio Intensity')}

if __name__ == '__main__':
    audio_thread = threading.Thread(target=process_audio)
    audio_thread.start()
    app.run_server(debug=True)
