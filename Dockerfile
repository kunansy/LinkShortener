FROM python:3.9

WORKDIR /app
COPY . /app

RUN apt update && apt upgrade -y && apt install python3-pip -y && pip3 install -r requirements.txt

CMD ['python3', './server.py']
