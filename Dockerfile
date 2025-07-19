FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src/ src/

# Install cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Copy the crontab file
COPY crontab /etc/cron.d/app-cron

# Give execution rights on the cron job file and apply it
RUN chmod 0644 /etc/cron.d/app-cron && crontab /etc/cron.d/app-cron

# Create a log file for cron output
RUN touch /var/log/cron.log

# Run cron in the background and tail the log to stdout
CMD ["sh", "-c", "printenv > /etc/environment && cron && tail -f /var/log/cron.log"]
