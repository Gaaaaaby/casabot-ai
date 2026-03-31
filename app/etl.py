# app/etl.py
# Pipeline ETL: Extraer, Transformar y Validar datos para el modelo

import pandas as pd
import numpy as np
from sklearn.datasets import fetch_california_housing
import logging

# Configurar logs para ver qué está pasando
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract():
    """
    EXTRAER: Obtener los datos crudos desde la fuente
    """
    logger.info("🔍 Extrayendo datos de California Housing...")
    
    data = fetch_california_housing()
    df = pd.DataFrame(data.data, columns=data.feature_names)
    df['target'] = data.target  # El precio es nuestro target
    
    logger.info(f"✅ Datos extraídos: {df.shape[0]} filas, {df.shape[1]} columnas")
    return df


def validate(df):
    """
    VALIDAR: Chequear que los datos estén limpios y sean válidos
    Retorna: (es_valido: bool, errores: list)
    """
    logger.info("🔎 Validando datos...")
    errores = []
    
    # 1. Verificar valores nulos
    if df.isnull().sum().sum() > 0:
        errores.append(f"❌ Hay {df.isnull().sum().sum()} valores nulos")
    
    # 2. Verificar que el target (precio) sea positivo
    if (df['target'] <= 0).any():
        errores.append("❌ Hay precios de casa <= 0 (inválidos)")
    
    # 3. Verificar rangos razonables de características
    if (df['HouseAge'] < 0).any():
        errores.append("❌ Hay edades de casa negativas")
    
    if (df['AveRooms'] <= 0).any():
        errores.append("❌ Hay casas con 0 o menos habitaciones")
    
    # 4. Verificar que tengamos suficientes datos
    if len(df) < 1000:
        errores.append(f"❌ Muy pocos datos: {len(df)} (mínimo 1000)")
    
    # 5. Verificar duplicados
    duplicados = df.duplicated().sum()
    if duplicados > 0:
        logger.warning(f"⚠️ Hay {duplicados} filas duplicadas (se eliminarán)")
    
    if errores:
        logger.error("❌ Validación FALLIDA:")
        for error in errores:
            logger.error(f"   {error}")
        return False, errores
    else:
        logger.info("✅ Validación EXITOSA: Los datos están limpios")
        return True, []


def transform(df):
    """
    TRANSFORMAR: Limpiar y preparar los datos para el modelo
    """
    logger.info("🔧 Transformando datos...")
    
    # 1. Eliminar duplicados
    df_clean = df.drop_duplicates().copy()
    
    # 2. Eliminar outliers extremos en el precio (opcional, para este ejemplo simple)
    # Quitar el 1% más caro y 1% más barato para evitar distorsiones
    q1 = df_clean['target'].quantile(0.01)
    q99 = df_clean['target'].quantile(0.99)
    df_clean = df_clean[(df_clean['target'] >= q1) & (df_clean['target'] <= q99)]
    
    # 3. (Opcional) Crear nuevas características (feature engineering)
    # Ejemplo: Habitaciones por ocupante
    df_clean['Rooms_per_Occupant'] = df_clean['AveRooms'] / df_clean['AveOccup']
    
    logger.info(f"✅ Datos transformados: {df_clean.shape[0]} filas finales")
    return df_clean


def load(df, output_path: str = "data/clean_data.csv"):
    """
    CARGAR: Guardar los datos limpios en un archivo
    """
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_csv(output_path, index=False)
    logger.info(f"💾 Datos guardados en: {output_path}")
    return output_path


def run_etl_pipeline():
    """
    Ejecutar todo el pipeline ETL en orden
    Retorna: DataFrame limpio o None si falla
    """
    logger.info("🚀 Iniciando pipeline ETL...")
    
    # 1. Extraer
    df = extract()
    
    # 2. Validar
    es_valido, errores = validate(df)
    if not es_valido:
        logger.error("🛑 Pipeline detenido: Validación fallida")
        return None
    
    # 3. Transformar
    df_clean = transform(df)
    
    # 4. Cargar (guardar)
    load(df_clean)
    
    logger.info("✅ Pipeline ETL completado exitosamente")
    return df_clean


# Para pruebas rápidas
if __name__ == "__main__":
    df_result = run_etl_pipeline()
    if df_result is not None:
        #print(f"\n📊 Resumen de datos limpios:")
        logger.info('Resumen de datos limpios')
        # Para ver el resumen en consola de forma legible
        logger.info("📊 Resumen de datos limpios:\n%s", df_result.describe().to_string())