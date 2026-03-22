# Use official Python runtime
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=UTC \
    PATH="/app:$PATH"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    git \
    ca-certificates \
    chromium-browser \
    chromium-driver \
    wkhtmltopdf \
    fontconfig \
    xfonts-75dpi \
    xfonts-96dpi \
    xfonts-base \
    xfonts-encodings \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m pip install --upgrade pip

# Install Playwright browsers
RUN python -m playwright install chromium && \
    python -m playwright install-deps

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p /app/resumes /app/logs /app/data && \
    chmod -R 755 /app

# Create non-root user for security
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Expose port for API (optional)
EXPOSE 8000

# Health check (ping the container)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import os; print('Health check passed')" || exit 1

# Start bot
CMD ["python", "run_bot.py"]
