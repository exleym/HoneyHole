FROM python:3.7

RUN apt-get update

COPY requirements.txt /

RUN pip install --no-cache-dir -r /requirements.txt

COPY data.sqlite /
COPY honeyhole /app/honeyhole
COPY honeyhole/config.py /app/config.py
COPY wsgi.py /app/
WORKDIR /app

EXPOSE 8000

CMD ["gunicorn", "-w 4", "-b 0.0.0.0:8000", "wsgi:app"]