FROM python:3.6.1-alpine

RUN apk update && apk add gcc make musl-dev python3-dev

ARG redis_host=localhost
ARG redis_port=6379
ARG app_config=development
ARG mapbox_access_token

ENV APP_DIR /app
ENV APP_PORT 5000

ENV REDIS_HOST $redis_host
ENV REDIS_PORT $redis_port
ENV MAPBOX_ACCESS_TOKEN $mapbox_access_token
ENV APP_CONFIG $app_config

RUN mkdir $APP_DIR
WORKDIR $APP_DIR

COPY ./requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE $APP_PORT

CMD ["python", "main.py"]
