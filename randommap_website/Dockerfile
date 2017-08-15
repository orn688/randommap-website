FROM python:3.6.1-alpine

RUN apk update && apk add gcc make musl-dev python3-dev

ENV APP_DIR /app

# These will be overridden by Docker Compose
ENV APP_PORT 5000
ENV REDIS_HOST localhost
ENV REDIS_PORT 6379
ENV MAPBOX_ACCESS_TOKEN dummy_token
ENV DEBUG true

RUN mkdir $APP_DIR
WORKDIR $APP_DIR
RUN mkdir maps

COPY ./requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE $APP_PORT

CMD ["python", "main.py"]
