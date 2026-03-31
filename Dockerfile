# 1. Imagen base: Python 3.8 (el sistema operativo mínimo)
FROM python:3.8-slim

# 2. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiar el archivo de requisitos primero (para aprovechar caché de Docker)
COPY requirements.txt .

# 4. Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar todo el código del proyecto al contenedor
COPY . .

# 6. Exponer el puerto 8000 (para que la API sea accesible)
EXPOSE 8000

# 7. Comando para iniciar la API cuando el contenedor arranque
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]