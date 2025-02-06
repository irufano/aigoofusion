# Use Python 3.11.11 slim base image
FROM python:3.11.11-slim

# Set working directory
WORKDIR /app

# Copy the project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Default command to keep the container running
CMD ["tail", "-f", "/dev/null"]