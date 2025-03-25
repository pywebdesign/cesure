FROM python:3.13-slim

WORKDIR /app

RUN pip install --upgrade pip

# Copy only what's needed for pip install
COPY pyproject.toml setup.py ./
COPY cesure/__init__.py ./cesure/

# Install dependencies
RUN pip install --no-cache-dir -e .

# Install debug dependencies
RUN pip install --no-cache-dir debugpy

RUN apt update && apt -y install telnet

# Copy the rest of the application
COPY . .


CMD ["uvicorn", "cesure.main:app", "--host", "0.0.0.0", "--port", "8000"]