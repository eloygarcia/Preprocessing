FROM nvidia/cuda:13.1.0-runtime-ubuntu24.04

ARG DEBIAN_FRONTEND=noninteractive
#ARG INSTALL_MYYOLOX=0
#ARG INSTALL_MASEG=0

ENV TZ=Etc/UTC
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

LABEL authors="Eloy García"

WORKDIR /workspace

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONPATH=/workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
	python3 \
	python3-dev \
	python3-pip \
	python3-venv \
	g++ \
	curl \
	wget \
	git \
	ffmpeg \
	libsm6 \
	libxext6 \
	libx11-6 \
	libgl1 \
	libgl1-mesa-dev \
	libssl-dev \
	python3-gdcm \
	libjpeg-dev \
	zlib1g-dev \
	&& rm -rf /var/lib/apt/lists/*

COPY requirement.txt /tmp/requirement.txt

RUN python3 -m venv "$VIRTUAL_ENV" && \
	python3 -m pip install --upgrade pip setuptools wheel && \
	grep -vE '^\s*gdcm\s*([><=].*)?$' /tmp/requirement.txt > /tmp/requirements.docker.txt && \
	pip install -r /tmp/requirements.docker.txt && \
	pip install fastapi "uvicorn[standard]" python-multipart requests

COPY . /workspace

#RUN if [ "$INSTALL_MYYOLOX" = "1" ] && [ -d "/workspace/MyYoloX" ]; then \
#		pip install -r /workspace/MyYoloX/requirements.txt && \
#		pip install -e /workspace/MyYoloX; \
#	fi

# RUN if [ "$INSTALL_MASEG" = "1" ] && [ -d "/workspace/BreastSegmentationUnet" ]; then \
#		grep -vE '^\s*gdcm\s*([><=].*)?$' /workspace/BreastSegmentationUnet/requirements.txt > /tmp/maseg.requirements.docker.txt && \
#		pip install -r /tmp/maseg.requirements.docker.txt && \
#		pip install SimpleITK; \
#	fi

CMD ["bash"]
