import logging
import os
import socket
import time

import httpx
import psutil  # Librería para obtener uso de CPU y memoria
from fastapi import Request

# Formato en estilo JSON para mayor compatibilidad con sistemas de logs modernos
log_format = (
    "[%(asctime)s] USER: %(user)s | LEVEL: %(levelname)s | THREAD: %(threadName)s | PROCESS: %(process)d\n"
    "Elapsed Time: %(time_elapsed).5f\n"
    "CPU Usage: %(cpu_usage).3f%% | Memory: %(memory_usage).3fMB\n"
    "Location: %(filename)s:%(lineno)d in %(funcName)s()\n"
    "Endpoint: %(endpoint)s | Method: %(method)s | Status Code: %(status_code)d\n"
    "Automation: %(automation_name)s\n"
    "Message: %(message)s\n"
    "--------------------------------------------"
)


# Variable para almacenar el tiempo del último log
last_log_time = time.time()


# Filtro personalizado para agregar campos extra a cada registro
class CustomLogFilter(logging.Filter):
    def filter(self, record):
        global last_log_time

        # Tiempo transcurrido desde el último log
        current_time = time.time()
        record.time_elapsed = current_time - last_log_time
        last_log_time = current_time

        # Añadir usuario, si existe
        try:
            record.user = getattr(record, "user", "Unknown")
        except (KeyError, OSError):
            record.user = "Unknown"

        # Añadir el nombre de la automatización desde la variable de entorno
        record.automation_name = os.getenv("nombre_hu", "Unknown_automation")

        # Obtener el uso actual de CPU y memoria
        record.cpu_usage = psutil.cpu_percent(interval=None)
        record.memory_usage = psutil.virtual_memory().percent

        return True


# Formateador personalizado
class SafeTimeFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, "time_elapsed"):
            record.time_elapsed = 0.0
        if not hasattr(record, "user"):
            record.user = "Unknown"
        if not hasattr(record, "endpoint"):
            record.endpoint = "unknown_endpoint"
        if not hasattr(record, "method"):
            record.method = "UNKNOWN"
        if not hasattr(record, "status_code"):
            record.status_code = 0
        if not hasattr(record, "automation_name"):
            record.automation_name = "Unknown_automation"
        if not hasattr(record, "cpu_usage"):
            record.cpu_usage = 0.0
        if not hasattr(record, "memory_usage"):
            record.memory_usage = 0.0
        return super().format(record)


# Configuración del logger
handler = logging.StreamHandler()
formatter = SafeTimeFormatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)

logging.basicConfig(
    handlers=[handler],
    force=True,
)

logger = logging.getLogger("api_logger")
logger.setLevel(logging.DEBUG)
logger.addFilter(CustomLogFilter())

# Configurar el logger para uvicorn
uvicorn_logger = logging.getLogger("uvicorn.access")
uvicorn_logger.setLevel(logging.DEBUG)
uvicorn_logger.addHandler(handler)

# Configurar el logger para httpx si lo usas en la aplicación
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.DEBUG)
httpx_logger.addHandler(handler)

# --- MONKEY PATCHING PARA CAPTURAR SOCKET ---
_original_socket = socket.socket
_original_connect = socket.socket.connect
_original_send = socket.socket.send
_original_recv = socket.socket.recv


def log_connect(self, address):
    logger.info(f"Connecting to {address}")
    return _original_connect(self, address)


# Aplicar monkey patching al módulo socket
socket.socket.connect = log_connect

# Middleware para capturar detalles de las solicitudes y respuestas
async def log_request_data(request: Request, call_next):
    start_time = time.time()

    # Obtener los datos de la solicitud
    method = request.method
    endpoint = request.url.path

    # Procesar la solicitud y obtener la respuesta
    response = await call_next(request)
    status_code = response.status_code

    # Registrar el log al final de la solicitud
    elapsed_time = time.time() - start_time
    logger.info(
        "Solicitud procesada",
        extra={
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "time_elapsed": elapsed_time,
            "automation_name": os.getenv(
                "nombre_hu", "Unknown_automation"
            ),  # Agregar el nombre de la automatización
            "cpu_usage": psutil.cpu_percent(interval=None),  # Uso de CPU
            "memory_usage": psutil.virtual_memory().percent,  # Uso de memoria
        },
    )

    return response


# --- CAPTURAR SOLICITUDES HTTP ---
async def log_request(request: httpx.Request):
    logger.info(f"Sending request {request.method} to {request.url}")
    return request


async def log_response(response: httpx.Response):
    logger.info(
        f"Received response {response.status_code} from {response.url}",
        extra={
            "url": response.url,
            "method": response.request.method,
            "status_code": response.status_code,
            "elapsed_time": response.elapsed.total_seconds(),
            "response_body": response.text[:100],  # Limitar el cuerpo del mensaje
        },
    )
    return response