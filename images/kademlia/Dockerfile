FROM python:3-alpine

RUN pip3 install kademlia && apk add iputils && mkdir /app

ADD main.py /app/main.py

ENTRYPOINT ["python3", "/app/main.py"]
