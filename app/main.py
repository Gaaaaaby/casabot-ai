# app/main.py
# Esta es la API que recibe datos y devuelve predicciones de precios

from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import os
import logging
from dotenv import load_dotenv 
from logging_config import setup_logging
from metrics import get_health_details, increment_prediccion  # ← Agregar esto


# Cargar variables de entorno
load_dotenv()
# app/main.py - Sección de logging simplificada
import logging

# Configurar logger básico (sin dependencias externas al inicio)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurar logging estructurado (esto ya incluye basicConfig y getLogger)
logger = setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file="logs/app.log" if os.getenv("DEBUG", "False").lower() == "false" else None
)

# 1. Crear la aplicación FastAPI
app = FastAPI(
    title=os.getenv("APP_NAME", "CasaBot AI"),
    description="API para predecir precios de casas usando Machine Learning",
    version=os.getenv("APP_VERSION", "1.0.0")
)

# 2. Cargar el modelo entrenado (se carga una sola vez al iniciar)
model_path = os.getenv("MODEL_PATH", "models/house_model.joblib")
try:
    model = joblib.load(model_path)
    logger.info("✅ Modelo cargado exitosamente", extra={
        "model_path": model_path,
        "model_type": type(model).__name__
    })
except FileNotFoundError:
    logger.error("❌ Modelo no encontrado", extra={"model_path": model_path}, exc_info=True)
    raise
except Exception as e:
    logger.error("❌ Error cargando modelo", extra={"error": str(e)}, exc_info=True)
    raise

# 3. Definir el formato de datos que recibiremos (como un "formulario")
class CasaInput(BaseModel):
    MedInc: float        # Ingreso medio del área
    HouseAge: float      # Edad de la casa
    AveRooms: float      # Promedio de habitaciones
    AveBedrms: float     # Promedio de dormitorios
    Population: float    # Población del área
    AveOccup: float      # Promedio de ocupantes
    Latitude: float      # Latitud de ubicación
    Longitude: float     # Longitud de ubicación

# 4. Endpoint raíz (para saber si la API está funcionando)
@app.get("/")
def root():
    logger.info("🔍 Endpoint raíz llamado", extra={"endpoint": "/"})
    return {"mensaje": "¡CasaBot API está funcionando! 🏠"}

# 5. Endpoint de salud: verifica que la API y el modelo están funcionando
@app.get("/salud")
def salud(detalle: bool = False):
    """
    Retorna el estado de la API y del modelo
    detalle: si es True, retorna métricas completas
    """
    health = {
        "estado": "OK",
        "modelo_cargado": model is not None,
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "mensaje": "CasaBot API está saludable 🏠✅"
    }
    
    # Si se pide detalle, agregar métricas completas
    if detalle:
        health["metricas"] = get_health_details()
    
    logger.info("🔍 Endpoint salud llamado", extra={
        "endpoint": "/salud",
        "detalle": detalle
    })
    
    return health
# 6. Endpoint de predicción
@app.post("/predecir")
def predecir_precio(casa: CasaInput):
    """
    Recibe los datos de una casa y devuelve el precio predicho
    """
    logger.info("🔍 Recibida petición de predicción", extra={
        "endpoint": "/predecir",
        "MedInc": casa.MedInc,
        "HouseAge": casa.HouseAge
    })
    
    try:
        # Calcular feature engineering internamente
        rooms_per_occupant = casa.AveRooms / casa.AveOccup if casa.AveOccup > 0 else 0
        
        # Preparar datos para el modelo (9 features)
        datos = [[
            casa.MedInc,
            casa.HouseAge,
            casa.AveRooms,
            casa.AveBedrms,
            casa.Population,
            casa.AveOccup,
            casa.Latitude,
            casa.Longitude,
            rooms_per_occupant
        ]]
        
        # Hacer la predicción
        prediccion = model.predict(datos)
        precio = float(prediccion[0])  # ← Definir precio AQUÍ, como float
        
        # Loggear éxito
        logger.info("✅ Predicción completada", extra={
            "endpoint": "/predecir",
            "precio_predicho": precio
        })
        
        # Retornar respuesta
        return {
            "precio_predicho": precio,
            "mensaje": f"El precio estimado de la casa es ${precio * 100000:.2f}"
        }
        
    except Exception as e:
        # Loggear error
        logger.error("❌ Error en predicción", extra={
            "endpoint": "/predecir",
            "error": str(e)
        }, exc_info=True)
        
        # Retornar error
        return {
            "estado": "ERROR",
            "mensaje": f"Error en predicción: {str(e)}"
        }, 500
@app.post("/reentrenar")
def reentrenar_modelo():
    """
    Ejecuta el pipeline ETL y reentrenar el modelo
    Retorna: resultados del entrenamiento
    """
    import sys
    sys.path.append(os.path.dirname(__file__))
    from train_model import train
    
    logger.info("🔄 Iniciando reentrenamiento desde API...", extra={"endpoint": "/reentrenar"})
    
    try:
        model = train()
        
        if model is not None:
            logger.info("✅ Reentrenamiento completado exitosamente", extra={"endpoint": "/reentrenar"})
            return {
                "estado": "OK",
                "mensaje": "Modelo reentrenado exitosamente 🎉",
                "r2": "Ver logs para detalles",
                "nota": "Revisa la terminal para ver métricas completas"
            }
        else:
            logger.warning("⚠️ Reentrenamiento completado pero modelo no guardado (R² bajo)", extra={"endpoint": "/reentrenar"})
            return {
                "estado": "ADVERTENCIA",
                "mensaje": "Entrenamiento completado pero el modelo no se guardó (R² bajo)",
                "recomendacion": "Revisa los datos o prueba otro algoritmo"
            }
    except Exception as e:
        logger.error("❌ Error en reentrenamiento", extra={
            "endpoint": "/reentrenar",
            "error": str(e)
        }, exc_info=True)
        return {
            "estado": "ERROR",
            "mensaje": f"Falló el reentrenamiento: {str(e)}"
        }