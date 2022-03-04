FROM python:latest
RUN apt-get update && apt-get -y install build-essential gcc pkg-config cmake
RUN mkdir -p /usr/src
WORKDIR /usr/src
RUN git clone --recursive https://github.com/bingmann/cobs.git
WORKDIR /usr/src/cobs
RUN python setup.py install
COPY requirements.txt /usr/src/app/
RUN pip install -r /usr/src/app/requirements.txt
COPY app.py /usr/src/app
COPY config/ /usr/src/app
WORKDIR /usr/src/app
ENTRYPOINT ["hug", "-f", "app.py"]
#CMD ["cli.py"]
