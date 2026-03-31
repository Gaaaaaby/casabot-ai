# tests/test_api.py
# Tests automatizados para la API de CasaBot

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Agregar la carpeta app al path para importar main
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app"))

from app.main import app

# Crear un cliente de prueba para FastAPI
client = TestClient(app)


def test_root_endpoint():
    """
    Prueba el endpoint raíz GET /
    """
    response = client.get("/")
    
    # Verificar que la respuesta es exitosa (200 OK)
    assert response.status_code == 200
    
    # Verificar que el JSON tiene la clave "mensaje"
    data = response.json()
    assert "mensaje" in data
    assert "API" in data["mensaje"]
    
    print("✅ test_root_endpoint: PASSED")


def test_salud_endpoint():
    """
    Prueba el endpoint de salud GET /salud
    """
    response = client.get("/salud")
    
    # Verificar estado 200
    assert response.status_code == 200
    
    # Verificar estructura de la respuesta
    data = response.json()
    assert data["estado"] == "OK"
    assert data["modelo_cargado"] is True
    assert "version" in data
    
    print("✅ test_salud_endpoint: PASSED")

def test_predecir_endpoint_success():
    """
    Prueba el endpoint de predicción con datos válidos
    """
    casa_datos = {
        "MedInc": 8.5,
        "HouseAge": 25,
        "AveRooms": 6,
        "AveBedrms": 1.5,
        "Population": 1200,
        "AveOccup": 3,
        "Latitude": 34.05,
        "Longitude": -118.25
        # Rooms_per_Occupant se calcula automáticamente en la API
    }
    
    response = client.post("/predecir", json=casa_datos)
    assert response.status_code == 200
    data = response.json()
    assert "precio_predicho" in data
    assert isinstance(data["precio_predicho"], (int, float))
    assert data["precio_predicho"] > 0
    print(f"✅ test_predecir_endpoint_success: PASSED (precio: {data['precio_predicho']})")
    
def test_predecir_endpoint_invalid_data():
    """
    Prueba que el endpoint rechaza datos inválidos
    """
    # Datos incompletos (falta Latitude y Longitude)
    casa_datos_incompletos = {
        "MedInc": 8.5,
        "HouseAge": 25,
        # Faltan campos requeridos
    }
    
    response = client.post("/predecir", json=casa_datos_incompletos)
    
    # FastAPI debería rechazar con 422 (Unprocessable Entity)
    assert response.status_code == 422
    
    print("✅ test_predecir_endpoint_invalid_data: PASSED (validación funciona)")


def test_reentrenar_endpoint():
    """
    Prueba el endpoint de reentrenamiento
    Nota: Este test puede tardar unos segundos porque entrena el modelo
    """
    response = client.post("/reentrenar")
    
    # Verificar que la respuesta es exitosa
    assert response.status_code == 200
    
    # Verificar estructura de la respuesta
    data = response.json()
    assert "estado" in data
    assert data["estado"] in ["OK", "ADVERTENCIA", "ERROR"]
    
    print(f"✅ test_reentrenar_endpoint: PASSED (estado: {data['estado']})")


# Para ejecutar tests individualmente desde la terminal:
# pytest tests/test_api.py::test_root_endpoint -v