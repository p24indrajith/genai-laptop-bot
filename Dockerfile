FROM node:20-alpine
WORKDIR /usr/src/app
RUN npm install -g flowise
EXPOSE 3000
CMD [ "npx", "flowise", "start" ]