
# ==========================================================
# SOFTWARE FJ
# ADMINISTRADOR CENTRAL DEL SISTEMA
# ==========================================================

from software_fj.entidades import Cliente
from software_fj.servicios import (
    Servicio,
    ServicioSala,
    ServicioEquipo,
    ServicioAsesoria
)
from software_fj.reservas import Reserva
from software_fj.excepciones import (
    RegistroDuplicadoError,
    OperacionNoPermitidaError
)
from software_fj.registro import (
    registrar_evento,
    registrar_error
)
from datetime import datetime
from software_fj.excepciones import RecursoNoDisponibleError

class Sistema:
    """
    Administrador central de Software FJ.

    Gestiona:
    - Clientes.
    - Servicios.
    - Reservas.

    Utiliza listas internas sin bases de datos.
    """

    def __init__(self) -> None:

        self.__clientes: list[Cliente] = []
        self.__servicios: list[Servicio] = []
        self.__reservas: list[Reserva] = []

        registrar_evento(
            "Sistema Software FJ inicializado."
        )

    # ======================================================
    # CREACION DE CLIENTES CON REGISTRO DE ERRORES
    # ======================================================

    def crear_cliente(
        self,
        identificador: str,
        nombre: str,
        documento: str,
        correo: str,
        telefono: str
    ) -> Cliente:

        try:
            cliente = Cliente(
                identificador,
                nombre,
                documento,
                correo,
                telefono
            )

        except (TypeError, ValueError) as error:

            registrar_error(
                "Error durante la creación de un cliente",
                error
            )

            raise

        self.registrar_cliente(cliente)

        return cliente

    # ======================================================
    # CREACION DE SERVICIO DE SALA
    # ======================================================

    def crear_servicio_sala(
        self,
        identificador: str,
        nombre: str,
        capacidad: int,
        precio_hora: float,
        disponible: bool = True
    ) -> ServicioSala:

        try:

            servicio = ServicioSala(
                identificador,
                nombre,
                capacidad,
                precio_hora,
                disponible
            )

        except (TypeError, ValueError) as error:

            registrar_error(
                "Error durante la creación de una sala",
                error
            )

            raise

        self.registrar_servicio(servicio)

        return servicio

    # ======================================================
    # CREACION DE SERVICIO DE EQUIPOS
    # ======================================================

    def crear_servicio_equipo(
        self,
        identificador: str,
        nombre: str,
        precio_dia: float,
        existencias: int,
        disponible: bool = True
    ) -> ServicioEquipo:

        try:

            servicio = ServicioEquipo(
                identificador,
                nombre,
                precio_dia,
                existencias,
                disponible
            )

        except (TypeError, ValueError) as error:

            registrar_error(
                "Error durante la creación de un equipo",
                error
            )

            raise

        self.registrar_servicio(servicio)

        return servicio

    # ======================================================
    # CREACION DE SERVICIO DE ASESORIA
    # ======================================================

    def crear_servicio_asesoria(
        self,
        identificador: str,
        nombre: str,
        especialidad: str,
        precio_hora: float,
        disponible: bool = True
    ) -> ServicioAsesoria:

        try:

            servicio = ServicioAsesoria(
                identificador,
                nombre,
                especialidad,
                precio_hora,
                disponible
            )

        except (TypeError, ValueError) as error:

            registrar_error(
                "Error durante la creación de una asesoría",
                error
            )

            raise

        self.registrar_servicio(servicio)

        return servicio

    # ======================================================
    # ADMINISTRACION DE CLIENTES
    # ======================================================

    def registrar_cliente(self, cliente: Cliente) -> None:

        try:

            if not isinstance(cliente, Cliente):
                raise TypeError(
                    "Solo se pueden registrar objetos Cliente."
                )

            for existente in self.__clientes:

                if existente.identificador == cliente.identificador:
                    raise RegistroDuplicadoError(
                        "Ya existe un cliente con ese identificador."
                    )

                if existente.documento == cliente.documento:
                    raise RegistroDuplicadoError(
                        "Ya existe un cliente con ese documento."
                    )

            self.__clientes.append(cliente)

        except (TypeError, ValueError) as error:

            registrar_error(
                "Error al registrar un cliente",
                error
            )

            raise

        else:

            registrar_evento(
                f"Cliente registrado: {cliente.identificador}"
            )

    def buscar_cliente_por_documento(
        self,
        documento: str
    ) -> Cliente | None:

        for cliente in self.__clientes:

            if cliente.documento == documento:
                return cliente

        return None

    def buscar_cliente_por_identificador(
        self,
        identificador: str
    ) -> Cliente | None:

        for cliente in self.__clientes:

            if cliente.identificador == identificador:
                return cliente

        return None

    def listar_clientes(self) -> tuple[Cliente, ...]:

        return tuple(self.__clientes)

    def cantidad_clientes(self) -> int:

        return len(self.__clientes)

    # ======================================================
    # ADMINISTRACION DE SERVICIOS
    # ======================================================

    def registrar_servicio(self, servicio: Servicio) -> None:

        try:

            if not isinstance(servicio, Servicio):
                raise TypeError(
                    "Solo se pueden registrar objetos Servicio."
                )

            for existente in self.__servicios:

                if existente.identificador == servicio.identificador:

                    raise RegistroDuplicadoError(
                        "Ya existe un servicio con ese identificador."
                    )

            self.__servicios.append(servicio)

        except (TypeError, ValueError) as error:

            registrar_error(
                "Error al registrar un servicio",
                error
            )

            raise

        else:

            registrar_evento(
                f"Servicio registrado: {servicio.identificador} "
                f"| {servicio.nombre}"
            )

    def buscar_servicio_por_identificador(
        self,
        identificador: str
    ) -> Servicio | None:

        for servicio in self.__servicios:

            if servicio.identificador == identificador:
                return servicio

        return None

    def listar_servicios(self) -> tuple[Servicio, ...]:

        return tuple(self.__servicios)

    def cantidad_servicios(self) -> int:

        return len(self.__servicios)

    # ======================================================
    # ADMINISTRACION DE RESERVAS
    # ======================================================

    def crear_reserva(
    self,
    identificador: str,
    identificador_cliente: str,
    identificador_servicio: str,
    duracion: float,
    cantidad: int = 1,
    personas: int = 1,
    fecha_hora_inicio: datetime | None = None
) -> Reserva:
        """
        Crea una reserva utilizando únicamente clientes
        y servicios previamente registrados.
        """

        try:

            # Evitar identificadores de reserva duplicados.
            for existente in self.__reservas:

                if existente.identificador == identificador:

                    raise RegistroDuplicadoError(
                        "Ya existe una reserva con ese identificador."
                    )

            # Buscar el cliente registrado.
            cliente = self.buscar_cliente_por_identificador(
                identificador_cliente
            )

            if cliente is None:
                raise OperacionNoPermitidaError(
                    "El cliente indicado no está registrado."
                )

            # Buscar el servicio registrado.
            servicio = self.buscar_servicio_por_identificador(
                identificador_servicio
            )

            if servicio is None:
                raise OperacionNoPermitidaError(
                    "El servicio indicado no está registrado."
                )

            # Construir la reserva.
            reserva = Reserva(
                identificador,
                cliente,
                servicio,
                duracion,
                cantidad,
                personas,
                fecha_hora_inicio
            )

            # Guardar la reserva.
            self.__reservas.append(reserva)

        except (TypeError, ValueError) as error:

            registrar_error(
                f"Error al crear reserva {identificador}",
                error
            )

            raise

        else:

            registrar_evento(
                f"Reserva incorporada al sistema: {identificador}"
            )

            return reserva

    def buscar_reserva_por_identificador(
        self,
        identificador: str
    ) -> Reserva | None:

        for reserva in self.__reservas:

            if reserva.identificador == identificador:
                return reserva

        return None

    def listar_reservas(self) -> tuple[Reserva, ...]:

        return tuple(self.__reservas)

    def cantidad_reservas(self) -> int:

        return len(self.__reservas)

    # ======================================================
    # PROCESAR RESERVAS
    # ======================================================

    def procesar_reserva(
        self,
        identificador: str,
        impuesto: float = 0,
        descuento: float = 0
    ) -> None:

        reserva = self.buscar_reserva_por_identificador(
            identificador
        )

        if reserva is None:
            raise OperacionNoPermitidaError(
                "No se encontró la reserva solicitada."
            )

        reserva.procesar(impuesto, descuento)

    # ======================================================
    # CONFIRMAR RESERVAS
    # ======================================================


    def confirmar_reserva(self, identificador: str) -> None:
        """
        Confirma una reserva después de comprobar
        la disponibilidad del recurso.
        """

        reserva = self.buscar_reserva_por_identificador(
            identificador
        )

        if reserva is None:
            raise OperacionNoPermitidaError(
                "No se encontró la reserva solicitada."
            )

        # Comprobar horarios cuando se trata de una sala.
        if isinstance(reserva.servicio, ServicioSala):

            for otra in self.__reservas:

                if otra.identificador == reserva.identificador:
                    continue

                misma_sala = (
                    otra.servicio.identificador
                    == reserva.servicio.identificador
                )

                reserva_activa = otra.estado in (
                    "PROCESADA",
                    "CONFIRMADA"
                )

                if misma_sala and reserva_activa:

                    hay_cruce = (
                        reserva.fecha_hora_inicio
                        < otra.fecha_hora_fin
                        and
                        otra.fecha_hora_inicio
                        < reserva.fecha_hora_fin
                    )

                    if hay_cruce:

                        error = RecursoNoDisponibleError(
                            f"La sala '{reserva.servicio.nombre}' "
                            "ya está ocupada en ese horario."
                        )

                        registrar_error(
                            f"Conflicto de horario en {identificador}",
                            error
                        )

                        raise error

        # Si no existe conflicto, confirmar la reserva.
        reserva.confirmar()

    # ======================================================
    # CANCELAR RESERVAS
    # ======================================================

    def cancelar_reserva(self, identificador: str) -> None:

        reserva = self.buscar_reserva_por_identificador(
            identificador
        )

        if reserva is None:
            raise OperacionNoPermitidaError(
                "No se encontró la reserva solicitada."
            )

        reserva.cancelar()
