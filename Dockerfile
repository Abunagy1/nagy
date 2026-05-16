# Install the base requirements for the nagy.
# This stage is to support development.
#FROM python:3.10-alpine3.16
FROM python:3.10-slim
COPY nagy/ /nagy
WORKDIR /nagy

ENV PYTHONUNBUFFERED 1
# COPY requirements.txt .
COPY requirements.txt /requirements.txt
RUN apk add --upgrade --no-cache build-base linux-headers && \
    pip install --upgrade pip && \
    pip install -r /requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput


CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]
#CMD ["uwsgi", "--socket", ":9000", "--workers", "4", "--master", "--enable-threads", "--module", "nagy.wsgi"]