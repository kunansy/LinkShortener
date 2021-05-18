FROM python:3.9

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get upgrade -y && apt-get install python3-pip -y && rm -rf /var/lib/apt/lists/*
RUN pip3 install -r requirements.txt

CMD ["python3", "./server.py"]
