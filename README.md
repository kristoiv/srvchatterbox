# srvchatterbox
Simple client/server rig for running chatterbox tts / voice cloning on digitalocean gpu droplets (1xH100)

### Requirements:

Does work locally for development purposes on an Apple Macbook Pro 16" M2 MAX 96GB ram laptop (however slowly). However chatterbox requires a faster GPU
for more practical use and better than real-time audio production. This repo is used by the author to quickly run it on a Digitalocean (DO) gpu droplet featuring
a NVIDIA H100 GPU (80gb vram). There it produces audio quickly, far beyond real-time.

NOTE: The repo is missing a voice.wav file which is required. Make it a clean audio recording 5-15s, with a voice you find pleasant. Limit background noise.

###  Initial setup of local python venv and deps
```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
$ python3 -m pip install "chatterbox-tts==0.1.1" "chatterbox-streaming==0.1.2" "flask==3.1.1" "requests==2.32.4" "pyaudio==0.2.14"
```

### Run locally for development
```bash
# Console 1 - Run server
$ python3 server.py voice.wav

# Console 2 - Run client with prompt on stdin
$ python3 client.py
Prompt:
Hello world!
^D
$ echo "Hello world\!" | python3 client.py
```

### Digitalocean GPU droplet (expects DO AI/ML Ready image) setup and use:
```bash
# Console 1 - Optionally prepare digitalocean droplet with the petunia-image:v0, then serve request from the servers localhost:5000
$ export DOIP=192....
$ make prepare-do
# Run server in the cloud
$ make serve-do
# Update python/voice clone wav and then run
$ make update-do serve-do

# Console 2 - Ssh port forward from localhost:5001 on host, to localhost:5001 on server droplet
$ export DOIP=192....
$ make forward-port

# Console 3 - Speak
$ export DOIP=192....
$ make speak
Prompt:
Hello world!
^D
$ echo "Hello world\!" | make speak
```
