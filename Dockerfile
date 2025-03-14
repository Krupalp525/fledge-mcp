FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire package
COPY . .

# Set environment variables
ENV PORT=8082
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 8082

# Run the server
CMD ["python", "-m", "fledge_mcp.main"] 