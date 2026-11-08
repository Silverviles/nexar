FROM python:3.12-slim

WORKDIR /app

# Install build dependencies for any packages that need to compile from source
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

EXPOSE 8002

ENTRYPOINT ["./entrypoint.sh"]
