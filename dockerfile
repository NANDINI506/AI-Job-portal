# Use official Python slim image
FROM python:3.11-slim

# ----------------------------
# Environment variables
# ----------------------------
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# ----------------------------
# Set working directory
# ----------------------------
WORKDIR /app

# ----------------------------
# Install system dependencies
# ----------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libpq-dev \
    curl \
    git \
    wget \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------
# Copy and install Python dependencies
# ----------------------------
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------
# Download spaCy & NLTK data
# ----------------------------
RUN python -m spacy download en_core_web_sm
RUN python -m nltk.downloader punkt stopwords wordnet

# ----------------------------
# Copy project code
# ----------------------------
COPY . .

# ----------------------------
# Create folder for sentence-transformers models
# ----------------------------
RUN mkdir -p /app/models

# ----------------------------
# Expose port
# ----------------------------
EXPOSE 8000

# ----------------------------
# Run FastAPI
# ----------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]

