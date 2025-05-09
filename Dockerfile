FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install pip requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose port for container access
EXPOSE 8000

# Start the FastAPI app with live reload (optional during development)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
