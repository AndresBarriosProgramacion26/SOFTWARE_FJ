# ==========================================================
# SOFTWARE FJ
# MODULO DE GESTION DE RESERVAS
# ==========================================================

"""
Módulo de Gestión de Reservas - Software FJ.

Este módulo implementa la lógica central para la creación, procesamiento,
confirmación y cancelación de reservas de servicios en Software FJ.

Conceptos clave implementados:
1. Máquina de Estados:
   La reserva sigue un ciclo de vida formal y determinista a través de estados:
   - PENDIENTE: Estado inicial al crearse la reserva. El costo aún no se ha calculado
     y el inventario no se ha reservado.
   - PROCESADA: Transición desde PENDIENTE mediante el método `procesar()`. Se calcula
     el costo final (impuestos y descuentos) y se validan las reglas del servicio.
   - CONFIRMADA: Transición desde PROCESADA mediante el método `confirmar()`. Se reserva
     el inventario físico en servicios de equipos. No se puede confirmar una reserva
     en estado PENDIENTE ni CANCELADA.
   - CANCELADA: Transición desde cualquier estado activo (PENDIENTE, PROCESADA o CONFIRMADA)
     mediante el método `cancelar()`. Si existía inventario comprometido, este es
     restituido automáticamente al stock del servicio. Una reserva cancelada es un
     estado terminal que no puede volver a reactivarse.

2. Cálculo Temporal Diferenciado:
   La propiedad `fecha_hora_fin` determina el término temporal de la reserva:
   - ServicioEquipo: La duración se mide en DÍAS, sumando `timedelta(days=duracion)`.
   - ServicioSala y ServicioAsesoria: La duración se mide en HORAS, sumando `timedelta(hours=duracion)`.
   Esta distinción temporal es esencial para el control de solapamiento de horarios y
   la gestión de disponibilidades.

3. Manejo Robusto de Excepciones:
   - Patrón `try / except / else / finally` en `procesar()` para aislar errores de cálculo,
     aplicar transiciones atómicas solo cuando la operación es exitosa (bloque `else`),
     y registrar eventos de auditoría obligatorios (bloque `finally`).
   - Encadenamiento de excepciones (`raise ... from error`) según PEP 3134 para
     preservar la causa raíz del error manteniendo la abstracción en la capa de negocio.
"""

from datetime import datetime, timedelta

from software_fj.entidades import Cliente, Entidad
from software_fj.excepciones import (
    ErrorProcesamientoReserva,
    EstadoReservaError,
)
from software_fj.registro import (
    registrar_error,
    registrar_evento,
)
from software_fj.servicios import (
    Servicio,
    ServicioEquipo,
    ServicioSala,
)


# ==========================================================
# CLASE RESERVA
# ==========================================================

