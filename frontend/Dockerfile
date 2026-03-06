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

# Cloud Run sets PORT automatically; default to 8080
ENV PORT=8080
# API_URL should be set to the deployed Cloud Run API service URL
ENV API_URL=http://localhost:3000

EXPOSE 8080

# Run envsubst with an explicit variable list so nginx's own $host, $uri,
# $remote_addr, $proxy_add_x_forwarded_for, $scheme etc. are left untouched.
# Then start nginx.
CMD ["/bin/sh", "-c", "envsubst '$PORT $API_URL' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
