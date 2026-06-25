FROM python:3.10-slim

WORKDIR /app

# Install system dependencies needed for FAISS and PyArrow
RUN apt-get update && apt-get install -y \
    build-essential \
    libomp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the BGE embedding model so it's cached in the Docker image
# This satisfies the "No Network" constraint during the actual ranking run
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"

# Copy the entire project
COPY . .

# Ensure data directory exists
RUN mkdir -p /app/redrob_pipeline/data/processed

# Set the default command to show usage if run without arguments
ENTRYPOINT ["python", "rank.py"]
CMD ["--help"]
