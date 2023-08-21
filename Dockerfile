FROM python:3.11.4-bookworm
RUN apt-get -y update && apt-get -y upgrade
ENV PYTHONPATH=:/workspaces/jra-tools/jra_tools/src/jra_tools
WORKDIR /home
COPY . /home/
RUN pip install /home/jra_tools
