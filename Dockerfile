FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir websockets

COPY . .

EXPOSE 8082

CMD ["python", "smithery_mcp_server.py"] 