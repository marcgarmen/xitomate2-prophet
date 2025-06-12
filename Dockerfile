# Usa una imagen oficial de Python
FROM python:3.11-slim

# Evita prompts de interacción
ENV DEBIAN_FRONTEND=noninteractive

# Instala dependencias del sistema necesarias para Prophet y otros paquetes
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        libatlas-base-dev \
        libgomp1 \
        git \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "run.py"]
