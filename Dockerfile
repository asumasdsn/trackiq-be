# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (postgres client, build-essential for some pip packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install Python dependencies using uv
COPY pyproject.toml .
RUN uv pip install --system .

# Copy the current directory contents into the container at /app
COPY . .

# Railway dynamically assigns PORT — default to 8000 locally
ENV PORT=8000
EXPOSE $PORT

# Command to run the application using a robust Python entry point
CMD ["python", "run.py"]
