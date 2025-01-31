FROM python:alpine

COPY rootfs /

RUN python -m pip install click requests