FROM python:alpine

# build takes up to 30 minutes, so we'll stick to copying the binary for now

RUN apk add -U git \
               g++ \
               cmake \
               make \
               boost-dev \
               doxygen \
               python3-dev \
               py3-pip \
               libffi-dev \
               openssl-dev

RUN git clone --depth=1 --recursive https://github.com/SebastianSchlag/kahypar.git

RUN cd kahypar && git fetch --all --tags && \
    git checkout tags/1.2.1 && \
    mkdir build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=RELEASE && make -j8

RUN ln -s /kahypar/build/kahypar/application/KaHyPar /usr/local/bin/kahypar
