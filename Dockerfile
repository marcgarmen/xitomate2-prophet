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

# Crea el directorio de la app
WORKDIR /app

# Copia los archivos de requerimientos primero para aprovechar el cache de Docker
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la app
COPY . .

# Expone el puerto por defecto de uvicorn
EXPOSE 8080

# Comando para ejecutar la app en Cloud Run (usa el puerto 8080)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
