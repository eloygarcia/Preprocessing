#FROM nvidia/cuda:12.0.0-devel-ubuntu22.04
FROM nvidia/cuda:13.1.0-devel-ubuntu24.04
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
# RUN apt-get install -y tzdata
LABEL authors="eloygarcia"

# ENTRYPOINT ["top", "-b"]
RUN set -ex
RUN apt-get update
RUN apt-get install -y g++ curl libzmq3-dev wget git
RUN apt-get install -y libx11-dev libxt-dev xserver-xorg-dev xorg-dev
RUN apt-get install -y ffmpeg libsm6 libxext6
RUN apt-get install -y libgl1-mesa-dev libssl-dev

RUN apt-get install -y software-properties-common

RUN apt-get install -y python3-pip
## Check if the package is available in the default repositories
RUN python3 -m pip config set global.break-system-packages true 

RUN apt-get install -y libjpeg-dev
RUN pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu130

COPY requirements.txt ./home/
RUN pip install -r ./home/requirements.txt

RUN git clone https://github.com/pytorch/captum.git ./home/captum
RUN cd ./home/captum
RUN pip install -e .

# https://github.com/meta-pytorch/captum/tree/master
# To customize the installation, you can also run the following variants of the above:
# 1. Also installs all tools necessary for development (testing, linting, docs building; see Contributing below).
# RUN pip install -e .[dev]
# 2. Also installs all packages necessary for running the tutorial notebooks.
# RUN pip install -e .[tutorials]
# To execute unit tests from a manual install, run:

# running a single unit test
# python -m unittest -v tests.attr.test_saliency
# running all unit tests
# pytest -ra
