# app/logging_config.py
# Configuración de logging estructurado para producción

# app/logging_config.py
# Configuración de logging estructurada (SIN dependencias circulares)

import logging
import sys
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Formatter personalizado para logs JSON"""
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['timestamp'] = record.created
        log_record['level'] = record.levelname
        log_record['logger'] = record.name


def setup_logging(log_level: str = "INFO", log_file: str = None):
    """
    Configurar logging estructurado
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Usar logger raíz sin crear dependencias
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Limpiar handlers existentes
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    
    # Formatter JSON
    json_formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Handler opcional para archivo
    if log_file:
        import os
        os.makedirs(os.path.dirname(log_file) or '.', exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(json_formatter)
        file_handler.setLevel(level)
        root_logger.addHandler(file_handler)
    
    return logging.getLogger(__name__)