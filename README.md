# 🏠 CasaBot AI - API de Predicción de Precios

[![CI/CD Pipeline](https://github.com/TU_USUARIO/casabot-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/TU_USUARIO/casabot-ai/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8](https://img.shields.io/badge/Python-3.8-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)

API REST para predecir precios de casas usando Machine Learning.

---

## API en Producción

| Endpoint | URL |
|----------|-----|
| **Base** | https://casabot-api.onrender.com |
| **Swagger** | https://casabot-api.onrender.com/docs |
| **Health** | https://casabot-api.onrender.com/salud |

---

## Features

- ✅ Pipeline ETL automático (Extraer, Transformar, Load)
- ✅ Modelo de Regresión Lineal (R² > 0.50)
- ✅ 4 endpoints REST (FastAPI)
- ✅ Tests automatizados (pytest) - 5/5 pasando
- ✅ Logging estructurado JSON
- ✅ Health checks con métricas (uptime, memoria, CPU)
- ✅ CI/CD con GitHub Actions
- ✅ Security scanning de dependencias
- ✅ Variables de entorno (.env)

---

## Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Health check básico |
| `/salud` | GET | Health check con métricas |
| `/predecir` | POST | Predecir precio de casa |
| `/reentrenar` | POST | Reentrenar modelo |

---

## Setup Local

```bash
# 1. Clonar repo
git clone https://github.com/TU_USUARIO/casabot-ai.git
cd casabot-ai

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Ubuntu/WSL
# o
venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear .env desde ejemplo
cp .env.example .env
# Editar .env con tus valores

# 5. Entrenar modelo (primera vez)
python app/train_model.py

# 6. Ejecutar API
uvicorn app.main:app --reload