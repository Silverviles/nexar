# ---- Build Stage ----
FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .

ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

# ---- Serve Stage ----
FROM nginx:alpine

# Remove the default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy the built frontend assets
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config as a template (we run envsubst manually at startup)
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Copy the runtime env config template
COPY env-config.js.template /usr/share/nginx/html/env-config.js.template

# Cloud Run sets PORT automatically; default to 8080
ENV PORT=8080
# API_URL should be set to the deployed Cloud Run API service URL
ENV API_URL=http://localhost:3000
# Runtime env vars for the frontend app (injected into env-config.js at startup)
ENV GOOGLE_CLIENT_ID=""
ENV GOOGLE_REDIRECT_URI=""

EXPOSE 8080

# At startup:
# 1. Extract the hostname from API_URL into API_HOST (e.g. https://nexar-api-xxx.run.app → nexar-api-xxx.run.app)
# 2. Run envsubst to substitute PORT, API_URL, and API_HOST into the nginx config template
# 3. Run envsubst to substitute GOOGLE_CLIENT_ID and GOOGLE_REDIRECT_URI into env-config.js
# 4. Start nginx
CMD ["/bin/sh", "-c", "export API_HOST=$(echo $API_URL | sed -E 's|^https?://||' | sed -E 's|/.*$||') && envsubst '$PORT $API_URL $API_HOST' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && envsubst '$GOOGLE_CLIENT_ID $GOOGLE_REDIRECT_URI' < /usr/share/nginx/html/env-config.js.template > /usr/share/nginx/html/env-config.js && nginx -g 'daemon off;'"]
