FROM python:3.9.6-slim-buster
ENV PYTHONUNBUFFERED=1
# RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . /app
EXPOSE 8000