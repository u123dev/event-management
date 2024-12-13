FROM python:3.12-slim
LABEL maintainer="u123@ua.fm"

ENV PYTHONUNBUFFERED 1

WORKDIR app/

COPY requirements.txt ./
RUN pip install -r  requirements.txt
COPY . .
