FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire package
COPY . .

# Set environment variables
ENV PORT=8082
ENV HTTP_PORT=8083
ENV PYTHONUNBUFFERED=1

# Expose the ports for WebSocket and HTTP
EXPOSE 8082
EXPOSE 8083

# Run the server
CMD ["python", "-m", "fledge_mcp.main"] 