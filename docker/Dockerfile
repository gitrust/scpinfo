FROM python:3.11.1-alpine3.17

RUN mkdir -p /src
WORKDIR /src

COPY *.py /src/
COPY leadtable.csv /src/

RUN adduser -D docker
USER docker

WORKDIR /home/docker

ENTRYPOINT ["python", "/src/scpinfo.py"]
CMD ["--help"]
