# Use an official Python runtime
FROM python:3.10-slim

# Install system dependencies (Graphviz)
RUN apt-get update && apt-get install -y graphviz && apt-get clean

# Set working directory
WORKDIR /app

# Copy dependency file
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Expose port
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
