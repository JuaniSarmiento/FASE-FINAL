FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Environment setup
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Command to run the app
CMD ["uvicorn", "src.infrastructure.http.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
