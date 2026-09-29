FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies with extended timeout and retry tolerance
COPY requirements-prod.txt .
RUN pip install --no-cache-dir --default-timeout=120 --retries 5 -r requirements-prod.txt

# Copy application source
COPY app/ ./app
COPY AGENTS.md README.md ./

# Expose port
EXPOSE 8000

# Run uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
