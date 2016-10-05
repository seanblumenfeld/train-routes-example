FROM python:3.4
MAINTAINER Datasystems "seanbl@me.com"

ADD . /pitch-example
WORKDIR /pitch-example
RUN pip install -r requirements.txt
