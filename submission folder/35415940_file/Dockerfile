# Use a lightweight Python image.
# slim is smaller than the full Python image, so the final Docker image is lighter.
FROM python:3.11-slim

# Prevent Python from writing .pyc cache files inside the container.
ENV PYTHONDONTWRITEBYTECODE=1

# Make Python logs show immediately in Docker/Kubernetes logs.
ENV PYTHONUNBUFFERED=1

# Tell Ultralytics to store temporary settings in /tmp.
# This prevents permission warnings when running as a non-root user.
ENV YOLO_CONFIG_DIR=/tmp/Ultralytics

# Set the working folder inside the container.
WORKDIR /app

# Install Linux system libraries required by OpenCV and Ultralytics.
# Even though we use opencv-python-headless, Ultralytics may still pull OpenCV
# components that need these runtime libraries inside a Linux container.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgomp1 \
    libgl1 \
    libxcb1 \
    libxext6 \
    libsm6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first.
# This improves Docker layer caching:
# dependencies are not reinstalled every time only source code changes.
COPY requirements.txt .

# Install CPU-only PyTorch first.
# This avoids downloading large CUDA/GPU packages, which are not needed for this assignment.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy only the folders needed by the API.
COPY app ./app
COPY fire-models ./fire-models

# Create a non-root user for safer container execution.
# This is better practice than running the API as root.
RUN useradd --create-home appuser
USER appuser

# FastAPI will listen on port 8000 inside the container.
EXPOSE 8000

# Start the FastAPI application using Uvicorn.
# 0.0.0.0 is required so Docker/Kubernetes can access the service.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]