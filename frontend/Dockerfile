FROM node:20-alpine AS base
WORKDIR /app

FROM base AS deps

COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./

RUN npm install --legacy-peer-deps

FROM base AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules

COPY . .

RUN npm run build

FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["node", "server.js"]
