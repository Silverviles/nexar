# ---- Build Stage ----
FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .

ARG VITE_API_BASE_URL=/api
ARG VITE_GOOGLE_CLIENT_ID
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_GOOGLE_CLIENT_ID=${VITE_GOOGLE_CLIENT_ID}

RUN npm run build

# ---- Serve Stage ----
FROM nginx:alpine

# Remove the default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy the built frontend assets
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config as a template (we run envsubst manually at startup)
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Cloud Run sets PORT automatically; default to 8080
ENV PORT=8080
# API_URL should be set to the deployed Cloud Run API service URL
ENV API_URL=http://localhost:3000

EXPOSE 8080

# At startup:
# 1. Extract the hostname from API_URL into API_HOST (e.g. https://nexar-api-xxx.run.app → nexar-api-xxx.run.app)
# 2. Run envsubst to substitute PORT, API_URL, and API_HOST into the nginx config template
# 3. Start nginx
CMD ["/bin/sh", "-c", "export API_HOST=$(echo $API_URL | sed -E 's|^https?://||' | sed -E 's|/.*$||') && envsubst '$PORT $API_URL $API_HOST' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
