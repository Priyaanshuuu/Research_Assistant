FROM node:20-alpine

WORKDIR /app

RUN apk add --no-cache curl

RUN npm install -g pnpm

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .

EXPOSE 3000

HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=10 CMD curl -f http://localhost:3000/api/healthcheck || exit 1

CMD [ "pnpm" , "dev" ]