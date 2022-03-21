# syntax=docker/dockerfile:1

FROM nikolaik/python-nodejs:latest

FROM node:16
ENV NODE_ENV=production
WORKDIR /app
COPY ["package.json", "package-lock.json*", "./"]
RUN npm install --production
COPY . .
CMD [ "node", "server.js" ]


FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "main.py", "--host=0.0.0.0:8001"]