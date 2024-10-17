FROM node:latest
WORKDIR /usr/src/app
COPY *.json ./
RUN npm install
COPY ./*.js .
COPY .env ./
CMD [ "node", "notification.js" ]