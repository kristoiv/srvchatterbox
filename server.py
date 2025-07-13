import sys
if len(sys.argv) < 2:
	print(f'Usage: {sys.argv[0]} <voice-base.wav> [<output-file.wav> [<exaggeration 0.5> [<cfg_weight 0.5>]]]')
	sys.exit(1)

voice_base_prompt = sys.argv[1]
print(f';;; voice_base_prompt={voice_base_prompt}')

output_file = "output.wav"
if len(sys.argv) > 2:
	output_file = sys.argv[2]
print(f';;; output_file={output_file}')

exaggeration = float(0.5)
if len(sys.argv) > 3:
	exaggeration = float(sys.argv[3])
print(f';;; exaggeration={exaggeration}')

cfg_weight = float(0.5)
if len(sys.argv) > 4:
	cfg_weight = float(sys.argv[4])
print(f';;; cfg_weight={cfg_weight}')

import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
from flask import Flask, Response, request, stream_with_context
import re

# Detect device (Mac with M1/M2/M3/M4)
device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
print(f';;; device={device}')

if device == "mps":
    map_location = torch.device(device)
    torch_load_original = torch.load
    def patched_torch_load(*args, **kwargs):
        if 'map_location' not in kwargs:
            kwargs['map_location'] = map_location
        return torch_load_original(*args, **kwargs)
    torch.load = patched_torch_load

model = ChatterboxTTS.from_pretrained(device=device)
app = Flask(__name__)

def generatePcmChunks(prompt: str):
    app.logger.info(f'Generating stream for prompt: {prompt}')
    sentences = re.split(r'(?<=[.!?])\s+', prompt.strip())
    paragraphs = ['']
    for s in sentences:
        currParaLen = len(paragraphs[-1])
        if currParaLen > 500:
            paragraphs.append('')
        paragraphs[-1] = ' '.join([paragraphs[-1], s]).strip()
    paraTotal = len(paragraphs)
    for paraIdx, para in enumerate(paragraphs):
        for audio_chunk, metrics in model.generate_stream(
            para,
            audio_prompt_path=voice_base_prompt,
            exaggeration=exaggeration,
            cfg_weight=cfg_weight,
            chunk_size=50 if "cuda" else 100
        ):
            app.logger.info(f"Generated chunk {(paraIdx+1)}/{paraTotal}-{metrics.chunk_count}, RTF: {metrics.rtf:.3f}" if metrics.rtf else f"Generated chunk {(paraIdx+1)}/{paraTotal}-{metrics.chunk_count}")
            yield audio_chunk.numpy().tobytes()

@app.route('/prompt', methods=['POST'])
def stream():
    app.logger.info('Stream opened!')
    @stream_with_context
    def generate():
        chunks = generatePcmChunks(request.data.decode('utf-8').rstrip())
        for pcm_data in chunks:
            length = len(pcm_data)
            app.logger.info(f'Shipping pcm-data to client of size: {length}')
            yield length.to_bytes(4, byteorder='big')
            yield pcm_data
    return Response(generate(), mimetype='application/octet-stream')

if __name__ == '__main__':
    import logging
    app.logger.setLevel(logging.DEBUG)
    app.logger.info('Starting app server')
    app.run(host='0.0.0.0', port=5001)
