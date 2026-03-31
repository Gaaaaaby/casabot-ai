

# app/train_model.py
# Entrenamiento del modelo usando el pipeline ETL

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
import sys
import logging

# Configurar logger para este módulo
logger = logging.getLogger(__name__)

# Agregar la carpeta app al path para poder importar etl
sys.path.append(os.path.dirname(__file__))
from etl import run_etl_pipeline

# Umbral mínimo de calidad del modelo
MIN_R2_THRESHOLD = 0.50

def train():
    logger.info("🚀 Iniciando entrenamiento con ETL...")
    
    # 1. Ejecutar pipeline ETL para obtener datos limpios
    logger.info("🔍 Ejecutando pipeline ETL...")
    df_clean = run_etl_pipeline()
    
    if df_clean is None:
        logger.error("❌ Error: El pipeline ETL falló, no se puede entrenar")
        return None
    
    logger.info("✅ Datos limpios listos", extra={
        "filas": len(df_clean),
        "columnas": len(df_clean.columns)
    })
    
    # 2. Separar características (X) y target (y)
    # Excluimos la columna 'target' de las características
    feature_cols = [col for col in df_clean.columns if col != 'target']
    X = df_clean[feature_cols]
    y = df_clean['target']
    
    logger.info("📊 Características seleccionadas", extra={
        "features": feature_cols,
        "total_features": len(feature_cols)
    })
    
    # 3. Dividir en entrenamiento y prueba (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    logger.info("📚 Datos divididos", extra={
        "train_size": len(X_train),
        "test_size": len(X_test),
        "split_ratio": "80/20"
    })
    
    # 4. Crear y entrenar el modelo
    model = LinearRegression()
    model.fit(X_train, y_train)
    logger.info("🧠 Modelo entrenado", extra={
        "model_type": "LinearRegression",
        "coefficients_count": len(model.coef_)
    })
    
    # 5. Evaluar el modelo
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    logger.info("📊 Métricas de evaluación", extra={
        "mse": float(mse),
        "rmse": float(mse ** 0.5),
        "r2": float(r2),
        "split": "test"
    })
    
    # 6. Validar calidad del modelo antes de guardar
    if r2 < MIN_R2_THRESHOLD:
        logger.warning("⚠️ R² por debajo del umbral", extra={
            "r2_actual": float(r2),
            "r2_threshold": MIN_R2_THRESHOLD,
            "accion": "modelo_no_guardado"
        })
        logger.info("💡 Recomendación: Revisar datos o probar otro algoritmo")
        # No guardamos modelos con R² bajo
        return model
    
    # 7. Guardar el modelo si pasa la validación
    model_path = os.path.join(os.path.dirname(__file__), "..", "models", "house_model.joblib")
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    
    logger.info("💾 Modelo guardado exitosamente", extra={
        "model_path": model_path,
        "r2": float(r2),
        "mse": float(mse)
    })
    
    logger.info("✅ ¡Entrenamiento completado exitosamente!", extra={
        "r2_final": float(r2),
        "modelo_guardado": True
    })
    
    return model

if __name__ == "__main__":
    # Configurar logging básico si se ejecuta como script directo
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    train()