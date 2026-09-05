FROM node:22-alpine

WORKDIR /app

COPY apps/frontend/package.json apps/frontend/package-lock.json* ./
RUN npm ci

COPY apps/frontend/ .

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
