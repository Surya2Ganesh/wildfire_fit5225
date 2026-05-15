# Start from a small Python base image to keep the container lightweight.
FROM python:3.11-slim

# All following COPY/RUN commands happen inside /app.
WORKDIR /app

# Avoid extra .pyc files and make logs appear immediately in the container output.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# OpenCV needs these shared libraries to load and process images correctly.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency list first so Docker can cache the install layer.
COPY requirements_a1.txt .

# Install CPU-only PyTorch plus the rest of the Python dependencies.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements_a1.txt

# Copy application code and the model assets used at runtime.
COPY app ./app
COPY fire-models ./fire-models
COPY demo-images ./demo-images
COPY scripts ./scripts

# Document the port uvicorn listens on inside the container.
EXPOSE 8000

# Launch the FastAPI app with uvicorn when the container starts.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
