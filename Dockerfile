FROM python:3.6
WORKDIR /chax
ADD . /chax

RUN pip install /chax

EXPOSE 80

CMD ["chax", "0.0.0.0", "80"]
