FROM python:3.10-slim

WORKDIR /app

# Install cron and curl
RUN apt-get update \
 && apt-get install -y --no-install-recommends cron curl \
 && rm -rf /var/lib/apt/lists/*

# Install scraper dependencies only
RUN pip install requests beautifulsoup4 python-dateutil minio

# Copy cron file
COPY scraper/crontab /etc/cron.d/scraper-cron

RUN chmod 0644 /etc/cron.d/scraper-cron

# Create log file
RUN touch /var/log/cron.log




