FROM amsterdam/python

LABEL maintainer=datapunt@amsterdaml.nl

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y
RUN apt-get install nano
RUN pip install --upgrade pip
RUN pip install uwsgi

COPY /api /app/api
COPY /requirements.txt /app
COPY /uwsgi.ini /app

COPY test.sh /app
COPY .flake8 /app/

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

CMD uwsgi --ini /app/uwsgi.ini
