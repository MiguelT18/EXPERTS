FROM node:20-alpine

RUN npm install -g pnpm

WORKDIR /app

COPY core/frontend/pnpm-lock.yaml core/frontend/package.json ./
COPY core/frontend/astro.config.mjs ./
COPY core/frontend/tsconfig.json ./

RUN pnpm install

COPY core/frontend ./

EXPOSE 3000

CMD ["pnpm", "run", "dev"]