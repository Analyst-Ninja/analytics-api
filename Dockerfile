FROM python:3.10.16-slim-bullseye

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends bash curl ca-certificates

# Install uv (UltraViolet package manager)
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Set the PATH
ENV PATH="/root/.local/bin/:$PATH"

# Set working directory
WORKDIR /app

# Copy dependencies files
COPY ./pyproject.toml ./uv.lock /app/

# Create and sync virtual environment
RUN uv venv && uv sync

# Activate virtual environment
ENV PATH="/app/.venv/bin/:$PATH"

# RUN cd /app/src

# RUN uvicorn main:app --host 0.0.0.0 --port 8000 --reload
