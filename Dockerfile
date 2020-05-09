FROM python:3.8.2-slim-buster

ENV BOOST_VERSION=1.73.0
ENV BOOST_DIR=/root

RUN  apt-get -y update 

# && apt install -y wget

#  && apt install -y p7zip-full

# RUN wget https://dl.bintray.com/boostorg/release/1.73.0/source/boost_1_73_0.7z && \
#     7z x boost_1_73_0.7z && \
#     rm -r boost_1_73_0.7z && \
#     cd boost_1_73_0 && \
#     ./bootstrap.sh --with-libraries=python && \
#     ./b2 && \
#     ./b2 install -y

RUN apt-get install -y git

RUN apt-get install -y sqlite3 libsqlite3-dev

RUN apt-get install -y --fix-missing \
    g++ \
    gdb \
    gcc \
    cmake \
    libboost-all-dev

# RUN git clone --recursive https://github.com/boostorg/boost.git \
#     && cd boost \
#     && git checkout develop \
#     && ./bootstrap.sh \
#     && ./b2 headers

RUN mkdir -p /project/face-project

WORKDIR /project/face-project

RUN cd ~ && \
    mkdir -p dlib && \
    git clone -b 'v19.9' --single-branch https://github.com/davisking/dlib.git dlib/ && \
    cd  dlib/ && \
    python3 setup.py install --yes USE_AVX_INSTRUCTIONS

COPY . .

RUN pip install -r requirements.txt

CMD python app.py
