FROM python:3.6.1-alpine

RUN apk update && apk add gcc make musl-dev python3-dev

ENV PORT 5000
ENV REDIS_URL redis://localhost:6379
ENV APP_CONFIG development
ENV MAPBOX_ACCESS_TOKEN mapbox_access_token

ENV APP_DIR /app

RUN mkdir $APP_DIR
WORKDIR $APP_DIR

COPY ./requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE $PORT

# Don't run as root, since Heroku doesn't grant root privileges
RUN adduser -D randommap
USER randommap

CMD ["python", "main.py"]
