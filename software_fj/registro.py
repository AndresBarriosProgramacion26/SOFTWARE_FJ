# ==========================================================
# UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD
# ESCUELA DE CIENCIAS BÁSICAS, TECNOLOGÍA E INGENIERÍA - ECBTI
# SOFTWARE FJ - MÓDULO DE REGISTRO DE EVENTOS Y ERRORES
# ==========================================================

"""
Módulo de auditoría y registro de eventos y errores para Software FJ.

Este módulo implementa el subsistema de bitácora (logging) de la aplicación,
proporcionando funciones centralizadas para documentar el historial de
operaciones exitosas y las excepciones ocurridas en tiempo de ejecución.

Aspectos clave de la configuración de registros:
- Uso de `pathlib.Path` para rutas absolutas e independientes de la plataforma.
- Almacenamiento persistente en archivo de texto plano (`logs/sistema.log`).
- Formato estructurado por columnas delimitadas por tuberías (|).
- Manejo explícito de codificación UTF-8 para soporte de tildes y caracteres especiales.
- Aislamiento del logger mediante espacio de nombres propio y desactivación de propagación.
- Prevención de manejadores duplicados en importaciones recursivas.
"""

import logging
from pathlib import Path


# ==========================================================
# DEFINICIÓN DE RUTAS DEL SISTEMA DE REGISTRO
# ==========================================================

# Se obtiene la ruta absoluta del directorio raíz del proyecto (SOFTWARE_FJ).
# Path(__file__).resolve() obtiene la ruta absoluta canónica de este archivo (registro.py).
# .parent corresponde a la carpeta 'software_fj'.
# .parent.parent asciende a la carpeta raíz 'SOFTWARE_FJ', garantizando que las rutas
# sean independientes del directorio de trabajo actual desde el que se ejecuta la aplicación.
RUTA_PROYECTO = Path(__file__).resolve().parent.parent

# Se define la ruta de la carpeta de bitácoras utilizando el operador / de pathlib.
RUTA_LOGS = RUTA_PROYECTO / "logs"

# Se asegura la existencia del directorio de logs en el sistema de archivos.
# El parámetro parents=True crea carpetas intermedias en caso de no existir.
# El parámetro exist_ok=True evita que se lance FileExistsError si el directorio ya existe.
RUTA_LOGS.mkdir(parents=True, exist_ok=True)

# Se define la ruta completa hacia el archivo principal de auditoría.
ARCHIVO_LOG = RUTA_LOGS / "sistema.log"


# ==========================================================
# CONFIGURACIÓN DEL LOGGER DE LA APLICACIÓN
# ==========================================================

# Se obtiene una instancia de logger con nombre específico 'software_fj' en lugar del
# logger raíz ('root'). Esto aísla los registros propios del sistema respecto a librerías externas.
logger = logging.getLogger("software_fj")

# Se define el nivel de severidad mínimo en INFO.
# Esto asegura que los eventos informativos (INFO), advertencias (WARNING),
# errores (ERROR) y fallos críticos (CRITICAL) sean capturados, descartando DEBUG.
logger.setLevel(logging.INFO)

# Se desactiva la propagación de eventos hacia el logger raíz (root logger).
# Esta decisión previene que los mensajes se dupliquen o se impriman involuntariamente
# en la consola estándar cuando otras librerías configuran manejadores globales.
logger.propagate = False


# ==========================================================
# ASIGNACIÓN DE MANEJADORES Y FORMATEO
# ==========================================================

# Se verifica que el logger no tenga manejadores asignados previamente.
# Esto evita que al importar este módulo repetidamente en diferentes puntos del
# sistema se agreguen múltiples instancias del mismo FileHandler, lo que causaría
# líneas duplicadas para un único evento en el archivo de texto.
if not logger.handlers:

    # Se crea un manejador de archivo (FileHandler) apuntando a sistema.log.
    # Se establece encoding="utf-8" para asegurar la correcta serialización de
    # caracteres especiales y tildes en cualquier sistema operativo (especialmente Windows).
    manejador = logging.FileHandler(
        ARCHIVO_LOG,
        encoding="utf-8"
    )

    # Se define la plantilla de formato visual para cada línea de registro.
    # Incluye: fecha y hora de emisión (asctime), nivel de severidad (levelname) y mensaje.
    # El parámetro datefmt normaliza el tiempo en formato estándar año-mes-día hora:minuto:segundo.
    formato = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Se enlaza el formato especificado con el manejador de archivo.
    manejador.setFormatter(formato)

    # Se asocia el manejador de archivo configurado al logger de Software FJ.
    logger.addHandler(manejador)


# ==========================================================
# FUNCIONES DE REGISTRO PÚBLICAS
# ==========================================================

def registrar_evento(mensaje: str) -> None:
    """
    Registra un evento informativo u operación exitosa en la bitácora del sistema.

    Esta función escribe una entrada con nivel de severidad INFO en el archivo
    `sistema.log`, dejando constancia cronológica de acciones clave del negocio,
    tales como creación de clientes, registro de servicios o cambios de estado
    en las reservas.

    Args:
        mensaje (str): Texto descriptivo del acontecimiento ocurrido en el sistema.

    Returns:
        None: La función no retorna ningún valor; su efecto es escribir en el archivo de log.
    """
    # Se envía el mensaje al logger configurado con nivel de severidad INFO.
    logger.info(mensaje)


def registrar_error(
    mensaje: str,
    error: BaseException | None = None
) -> None:
    """
    Registra una anomalía, fallo de validación o excepción en la bitácora del sistema.

    Esta función escribe una entrada con nivel de severidad ERROR en el archivo
    `sistema.log`. Si se proporciona un objeto de excepción, se extrae e incluye
    el nombre de su tipo y el mensaje de error. Si la excepción posee una traza
    de ejecución activa (traceback), esta se anexa al registro para facilitar
    el diagnóstico y la depuración del código.

    Args:
        mensaje (str): Descripción del contexto operacional en el que ocurrió la falla.
        error (BaseException | None, optional): Objeto de excepción capturado en el
            bloque try-except, o None si únicamente se desea registrar un mensaje de error.
            Por defecto es None.

    Returns:
        None: La función no retorna ningún valor; su efecto es escribir en el archivo de log.
    """
    # Si no se suministró ningún objeto de excepción, se registra únicamente el mensaje de texto.
    if error is None:
        logger.error(mensaje)
    else:
        # Se construye un registro detallado que combina el contexto, el tipo de error y su mensaje.
        # type(error).__name__ obtiene el nombre de la clase de la excepción (ej: DatoInvalidoError).
        # str(error) obtiene la descripción del motivo del error.
        # exc_info evalúa si la excepción tiene información de traceback para anexar la traza completa.
        logger.error(
            "%s | %s: %s",
            mensaje,
            type(error).__name__,
            error,
            exc_info=(
                (type(error), error, error.__traceback__)
                if error.__traceback__ is not None
                else False
            )
        )
