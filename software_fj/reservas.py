
# ==========================================================
# SOFTWARE FJ
# MODULO DE GESTION DE RESERVAS
# ==========================================================

from datetime import datetime, timedelta

from software_fj.entidades import Entidad, Cliente

from software_fj.servicios import (
    Servicio,
    ServicioSala,
    ServicioEquipo
)

from software_fj.excepciones import (
    EstadoReservaError,
    ErrorProcesamientoReserva
)

from software_fj.registro import (
    registrar_evento,
    registrar_error
)


# ==========================================================
# CLASE RESERVA
# ==========================================================

class Reserva(Entidad):
    """
    Representa una reserva de Software FJ.

    Integra cliente, servicio, duración, fecha,
    cantidad, estado y costo total.
    """

    def __init__(
        self,
        identificador: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: float,
        cantidad: int = 1,
        personas: int = 1,
        fecha_hora_inicio: datetime | None = None
    ) -> None:

        super().__init__(identificador)

        if not isinstance(cliente, Cliente):
            raise TypeError("El cliente no es válido.")

        if not isinstance(servicio, Servicio):
            raise TypeError("El servicio no es válido.")

        if isinstance(duracion, bool) or not isinstance(
            duracion, (int, float)
        ):
            raise TypeError("La duración debe ser un número.")

        if duracion <= 0:
            raise ValueError("La duración debe ser mayor que cero.")

        if isinstance(cantidad, bool) or not isinstance(cantidad, int):
            raise TypeError("La cantidad debe ser un entero.")

        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")

        if isinstance(personas, bool) or not isinstance(personas, int):
            raise TypeError("El número de personas debe ser un entero.")

        if personas <= 0:
            raise ValueError(
                "El número de personas debe ser mayor que cero."
            )

        # Si no se proporciona fecha, se utiliza la fecha actual.
        if fecha_hora_inicio is None:
            fecha_hora_inicio = datetime.now()

        if not isinstance(fecha_hora_inicio, datetime):
            raise TypeError(
                "La fecha de inicio debe ser un objeto datetime."
            )

        # Para evitar comparaciones incompatibles,
        # utilizaremos fechas locales sin zona horaria.
        if fecha_hora_inicio.tzinfo is not None:
            raise ValueError(
                "Utilice una fecha y hora sin zona horaria."
            )

        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion = float(duracion)
        self.__cantidad = cantidad
        self.__personas = personas
        self.__fecha_hora_inicio = fecha_hora_inicio

        self.__estado = "PENDIENTE"
        self.__costo_total = None

        # Indica si el inventario ya fue descontado.
        self.__recurso_reservado = False

        registrar_evento(
            f"Reserva creada: {self.identificador} "
            f"| Cliente: {cliente.identificador} "
            f"| Servicio: {servicio.identificador}"
        )

    # ======================================================
    # PROPIEDADES
    # ======================================================

    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        return self.__servicio

    @property
    def duracion(self) -> float:
        return self.__duracion

    @property
    def cantidad(self) -> int:
        return self.__cantidad

    @property
    def personas(self) -> int:
        return self.__personas

    @property
    def estado(self) -> str:
        return self.__estado

    @property
    def costo_total(self) -> float | None:
        return self.__costo_total

    @property
    def fecha_hora_inicio(self) -> datetime:
        return self.__fecha_hora_inicio

    @property
    def fecha_hora_fin(self) -> datetime:
        """
        Calcula la finalización de acuerdo con el tipo de servicio.

        Equipos: duración expresada en días.
        Salas y asesorías: duración expresada en horas.
        """

        if isinstance(self.__servicio, ServicioEquipo):

            return self.__fecha_hora_inicio + timedelta(
                days=self.__duracion
            )

        return self.__fecha_hora_inicio + timedelta(
            hours=self.__duracion
        )

    # ======================================================
    # CALCULAR COSTO
    # ======================================================

    def _calcular_costo(
        self,
        impuesto: float = 0,
        descuento: float = 0
    ) -> float:

        if isinstance(self.__servicio, ServicioSala):

            return self.__servicio.calcular_costo(
                self.__duracion,
                impuesto=impuesto,
                descuento=descuento,
                personas=self.__personas
            )

        elif isinstance(self.__servicio, ServicioEquipo):

            return self.__servicio.calcular_costo(
                self.__duracion,
                impuesto=impuesto,
                descuento=descuento,
                cantidad=self.__cantidad
            )

        return self.__servicio.calcular_costo(
            self.__duracion,
            impuesto=impuesto,
            descuento=descuento
        )

    # ======================================================
    # PROCESAR RESERVA
    # ======================================================

    def procesar(
        self,
        impuesto: float = 0,
        descuento: float = 0
    ) -> None:

        try:

            if self.__estado != "PENDIENTE":
                raise EstadoReservaError(
                    "Solo se pueden procesar reservas pendientes."
                )

            total = self._calcular_costo(
                impuesto,
                descuento
            )

        except (TypeError, ValueError) as error:

            registrar_error(
                f"Error procesando reserva {self.identificador}",
                error
            )

            raise ErrorProcesamientoReserva(
                f"No fue posible procesar la reserva "
                f"{self.identificador}."
            ) from error

        else:

            self.__costo_total = total
            self.__estado = "PROCESADA"

            registrar_evento(
                f"Reserva procesada: {self.identificador} "
                f"| Costo: {total}"
            )

        finally:

            registrar_evento(
                f"Finalizó intento de procesamiento: "
                f"{self.identificador}"
            )

    # ======================================================
    # CONFIRMAR RESERVA
    # ======================================================


    def confirmar(self) -> None:

        if self.__estado != "PROCESADA":

            error = EstadoReservaError(
                "La reserva debe estar procesada antes de confirmarse."
            )

            registrar_error(
                f"Error al confirmar reserva {self.identificador}",
                error
            )

            raise error

        if isinstance(self.__servicio, ServicioEquipo):

            try:

                self.__servicio.reservar_existencias(
                    self.__cantidad
                )

            except (TypeError, ValueError) as error:

                registrar_error(
                    f"Error al descontar inventario "
                    f"en reserva {self.identificador}",
                    error
                )

                raise

            self.__recurso_reservado = True

        self.__estado = "CONFIRMADA"

        registrar_evento(
            f"Reserva confirmada: {self.identificador}"
        )

    # ======================================================
    # CANCELAR RESERVA
    # ======================================================


    def cancelar(self) -> None:

        if self.__estado == "CANCELADA":

            error = EstadoReservaError(
                "La reserva ya se encuentra cancelada."
            )

            registrar_error(
                f"Error al cancelar reserva {self.identificador}",
                error
            )

            raise error

        if self.__recurso_reservado:

            try:

                self.__servicio.liberar_existencias(
                    self.__cantidad
                )

            except (TypeError, ValueError) as error:

                registrar_error(
                    f"Error al devolver inventario "
                    f"de reserva {self.identificador}",
                    error
                )

                raise

            self.__recurso_reservado = False

            registrar_evento(
                f"Equipos devueltos al inventario: "
                f"{self.__cantidad}"
            )

        self.__estado = "CANCELADA"

        registrar_evento(
            f"Reserva cancelada: {self.identificador}"
        )

    # ======================================================
    # INFORMACION DE LA RESERVA
    # ======================================================

    def obtener_informacion(self) -> str:

        costo = (
            "Pendiente de cálculo"
            if self.__costo_total is None
            else f"${self.__costo_total:,.2f}"
        )

        return (
            f"RESERVA | "
            f"ID: {self.identificador} | "
            f"Cliente: {self.__cliente.nombre} | "
            f"Servicio: {self.__servicio.nombre} | "
            f"Inicio: {self.fecha_hora_inicio:%Y-%m-%d %H:%M} | "
            f"Fin: {self.fecha_hora_fin:%Y-%m-%d %H:%M} | "
            f"Duración: {self.__duracion} | "
            f"Estado: {self.__estado} | "
            f"Costo: {costo}"
        )
