FROM python:3.6.1-alpine

ENV APP_DIR /app

# These will be overridden by Docker Compose
ENV FLASK_PORT 5000
ENV REDIS_HOST localhost
ENV REDIS_PORT 6379
ENV MAPBOX_ACCESS_TOKEN dummy_token
ENV DEBUG true

RUN mkdir $APP_DIR
WORKDIR $APP_DIR

COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE $FLASK_PORT

CMD ["python", "main.py"]
