# One Dockerfile, three stages. Pick a stage with "target:" in docker compose.

# ---- dev: Vite dev server with hot reload (used by docker-compose.yml) ----
FROM node:24-alpine AS dev
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev"]

# ---- build: compile React into static files ----
FROM dev AS build
RUN npm run build

# ---- prod: tiny nginx image that serves the files and proxies /api (used for Live) ----
FROM nginx:1.29-alpine AS prod
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
