FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

# Install postgres client
RUN apk add --update --no-cache postgresql-client

# Install individual dependencies
# so that we could avoid installing extra packages to the container
RUN apk add --update --no-cache --virtual .tmp-build-deps \
	gcc libc-dev linux-headers postgresql-dev libffi-dev
RUN pip install -r /requirements.txt
    
# Remove dependencies   
RUN apk del .tmp-build-deps

RUN mkdir /django_backend
WORKDIR /django_backend
COPY ./django_backend /django_backend

# [Security] Limit the scope of user who run the docker image
RUN adduser -D chris

USER chris