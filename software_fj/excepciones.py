
# ==========================================================
# SOFTWARE FJ
# EXCEPCIONES PERSONALIZADAS
# ==========================================================


class ErrorSoftwareFJ(ValueError):
    """Clase base para los errores propios del sistema."""
    pass


class DatoInvalidoError(ErrorSoftwareFJ):
    """Se utiliza cuando un dato no cumple las validaciones."""
    pass


class RegistroDuplicadoError(ErrorSoftwareFJ):
    """Se utiliza cuando se intenta registrar información duplicada."""
    pass


class RecursoNoDisponibleError(ErrorSoftwareFJ):
    """Se utiliza cuando un servicio no está disponible."""
    pass


class EstadoReservaError(ErrorSoftwareFJ):
    """Se utiliza cuando una operación no corresponde al estado de la reserva."""
    pass


class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """Se utiliza cuando se intenta realizar una operación no permitida."""
    pass


class ErrorProcesamientoReserva(ErrorSoftwareFJ):
    """Se utiliza cuando ocurre un error procesando una reserva."""
    pass
