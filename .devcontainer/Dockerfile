FROM mcr.microsoft.com/devcontainers/python:1.1.9-3.8-bookworm
ENV DB=mariadb+pymysql://user:pass@host_name/database_name
WORKDIR /home
COPY . /home/
RUN apt-get -y update && pip install --upgrade pip
