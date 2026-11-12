
# ==========================================================
# SOFTWARE FJ
# SISTEMA DE REGISTRO DE EVENTOS Y ERRORES
# ==========================================================

import logging
from pathlib import Path


# Obtener la ubicación principal del proyecto.
RUTA_PROYECTO = Path(__file__).resolve().parent.parent

# Crear la carpeta de registros si no existe.
RUTA_LOGS = RUTA_PROYECTO / "logs"
RUTA_LOGS.mkdir(parents=True, exist_ok=True)

# Archivo donde se almacenarán los registros.
ARCHIVO_LOG = RUTA_LOGS / "sistema.log"


# Configurar el sistema de registros.
logger = logging.getLogger("software_fj")

logger.setLevel(logging.INFO)
logger.propagate = False


# Evitar crear múltiples manejadores al importar el módulo.
if not logger.handlers:

    manejador = logging.FileHandler(
        ARCHIVO_LOG,
        encoding="utf-8"
    )

    formato = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    manejador.setFormatter(formato)

    logger.addHandler(manejador)


# ==========================================================
# REGISTRAR EVENTOS
# ==========================================================

def registrar_evento(mensaje: str) -> None:
    """Guarda un acontecimiento importante del sistema."""

    logger.info(mensaje)


# ==========================================================
# REGISTRAR ERRORES
# ==========================================================

def registrar_error(
    mensaje: str,
    error: BaseException | None = None
) -> None:
    """Guarda un error y su información correspondiente."""

    if error is None:
        logger.error(mensaje)
    else:
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
