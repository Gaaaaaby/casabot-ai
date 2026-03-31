# app/metrics.py
# Métricas y monitoreo para la API

import time
import psutil
import os
from datetime import datetime

# Variables globales para tracking
START_TIME = time.time()
TOTAL_PREDICCIONES = 0
ULTIMA_PREDICCION = None


def get_uptime():
    """
    Calcular el tiempo de actividad de la API
    """
    uptime_seconds = time.time() - START_TIME
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    return f"{hours}h {minutes}m {seconds}s"


def get_memory_usage():
    """
    Obtener uso de memoria del proceso
    """
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        "rss_mb": round(memory_info.rss / 1024 / 1024, 2),  # Resident Set Size
        "vms_mb": round(memory_info.vms / 1024 / 1024, 2),  # Virtual Memory Size
        "porcentaje": round(process.memory_percent(), 2)
    }


def get_cpu_usage():
    """
    Obtener uso de CPU del proceso
    """
    process = psutil.Process(os.getpid())
    return round(process.cpu_percent(interval=0.1), 2)


def increment_prediccion():
    """
    Incrementar el contador de predicciones
    """
    global TOTAL_PREDICCIONES, ULTIMA_PREDICCION
    TOTAL_PREDICCIONES += 1
    ULTIMA_PREDICCION = datetime.utcnow().isoformat() + "Z"


def get_prediccion_stats():
    """
    Obtener estadísticas de predicciones
    """
    return {
        "total": TOTAL_PREDICCIONES,
        "ultima": ULTIMA_PREDICCION
    }


def get_health_details():
    """
    Obtener detalles completos de salud de la API
    """
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime": get_uptime(),
        "memoria": get_memory_usage(),
        "cpu": get_cpu_usage(),
        "predicciones": get_prediccion_stats()
    }