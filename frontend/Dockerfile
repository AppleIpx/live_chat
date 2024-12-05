# Dockerfile для Vue.js
FROM node:16-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install
RUN npm install axios vue-router vuex
RUN npm install npm install vue3-emoji-picker

COPY . .

CMD ["npm", "run", "serve"]
