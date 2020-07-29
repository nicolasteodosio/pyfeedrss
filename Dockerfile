FROM python:3.7-alpine

RUN apk upgrade && \
  apk add --no-cache --virtual build-dependencies python3-dev linux-headers postgresql-dev make gcc \
  g++ ca-certificates zlib-dev jpeg-dev tiff-dev freetype-dev lcms2-dev musl-dev \
  libwebp-dev tcl-dev tk-dev libxml2-dev libxslt-dev git netcat-openbsd && \
  rm -rf /var/cache/apk/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /opt/code
WORKDIR /opt/code
RUN pip install -r requirements/dev.txt
