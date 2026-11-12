# ==========================================================
# UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD
# ESCUELA DE CIENCIAS BÁSICAS, TECNOLOGÍA E INGENIERÍA - ECBTI
# SOFTWARE FJ - PAQUETE PRINCIPAL DEL SISTEMA
# ==========================================================

"""
Paquete principal del sistema de gestión empresarial Software FJ.

Este paquete agrupa y organiza la arquitectura completa de la aplicación,
diseñada bajo el paradigma de programación orientada a objetos (POO),
aplicando principios SOLID, encapsulación estricta, validaciones de dominio,
manejo jerárquico de excepciones y auditoría mediante bitácoras.

Estructura de módulos del paquete:
- entidades: Define la clase base abstracta `Entidad` y la clase `Cliente`.
- servicios: Define la jerarquía polimórfica de servicios (`Servicio`,
  `ServicioSala`, `ServicioEquipo`, `ServicioAsesoria`).
- reservas: Implementa la clase `Reserva`, gestionando estados y costos.
- sistema: Controlador principal que actúa como fachada del sistema.
- excepciones: Jerarquía de excepciones personalizadas del dominio.
- registro: Subsistema de bitácora y auditoría de eventos y errores.
"""

# Importación de las entidades base y clientes del dominio
from software_fj.entidades import Cliente, Entidad

# Importación de la jerarquía de excepciones personalizadas
from software_fj.excepciones import (
    DatoInvalidoError,
    ErrorProcesamientoReserva,
    ErrorSoftwareFJ,
    EstadoReservaError,
    OperacionNoPermitidaError,
    RecursoNoDisponibleError,
    RegistroDuplicadoError,
)

# Importación del modelo de reservas
from software_fj.reservas import Reserva

# Importación de la jerarquía de servicios disponibles
from software_fj.servicios import (
    Servicio,
    ServicioAsesoria,
    ServicioEquipo,
    ServicioSala,
)

# Importación del controlador central del sistema
from software_fj.sistema import Sistema

# Lista explícita de elementos públicos exportados por el paquete
__all__ = [
    # Modelos de entidades
    "Entidad",
    "Cliente",
    # Modelos de servicios
    "Servicio",
    "ServicioSala",
    "ServicioEquipo",
    "ServicioAsesoria",
    # Modelo de reservas y fachada central
    "Reserva",
    "Sistema",
    # Jerarquía de excepciones
    "ErrorSoftwareFJ",
    "DatoInvalidoError",
    "RegistroDuplicadoError",
    "RecursoNoDisponibleError",
    "EstadoReservaError",
    "OperacionNoPermitidaError",
    "ErrorProcesamientoReserva",
]
