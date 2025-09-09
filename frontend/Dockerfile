FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --no-audit --no-fund
COPY . .
# Build with default API base to "/api"
ENV VITE_API_BASE_URL=/api
RUN npm run build

FROM nginx:1.27-alpine
WORKDIR /
COPY --from=builder /app/dist /usr/share/nginx/dist
# The compose will mount a custom nginx.conf at /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
