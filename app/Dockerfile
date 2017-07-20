FROM python:3.6.1-alpine

ENV FLASK_PORT 5000
ENV REDIS_PORT 6379
ENV APP_DIR /app

# These will be overridden by Docker Compose
ENV REDIS_HOST localhost
ENV DEBUG true
ENV MAPBOX_ACCESS_TOKEN dummy_token

RUN mkdir $APP_DIR
WORKDIR $APP_DIR

COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE $FLASK_PORT

CMD ["python", "main.py"]
