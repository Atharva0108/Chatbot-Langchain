# Use official Python slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy only requirements first (better layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Run Streamlit app
ENTRYPOINT ["streamlit", "run", "Home.py", \
            "--server.port=8501", \
            "--server.address=0.0.0.0", \
            "--server.enableCORS=false", \
            "--server.enableXsrfProtection=false"]
