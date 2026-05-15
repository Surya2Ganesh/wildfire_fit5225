# FILE: Dockerfile
# ROLE: Recipe for building the Docker image that Kubernetes runs as pods.
#       Docker reads this file top-to-bottom and creates a layered image.
#       Each instruction (FROM, RUN, COPY) creates a new layer.
#
# HOW TO BUILD: docker build -t wildfire-api:latest .
# HOW TO RUN:   docker run -p 8000:8000 wildfire-api:latest
# HOW TO CHECK: docker images   (see the image size)
#               docker ps       (see running containers)

# ── Base image ────────────────────────────────────────────────────────────────
# python:3.11-slim is a minimal Debian-based image with Python 3.11 pre-installed.
# 'slim' removes development tools, documentation, and optional extras.
# WHY NOT python:3.11 (full)? The full image is ~400MB larger — no benefit for runtime.
# WHY NOT alpine? Alpine uses musl libc which causes compatibility issues with
# PyTorch and OpenCV wheels built for glibc.
FROM python:3.11-slim

# ── Working directory ─────────────────────────────────────────────────────────
# All subsequent COPY and RUN commands execute relative to /app inside the container.
# If /app doesn't exist Docker creates it automatically.
WORKDIR /app

# ── Environment variables ──────────────────────────────────────────────────────
# Tells Python NOT to write .pyc bytecode cache files.
# .pyc files waste space in the container image and provide no benefit.
ENV PYTHONDONTWRITEBYTECODE=1

# Disables Python's output buffering so print() and log messages appear
# in 'docker logs' immediately instead of waiting for a buffer to fill.
ENV PYTHONUNBUFFERED=1

# ── System dependencies ────────────────────────────────────────────────────────
# OpenCV (cv2) requires these shared C libraries at runtime.
# libgl1       — OpenGL library used by OpenCV's display/drawing functions
# libglib2.0-0 — GLib runtime required by OpenCV internals
# Without these, 'import cv2' crashes with a missing .so file error.
# --no-install-recommends: skip optional packages → smaller image
# rm -rf /var/lib/apt/lists/*: delete the apt package index cache (saves ~30-50 MB)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ── LAYER CACHE OPTIMISATION ───────────────────────────────────────────────────
# Docker builds layers in order. If a layer hasn't changed, Docker reuses the
# cached version from a previous build (skips re-running the instruction).
# STRATEGY: copy the requirements file BEFORE the application source code.
# WHY: pip install is slow (5+ minutes). If we copy ALL files first, any change
# to main.py invalidates the pip install layer and Docker reinstalls everything.
# By copying only requirements_a1.txt first, the pip layer is only re-run when
# dependencies actually change — not when we edit application code.
COPY requirements_a1.txt .

# ── Python dependencies ────────────────────────────────────────────────────────
# Step 1: upgrade pip itself
# Step 2: install CPU-only PyTorch from the dedicated CPU wheel index
#   --index-url https://download.pytorch.org/whl/cpu installs the CPU build (~300 MB)
#   The default PyPI torch includes CUDA GPU support (~2.5 GB) — we don't need that
#   because our OCI VMs have no GPU. This saves ~2.2 GB of image size.
# Step 3: install all other dependencies from requirements_a1.txt
# --no-cache-dir: don't save pip's download cache in the image (saves space)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements_a1.txt

# ── Application files ──────────────────────────────────────────────────────────
# Copied AFTER pip install to preserve the pip layer cache (see above).
# Only copy what the API actually needs at runtime:
# FastAPI source code (main.py, predictor.py, schemas.py, utils.py)
COPY app ./app
# YOLO model weights (fire_m.pt) — loaded by predictor.py at startup
COPY fire-models ./fire-models
# Test images used by scripts/test_request.py and locust
COPY demo-images ./demo-images
# Manual test script
COPY scripts ./scripts

# ── Network ────────────────────────────────────────────────────────────────────
# Documents that uvicorn listens on port 8000 inside the container.
# This is INFORMATIONAL only — does not actually publish the port.
# Port publishing is done by:
#   docker run -p 8000:8000 ...          (local testing)
#   k8s/service.yaml targetPort: 8000    (Kubernetes)
EXPOSE 8000

# ── Startup command ────────────────────────────────────────────────────────────
# The command Kubernetes (and docker run) executes when the container starts.
# uvicorn is the ASGI server that serves the FastAPI application.
#   app.main:app  — import path: the 'app' object inside app/main.py
#   --host 0.0.0.0 — listen on all network interfaces (not just localhost)
#                    required so the container is reachable from outside
#   --port 8000   — the port uvicorn binds to inside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
