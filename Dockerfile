FROM python:3.11.4-bookworm
RUN apt-get -y update && apt-get -y upgrade && pip install --upgrade pip
WORKDIR /home
COPY . /home/
RUN pip install /home/jra_tools
