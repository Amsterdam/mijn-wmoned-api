FROM amsterdam/python

LABEL maintainer=datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y
RUN pip install --upgrade pip
RUN pip install uwsgi

WORKDIR /app

COPY app ./app
COPY scripts ./scripts
COPY requirements.txt .
COPY uwsgi.ini .

COPY test.sh .
COPY .flake8 .

RUN pip install --no-cache-dir -r /app/requirements.txt

USER datapunt
CMD uwsgi --ini /app/uwsgi.ini
