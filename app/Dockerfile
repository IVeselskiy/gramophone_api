FROM python:3-alpine

WORKDIR /app

RUN apk update

RUN apk upgrade

RUN apk add ffmpeg

COPY requirements.txt /app/

RUN python -m pip install --upgrade pip

RUN python -m pip install -r /app/requirements.txt

COPY . /app

EXPOSE 5000

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]
