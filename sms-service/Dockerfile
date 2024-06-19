FROM python:3.10-slim

RUN apt update && apt install -y gcc

ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /usr/src/sms
COPY reqs.txt ./reqs.txt

RUN pip install --upgrade pip && pip install -r reqs.txt

COPY . .