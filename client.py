import requests
import pyaudio
import sys

prompt = sys.stdin.read()

# Initialize PyAudio
sample_rate = 24000
p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paFloat32,
    channels=1,
    rate=sample_rate,
    output=True
)

# Send POST request and stream the response
response = requests.post('http://127.0.0.1:5001/prompt', data=prompt, stream=True)

if response.status_code != 200:
    print(f"Error (status: {response.status_code}): {response.text}")
    exit(1)

# Playback the streamed WAV file as it is received
raw = response.raw
while True:
    chunkLengthBytes = raw.read(4)
    if not chunkLengthBytes:
        break

    chunkLength = int.from_bytes(chunkLengthBytes, byteorder='big')
    chunk = raw.read(chunkLength)
    if not chunk:
        break

    stream.write(chunk)

# Cleanup PyAudio
stream.stop_stream()
stream.close()
p.terminate()
