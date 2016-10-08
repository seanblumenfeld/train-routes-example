FROM python:3.4
MAINTAINER Datasystems "seanbl@me.com"

ADD . /thoughtworks-example
WORKDIR /thoughtworks-example
RUN pip install -r requirements.txt
