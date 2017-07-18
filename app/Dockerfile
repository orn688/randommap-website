FROM python:3.6.1-alpine

ENV BOTTLE_PORT 8080
ENV REDIS_HOST localhost
ENV REDIS_PORT 6379
ENV APP_DIR /app

RUN mkdir $APP_DIR
WORKDIR $APP_DIR

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE $BOTTLE_PORT

CMD ["python", "app.py"]
