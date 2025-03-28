# Use the official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    gcc \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone the PhiData repository and checkout the specific commit
RUN git clone https://github.com/phidatahq/phidata.git && \
    cd phidata && \
    git checkout c7baaf1a0cd4546c0a124924bfcc9150f391da5f

# Navigate to the Ollama RAG directory
WORKDIR /app/phidata/cookbook/llms/ollama/rag

# Copy the requirements.txt file
COPY requirements.txt .

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV DATABASE_URL=postgresql://ai:ai@db:5432/ai

# Create application_materials directory and download the provided PDF
RUN mkdir -p /app/application_materials/knowledge_files && \
    wget -O /app/application_materials/knowledge_files/sample.pdf https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf

# Copy the modified app.py that uses the OllamaEmbedder
COPY app.py .

# Expose the port for Streamlit
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
