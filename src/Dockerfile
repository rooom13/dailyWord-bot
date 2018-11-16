FROM node:11

RUN mkdir -p /usr/src/detuschlerne_bot/src
WORKDIR /usr/src/detuschlerne_bot/src

COPY package.json /usr/src/detuschlerne_bot/src
RUN npm install

COPY . /usr/src/detuschlerne_bot/src

EXPOSE 8443

CMD [ "node", "server.js"]