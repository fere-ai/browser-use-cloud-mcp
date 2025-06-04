FROM mcr.microsoft.com/devcontainers/python:3.10

# Install Poetry
RUN pip install poetry

# Configure Poetry
RUN poetry config virtualenvs.create false

# Set working directory
WORKDIR /workspaces/browser-use-cloud-mcp

# Copy project files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install

# Set environment
ENV PYTHONPATH=/workspaces/browser-use-cloud-mcp