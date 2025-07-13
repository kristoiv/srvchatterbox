.PHONY: help prepare-do update-do serve-do forward-port speak check-env-do

help:
	@echo "Usage: make prepare-do serve-do"

prepare-do: check-env-do voice.wav
	@echo "Preparing root@${DOIP}"
	scp server.py voice.wav root@${DOIP}:./
	ssh root@${DOIP} " \
	  docker pull nvcr.io/nvidia/pytorch:25.01-py3 && \
	  docker rm -f srvchatterbox srvchatterbox-build && \
	  docker rmi -f srvchatterbox-build:v0 && \
	  docker run --name srvchatterbox-build --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 nvcr.io/nvidia/pytorch:25.01-py3 bash -c 'python3 -m venv .venv && source .venv/bin/activate && pip install \"chatterbox-tts==0.1.1\" \"chatterbox-streaming==0.1.2\" \"flask==3.1.1\"' && \
	  docker commit srvchatterbox-build srvchatterbox-image:v0 && \
	  echo "Done!" \
	"

update-do: check-env-do voice.wav
	@echo "Updating root@${DOIP}"
	scp server.py voice.wav root@${DOIP}:./
	ssh root@${DOIP} "docker rm -f srvchatterbox"

serve-do: check-env-do voice.wav
	ssh root@${DOIP} " \
	  docker rm -f srvchatterbox && \
	  docker run --rm --name srvchatterbox --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 -v /root:/workspace/files -p 5001:5001 srvchatterbox-image:v0 bash -c 'source .venv/bin/activate && python3 files/server.py files/voice.wav' \
	"

forward-port: check-env-do
	ssh -L5001:localhost:5001 root@${DOIP}

speak:
	@if [ -t 0 ]; then \
		echo "Prompt:"; \
	fi; \
	bash -c "source .venv/bin/activate && python3 client.py"

check-env-do:
ifndef DOIP
	$(error DOIP envvar is required)
endif
