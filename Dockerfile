# Dockerfile
FROM python:3.10

WORKDIR /app

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install djangorestframework


# Copia todo el proyecto
COPY . .

# Variables de entorno adicionales si son necesarias
ENV PYTHONUNBUFFERED 1