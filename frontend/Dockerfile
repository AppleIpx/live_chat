# Dockerfile для Vue.js
FROM node:16-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install
RUN npm install axios vue-router vuex


COPY . .

CMD ["npm", "run", "serve"]
