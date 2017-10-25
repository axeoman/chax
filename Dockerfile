FROM python:3.6
WORKDIR /chax
ADD . /chax

RUN pip install /chax

EXPOSE 80

ENV REDISHOST 0.0.0.0
ENV REDISPORT 6379

CMD ["chax"]
