FROM python:3.4
MAINTAINER Datasystems "seanbl@me.com"

ADD . /train-routes-example
WORKDIR /train-routes-example
RUN pip install -r requirements.txt
