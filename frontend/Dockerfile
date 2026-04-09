# syntax=docker/dockerfile:1.7

# --- Stage 1: Dependencies ---
FROM node:20-alpine AS deps
WORKDIR /app
COPY frontend/package.json ./
RUN npm install

# --- Stage 2: Builder ---
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ ./
# VITE_API_URL is baked into the built bundle; pass via build arg
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# --- Stage 3: Development (hot reload) ---
FROM node:20-alpine AS development
WORKDIR /app
RUN apk add --no-cache wget
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# --- Stage 4: Production (static files via nginx) ---
FROM nginx:1.27-alpine AS production
RUN addgroup -g 1001 -S web && adduser -S web -u 1001 -G web
COPY --from=builder /app/dist /usr/share/nginx/html
# Run nginx as non-root on port 8080
RUN sed -i 's/listen\s*80;/listen 8080;/' /etc/nginx/conf.d/default.conf \
 && chown -R web:web /usr/share/nginx/html /var/cache/nginx /var/log/nginx /etc/nginx/conf.d \
 && touch /var/run/nginx.pid \
 && chown web:web /var/run/nginx.pid
EXPOSE 8080
USER web
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/ || exit 1
CMD ["nginx", "-g", "daemon off;"]
