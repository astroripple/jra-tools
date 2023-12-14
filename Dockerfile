FROM mcr.microsoft.com/devcontainers/python:1.1.3-3.8-bookworm
RUN apt-get -y update && pip install --upgrade pip
WORKDIR /home
COPY . /home/
RUN pip install /home/jra_tools && \
    pip install pytest pytest-mock pymysql pylint-pytest pytest-asyncio aioresponses
