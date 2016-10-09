FROM python:3.4
MAINTAINER Datasystems "seanbl@me.com"

# Copy requirements file in seperately to rest of project.
# This allows docker to cache requirements, and so only changes to
# requirements.txt will trigger a new pip install
ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD . /train-routes-example
WORKDIR /train-routes-example

ENV PYTHONPATH=/train-routes-example:$PYTHONPATH
