FROM amsterdam/python:3.9.6-buster

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