class Reserva(Entidad):
    """
    Representa una reserva de servicio en Software FJ.

    Coordina la interacción entre el cliente solicitante y el servicio contratado,
    administrando los parámetros de tiempo, aforo, cantidad de equipos, máquina
    de estados del ciclo de vida y costo económico total.
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
        """
        Inicializa una nueva reserva en estado PENDIENTE.

        Args:
            identificador (str): Código alfanumérico único de la reserva.
            cliente (Cliente): Instancia válida del cliente que solicita la reserva.
            servicio (Servicio): Instancia válida del servicio a reservar.
            duracion (float): Magnitud temporal de uso (horas para salas/asesorías, días para equipos).
            cantidad (int, optional): Unidades de equipos solicitadas. Por defecto 1.
            personas (int, optional): Asistentes previstos para salas. Por defecto 1.
            fecha_hora_inicio (datetime | None, optional): Fecha y hora de inicio de la reserva.
                Si es None, se toma la fecha y hora actual del sistema. Por defecto None.

        Raises:
            TypeError: Si el cliente, servicio, duración, cantidad, personas o fecha no cumplen
                con los tipos requeridos.
            ValueError: Si la duración, cantidad o personas son <= 0, o si la fecha incluye zona horaria.
        """
        # Invocar al constructor de la clase base Entidad para validar el identificador único
        super().__init__(identificador)

        # Validar que el cliente sea una instancia legítima de la clase Cliente
        if not isinstance(cliente, Cliente):
            raise TypeError("El cliente no es válido.")

        # Validar que el servicio sea una instancia legítima de la clase abstracta Servicio
        if not isinstance(servicio, Servicio):
            raise TypeError("El servicio no es válido.")

        # Comprobar que la duración no sea booleana y corresponda a un tipo numérico (int o float)
        if isinstance(duracion, bool) or not isinstance(
            duracion, (int, float)
        ):
            raise TypeError("La duración debe ser un número.")

        # Regla de negocio: la duración del servicio debe ser estrictamente mayor que cero
        if duracion <= 0:
            raise ValueError("La duración debe ser mayor que cero.")

        # Comprobar que la cantidad de unidades solicitadas sea un entero y no un booleano
        if isinstance(cantidad, bool) or not isinstance(cantidad, int):
            raise TypeError("La cantidad debe ser un entero.")

        # Regla de negocio: la cantidad de recursos solicitados debe ser mayor a cero
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")

        # Comprobar que el número de personas asistentes sea un entero y no un booleano
        if isinstance(personas, bool) or not isinstance(personas, int):
            raise TypeError("El número de personas debe ser un entero.")

        # Regla de negocio: el número de asistentes debe ser mayor a cero
        if personas <= 0:
            raise ValueError(
                "El número de personas debe ser mayor que cero."
            )

        # Si el usuario no especificó fecha de inicio, asignar la fecha y hora actual del sistema
        if fecha_hora_inicio is None:
            fecha_hora_inicio = datetime.now()

        # Comprobar que la fecha de inicio sea efectivamente un objeto de tipo datetime
        if not isinstance(fecha_hora_inicio, datetime):
            raise TypeError(
                "La fecha de inicio debe ser un objeto datetime."
            )

        # Para garantizar comparaciones homogéneas sin desfases, se exigen fechas sin zona horaria (naive)
        if fecha_hora_inicio.tzinfo is not None:
            raise ValueError(
                "Utilice una fecha y hora sin zona horaria."
            )

        # Asignar los atributos privados de la reserva
        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion = float(duracion)
        self.__cantidad = cantidad
        self.__personas = personas
        self.__fecha_hora_inicio = fecha_hora_inicio

        # Lógica de máquina de estados: la reserva nace siempre en estado inicial "PENDIENTE"
        self.__estado = "PENDIENTE"

        # El costo total permanece en None hasta que la reserva sea procesada explícitamente
        self.__costo_total = None

        # Bandera de control para rastrear si el inventario físico ya fue descontado en bodega
        self.__recurso_reservado = False

        # Registrar en el log de auditoría la creación exitosa de la reserva
        registrar_evento(
            f"Reserva creada: {self.identificador} "
            f"| Cliente: {cliente.identificador} "
            f"| Servicio: {servicio.identificador}"
        )

    # ======================================================
    # PROPIEDADES (GETTERS)
    # ======================================================

    @property
    def cliente(self) -> Cliente:
        """
        Obtiene la instancia del cliente titular de la reserva.

        Returns:
            Cliente: Objeto del cliente asociado.
        """
        # Retorna la referencia privada al cliente
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        """
        Obtiene la instancia del servicio contratado.

        Returns:
            Servicio: Objeto del servicio asociado.
        """
        # Retorna la referencia privada al servicio
        return self.__servicio

    @property
    def duracion(self) -> float:
        """
        Obtiene la duración de la reserva (horas o días según el servicio).

        Returns:
            float: Duración temporal del servicio.
        """
        # Retorna la duración numérica privada
        return self.__duracion

    @property
    def cantidad(self) -> int:
        """
        Obtiene la cantidad de unidades o equipos reservados.

        Returns:
            int: Número de unidades solicitadas.
        """
        # Retorna la cantidad privada de recursos
        return self.__cantidad

    @property
    def personas(self) -> int:
        """
        Obtiene el número de asistentes previstos para la reserva.

        Returns:
            int: Cantidad de personas registradas.
        """
        # Retorna el número privado de asistentes
        return self.__personas

    @property
    def estado(self) -> str:
        """
        Obtiene el estado actual en la máquina de estados de la reserva.

        Returns:
            str: Estado actual ('PENDIENTE', 'PROCESADA', 'CONFIRMADA' o 'CANCELADA').
        """
        # Retorna el estado actual de la reserva
        return self.__estado

    @property
    def costo_total(self) -> float | None:
        """
        Obtiene el costo total calculado de la reserva.

        Returns:
            float | None: Valor monetario calculado, o None si aún no se procesa.
        """
        # Retorna el costo monetario total o None si está pendiente de cálculo
        return self.__costo_total

    @property
    def fecha_hora_inicio(self) -> datetime:
        """
        Obtiene la fecha y hora programada para el inicio de la reserva.

        Returns:
            datetime: Momento exacto de inicio.
        """
        # Retorna la fecha y hora de inicio de la reserva
        return self.__fecha_hora_inicio

    @property
    def fecha_hora_fin(self) -> datetime:
        """
        Calcula dinámicamente la fecha y hora de finalización según el tipo de servicio.

        Lógica de cálculo temporal diferenciado:
        - ServicioEquipo: La unidad de duración representa DÍAS, por lo que se incrementa
          la fecha de inicio utilizando `timedelta(days=self.__duracion)`.
        - ServicioSala y ServicioAsesoria: La unidad de duración representa HORAS, por
          lo que se incrementa la fecha de inicio usando `timedelta(hours=self.__duracion)`.

        Returns:
            datetime: Momento de finalización calculado para la reserva.
        """
        # Evaluación polimórfica del servicio: si es alquiler de equipos, la tarifa y duración son diarias
        if isinstance(self.__servicio, ServicioEquipo):
            # Sumar la duración como días mediante timedelta
            return self.__fecha_hora_inicio + timedelta(
                days=self.__duracion
            )

        # Para salas de reuniones y asesorías profesionales, la duración se cuantifica en horas
        return self.__fecha_hora_inicio + timedelta(
            hours=self.__duracion
        )

    # ======================================================
    # CALCULAR COSTO (DELEGACION POLIMORFICA)
    # ======================================================

    def _calcular_costo(
        self,
        impuesto: float = 0,
        descuento: float = 0
    ) -> float:
        """
        Delega el cálculo del costo económico al servicio concreto correspondiente.

        Aplica polimorfismo suministrando los argumentos especializados según el tipo
        de servicio (aforo de personas para salas, cantidad de unidades para equipos).

        Args:
            impuesto (float, optional): Porcentaje tributario a sumar. Por defecto 0.
            descuento (float, optional): Porcentaje comercial a restar. Por defecto 0.

        Returns:
            float: Costo monetario calculado por el servicio.

        Raises:
            RecursoNoDisponibleError: Si el servicio no está operativo o no hay inventario.
            TypeError: Si algún parámetro no cumple el tipo esperado.
            DatoInvalidoError: Si algún parámetro viola reglas de negocio.
        """
        # Si el servicio corresponde a una sala, enviar el parámetro de personas para validar aforo
        if isinstance(self.__servicio, ServicioSala):

            return self.__servicio.calcular_costo(
                self.__duracion,
                impuesto=impuesto,
                descuento=descuento,
                personas=self.__personas
            )

        # Si el servicio corresponde a alquiler de equipos, enviar la cantidad de unidades para inventario
        elif isinstance(self.__servicio, ServicioEquipo):

            return self.__servicio.calcular_costo(
                self.__duracion,
                impuesto=impuesto,
                descuento=descuento,
                cantidad=self.__cantidad
            )

        # Para otros servicios (ej. asesorías especializadas), invocar el cálculo estándar sin parámetros extra
        return self.__servicio.calcular_costo(
            self.__duracion,
            impuesto=impuesto,
            descuento=descuento
        )

    # ======================================================
    # PROCESAR RESERVA (TRANSICION: PENDIENTE -> PROCESADA)
    # ======================================================

    def procesar(
        self,
        impuesto: float = 0,
        descuento: float = 0
    ) -> None:
        """
        Procesa la reserva, calculando el costo total y validando disponibilidad y reglas.

        Lógica de la máquina de estados:
        - Solo se permite procesar reservas en estado 'PENDIENTE'. Si la reserva se encuentra
          en estado 'PROCESADA', 'CONFIRMADA' o 'CANCELADA', la operación es rechazada.
        - Transición exitosa: 'PENDIENTE' -> 'PROCESADA'.

        Patrón try / except / else / finally:
        - try: Ejecuta la validación de estado y el cálculo de costo potencialmente propenso a fallas.
        - except: Captura fallos de validación (TypeError, ValueError, DatoInvalidoError,
          RecursoNoDisponibleError), los registra en el log y lanza ErrorProcesamientoReserva
          encadenando la causa original con `from error` (PEP 3134).
        - else: Se ejecuta ÚNICAMENTE si el bloque try culminó sin errores, asegurando la atomicidad
          del cambio de estado a 'PROCESADA' y la fijación del costo total.
        - finally: Se ejecuta de manera incondicional (haya o no excepción) para asentar en el log
          de auditoría la conclusión del intento de procesamiento.

        Args:
            impuesto (float, optional): Porcentaje tributario a sumar. Por defecto 0.
            descuento (float, optional): Porcentaje comercial a restar. Por defecto 0.

        Raises:
            EstadoReservaError: Si la reserva no se encuentra en estado 'PENDIENTE'.
            ErrorProcesamientoReserva: Si ocurre un error de datos, disponibilidad o cálculo,
                encadenando la excepción original.
        """
        try:
            # Condición de guarda: comprobar que la reserva esté estrictamente en estado "PENDIENTE"
            if self.__estado != "PENDIENTE":
                raise EstadoReservaError(
                    "Solo se pueden procesar reservas pendientes."
                )

            # Ejecutar el cálculo financiero delegando polimórficamente en el servicio
            total = self._calcular_costo(
                impuesto,
                descuento
            )

        except (TypeError, ValueError) as error:
            # Registrar el error técnico y la causa en el archivo de log para soporte y trazabilidad
            registrar_error(
                f"Error procesando reserva {self.identificador}",
                error
            )

            # Encadenamiento de excepciones (PEP 3134): se eleva una excepción de alto nivel
            # (ErrorProcesamientoReserva) enlazando explícitamente la causa original (`from error`)
            # para preservar la trazabilidad completa del fallo sin romper la abstracción.
            raise ErrorProcesamientoReserva(
                f"No fue posible procesar la reserva "
                f"{self.identificador}."
            ) from error

        else:
            # Bloque else: garantiza atomicidad, ejecutándose solo si no hubo ninguna excepción
            # Se fija el costo total calculado en el atributo de la reserva
            self.__costo_total = total

            # Transición en la máquina de estados: pasa formalmente a estado "PROCESADA"
            self.__estado = "PROCESADA"

            # Asentar en el log de eventos el procesamiento exitoso con el monto liquidado
            registrar_evento(
                f"Reserva procesada: {self.identificador} "
                f"| Costo: {total}"
            )

        finally:
            # Bloque finally: ejecución garantizada incondicionalmente para auditoría de intentos
            registrar_evento(
                f"Finalizó intento de procesamiento: "
                f"{self.identificador}"
            )

    # ======================================================
    # CONFIRMAR RESERVA (TRANSICION: PROCESADA -> CONFIRMADA)
    # ======================================================

    def confirmar(self) -> None:
        """
        Confirma la reserva previamente procesada y asegura el inventario físico necesario.

        Lógica de la máquina de estados:
        - Condición de guarda: La reserva DEBE encontrarse previamente en estado 'PROCESADA'.
          No se permite confirmar directamente reservas en estado 'PENDIENTE' (sin costo calculado)
          ni reservas ya 'CONFIRMADAS' o 'CANCELADAS'.
        - Transición exitosa: 'PROCESADA' -> 'CONFIRMADA'.

        Gestión de recursos:
        - Si el servicio reservado es de tipo ServicioEquipo, se ejecuta `reservar_existencias()`
          para descontar físicamente las unidades del inventario de bodega y se marca la
          bandera interna `__recurso_reservado = True`.

        Raises:
            EstadoReservaError: Si la reserva no se encuentra en estado 'PROCESADA'.
            RecursoNoDisponibleError: Si no hay inventario suficiente en bodega para confirmar.
            TypeError: Si la cantidad de equipos no es un número entero.
            ValueError: Si la cantidad de equipos es <= 0.
        """
        # Condición de guarda: verificar que la reserva ya haya sido procesada y cotizada
        if self.__estado != "PROCESADA":

            # Crear la excepción de transición de estado inválida
            error = EstadoReservaError(
                "La reserva debe estar procesada antes de confirmarse."
            )

            # Registrar el intento fallido en el log de errores
            registrar_error(
                f"Error al confirmar reserva {self.identificador}",
                error
            )

            # Lanzar la excepción para detener la operación
            raise error

        # Si el servicio corresponde a alquiler de equipos, comprometer el inventario físico en bodega
        if isinstance(self.__servicio, ServicioEquipo):

            try:
                # Descontar del inventario disponible la cantidad de equipos solicitada
                self.__servicio.reservar_existencias(
                    self.__cantidad
                )

            except (TypeError, ValueError) as error:
                # Registrar el fallo de existencias en el log de errores antes de re-lanzar
                registrar_error(
                    f"Error al descontar inventario "
                    f"en reserva {self.identificador}",
                    error
                )

                # Re-lanzar la excepción original para notificar al llamador del problema de stock
                raise

            # Marcar la bandera que indica que el inventario físico ha sido exitosamente descontado
            self.__recurso_reservado = True

        # Transición en la máquina de estados: pasa formalmente a estado "CONFIRMADA"
        self.__estado = "CONFIRMADA"

        # Registrar en el log de eventos la confirmación definitiva de la reserva
        registrar_evento(
            f"Reserva confirmada: {self.identificador}"
        )

    # ======================================================
    # CANCELAR RESERVA (TRANSICION: ACTIVA -> CANCELADA)
    # ======================================================

    def cancelar(self) -> None:
        """
        Cancela la reserva y restituye cualquier recurso o inventario físico comprometido.

        Lógica de la máquina de estados:
        - Condición de guarda: Si la reserva ya se encuentra en estado 'CANCELADA', se rechaza
          la operación para garantizar la integridad e idempotencia del ciclo de vida.
        - Se permite cancelar reservas en estado 'PENDIENTE', 'PROCESADA' o 'CONFIRMADA'.
        - Transición: Estado actual -> 'CANCELADA' (estado terminal definitivo).

        Restitución de inventario:
        - Si la bandera `__recurso_reservado` es True (se habían descontado existencias en bodega),
          se invoca `liberar_existencias()` para reponer las unidades al stock del servicio y
          se restablece la bandera a False.

        Raises:
            EstadoReservaError: Si la reserva ya se encontraba previamente cancelada.
            TypeError: Si la cantidad de equipos devuelta no es entera.
            ValueError: Si la cantidad de equipos devuelta no es positiva.
        """
        # Condición de guarda: evitar cancelar una reserva que ya se encuentra cancelada
        if self.__estado == "CANCELADA":

            # Crear la excepción informando que la reserva ya está en estado terminal cancelado
            error = EstadoReservaError(
                "La reserva ya se encuentra cancelada."
            )

            # Registrar el intento inválido en el log de errores
            registrar_error(
                f"Error al cancelar reserva {self.identificador}",
                error
            )

            # Lanzar el error de estado
            raise error

        # Si la reserva tenía recursos físicos comprometidos en inventario, devolverlos inmediatamente
        if self.__recurso_reservado:

            try:
                # Reintegrar las unidades retenidas al stock de equipos del servicio
                self.__servicio.liberar_existencias(
                    self.__cantidad
                )

            except (TypeError, ValueError) as error:
                # Registrar el error en el log en caso de inconsistencia al devolver inventario
                registrar_error(
                    f"Error al devolver inventario "
                    f"de reserva {self.identificador}",
                    error
                )

                # Re-lanzar la excepción para alertar de la falla operativa
                raise

            # Restablecer la bandera indicando que el recurso ya no está retenido por esta reserva
            self.__recurso_reservado = False

            # Registrar en el log de auditoría la reposición exitosa de equipos al almacén
            registrar_evento(
                f"Equipos devueltos al inventario: "
                f"{self.__cantidad}"
            )

        # Transición en la máquina de estados: fijar el estado terminal en "CANCELADA"
        self.__estado = "CANCELADA"

        # Registrar en el log de eventos la cancelación definitiva de la reserva
        registrar_evento(
            f"Reserva cancelada: {self.identificador}"
        )

    # ======================================================
    # INFORMACION DE LA RESERVA (IMPLEMENTACION DE ENTIDAD)
    # ======================================================

    def obtener_informacion(self) -> str:
        """
        Retorna una representación estructurada en texto con todos los datos de la reserva.

        Implementa el método abstracto exigido por la clase padre Entidad, permitiendo
        consultar cliente, servicio, inicio, fin, duración, estado y costo.

        Returns:
            str: Resumen completo formateado de la reserva.
        """
        # Formatear el costo monetario si ya fue calculado, o indicar texto pendiente si aún no lo está
        costo = (
            "Pendiente de cálculo"
            if self.__costo_total is None
            else f"${self.__costo_total:,.2f}"
        )

        # Construir y retornar la cadena descriptiva integral de la reserva
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
