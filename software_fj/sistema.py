"""
Módulo del Administrador Central del Sistema - Software FJ.

Este módulo implementa la clase principal `Sistema`, la cual actúa como
controlador central y punto de entrada unificado (patrón de diseño Fachada /
Facade) para toda la lógica de negocio de la plataforma Software FJ.

El administrador orquesta de manera integrada las tres áreas nucleares:
1. Gestión de Clientes: Registro, validación de identidad y datos de contacto.
2. Catálogo de Servicios: Soporte polimórfico para Salas, Equipos y Asesorías.
3. Ciclo de Vida de Reservas: Creación, tarificación financiera, control de
   disponibilidad horaria (detección de traslapes en salas), reserva de existencias
   y cancelación con liberación de recursos.

Adicionalmente, se integra con el subsistema de bitácora (`software_fj.registro`)
para proporcionar trazabilidad total de operaciones y captura centralizada de
excepciones del dominio de la aplicación.
"""

# ==========================================================
# IMPORTACIONES DE BIBLIOTECA ESTÁNDAR
# ==========================================================
from datetime import datetime

# ==========================================================
# IMPORTACIONES INTERNAS DEL PAQUETE SOFTWARE_FJ
# ==========================================================
from software_fj.entidades import Cliente
from software_fj.excepciones import (
    OperacionNoPermitidaError,
    RecursoNoDisponibleError,
    RegistroDuplicadoError
)
from software_fj.registro import (
    registrar_error,
    registrar_evento
)
from software_fj.reservas import Reserva
from software_fj.servicios import (
    Servicio,
    ServicioAsesoria,
    ServicioEquipo,
    ServicioSala
)


class Sistema:
    """
    Administrador central y fachada de la plataforma Software FJ.

    Esta clase encapsula la gestión integral del sistema sin dependencias
    externas de bases de datos, almacenando la información en colecciones
    en memoria y aplicando estrictas reglas de integridad referencial,
    unicidad de identificadores y control de disponibilidad de recursos.

    Attributes:
        __clientes (list[Cliente]): Lista privada con las entidades de clientes
            registrados en el sistema.
        __servicios (list[Servicio]): Catálogo privado con las instancias de
            servicios (Salas, Equipos, Asesorías) disponibles.
        __reservas (list[Reserva]): Colección privada con las reservas generadas,
            permitiendo supervisar su estado, cronograma y costos asociados.
    """

    def __init__(self) -> None:
        """
        Inicializa una nueva instancia del administrador central de Software FJ.

        Crea las estructuras de datos internas en memoria para almacenar clientes,
        servicios y reservas, y emite un registro de auditoría en la bitácora
        informando el inicio de operaciones del sistema.

        Args:
            Ninguno.

        Returns:
            None.
        """
        # Estructuras privadas para almacenar las colecciones del sistema en memoria.
        # Se utilizan listas privadas con doble guion bajo (name mangling) para
        # garantizar encapsulamiento estricto y evitar modificaciones externas no autorizadas.
        self.__clientes: list[Cliente] = []
        self.__servicios: list[Servicio] = []
        self.__reservas: list[Reserva] = []

        # Registro de auditoría para documentar el arranque formal del sistema en el archivo de log.
        registrar_evento(
            "Sistema Software FJ inicializado."
        )

    # ======================================================
    # CREACIÓN Y FÁBRICA DE CLIENTES CON REGISTRO DE ERRORES
    # ======================================================

    def crear_cliente(
        self,
        identificador: str,
        nombre: str,
        documento: str,
        correo: str,
        telefono: str
    ) -> Cliente:
        """
        Crea, valida e incorpora un nuevo cliente en el sistema.

        Aplica un patrón de fábrica que instancia el objeto `Cliente`,
        activando las validaciones internas de formato (correo, teléfono,
        documento y nombre no vacíos). Si ocurre un fallo en los datos,
        el error se registra en la bitácora y se propaga. Si la validación
        es exitosa, se procede a registrar al cliente en el sistema.

        Args:
            identificador (str): Código único asignado al cliente (ej. 'CLI-001').
            nombre (str): Nombre completo o razón social del cliente.
            documento (str): Número de identificación o cédula del cliente.
            correo (str): Dirección electrónica válida del cliente.
            telefono (str): Número telefónico en formato estándar colombiano.

        Returns:
            Cliente: Instancia del cliente recién creado y registrado.

        Raises:
            TypeError: Si alguno de los tipos de datos suministrados es inválido.
            ValueError: Si algún campo no cumple con el formato o longitud requerida.
            RegistroDuplicadoError: Si ya existe un cliente con el mismo ID o documento.
        """
        # Se utiliza un bloque try/except para capturar cualquier anomalía durante
        # la instanciación y validación del cliente antes de ingresarlo a la colección.
        try:
            # La creación de la entidad ejecuta automáticamente sus validaciones internas
            # de tipos, formato de correo con '@', estructura de teléfono y campos no vacíos.
            cliente = Cliente(
                identificador,
                nombre,
                documento,
                correo,
                telefono
            )

        except (TypeError, ValueError) as error:
            # En caso de datos inválidos, se asienta el incidente en la bitácora
            # para fines de auditoría forense y soporte técnico antes de relanzarlo.
            registrar_error(
                "Error durante la creación de un cliente",
                error
            )
            # Se relanza la excepción original para que la capa llamadora (UI o API)
            # reciba el motivo exacto del fallo y notifique adecuadamente al usuario.
            raise

        # Una vez validada la entidad individual, se delega su incorporación formal
        # en la colección del sistema, donde se validará la no duplicidad de registros.
        self.registrar_cliente(cliente)

        # Se retorna la referencia de la entidad creada y validada satisfactoriamente.
        return cliente

    # ======================================================
    # CREACIÓN DE SERVICIOS (SALAS, EQUIPOS Y ASESORÍAS)
    # ======================================================

    def crear_servicio_sala(
        self,
        identificador: str,
        nombre: str,
        capacidad: int,
        precio_hora: float,
        disponible: bool = True
    ) -> ServicioSala:
        """
        Crea, valida y registra un nuevo servicio de alquiler de sala de reuniones.

        Instancia un objeto `ServicioSala` validando que la capacidad y el precio
        por hora sean valores estrictamente positivos. Ante cualquier error de validación,
        lo registra en la bitácora de auditoría y lo relanza; si es válido, lo añade
        al catálogo central de servicios.

        Args:
            identificador (str): Identificador único del servicio (ej. 'SRV-001').
            nombre (str): Nombre descriptivo de la sala.
            capacidad (int): Número máximo de personas permitidas en la sala (debe ser > 0).
            precio_hora (float): Valor monetario por hora de uso de la sala (debe ser > 0).
            disponible (bool, optional): Estado de habilitación comercial. Por defecto True.

        Returns:
            ServicioSala: Instancia del servicio de sala creado y catalogado.

        Raises:
            TypeError: Si los parámetros no coinciden con los tipos esperados.
            ValueError: Si la capacidad o el precio por hora no son positivos.
            RegistroDuplicadoError: Si ya existe un servicio con el mismo identificador.
        """
        # Se captura cualquier falla durante la construcción de la entidad de sala.
        try:
            # Se instancia el servicio de sala, activando las validaciones de negocio de la clase.
            servicio = ServicioSala(
                identificador,
                nombre,
                capacidad,
                precio_hora,
                disponible
            )

        except (TypeError, ValueError) as error:
            # Se documenta en el log el intento fallido de registro de sala.
            registrar_error(
                "Error durante la creación de una sala",
                error
            )
            # Propagación de la excepción para manejo en la capa superior.
            raise

        # Se almacena en el catálogo del sistema garantizando unicidad de identificador.
        self.registrar_servicio(servicio)

        return servicio

    def crear_servicio_equipo(
        self,
        identificador: str,
        nombre: str,
        precio_dia: float,
        existencias: int,
        disponible: bool = True
    ) -> ServicioEquipo:
        """
        Crea, valida y registra un nuevo servicio de alquiler de equipos informáticos.

        Instancia un objeto `ServicioEquipo` validando que la tarifa por día sea mayor
        que cero y las existencias sean un número entero mayor o igual a cero. En caso de
        error, asienta el evento en el log y relanza la excepción.

        Args:
            identificador (str): Identificador único del servicio (ej. 'SRV-002').
            nombre (str): Denominación del equipo o kit tecnológico.
            precio_dia (float): Valor monetario del alquiler por jornada de uso (debe ser > 0).
            existencias (int): Número de unidades físicas disponibles en inventario (>= 0).
            disponible (bool, optional): Estado de habilitación comercial. Por defecto True.

        Returns:
            ServicioEquipo: Instancia del servicio de equipo creado y catalogado.

        Raises:
            TypeError: Si los tipos de los argumentos no son válidos.
            ValueError: Si el precio es menor o igual a cero o las existencias son negativas.
            RegistroDuplicadoError: Si el identificador ya existe en el catálogo.
        """
        try:
            # Construcción de la instancia y verificación de existencias e importes.
            servicio = ServicioEquipo(
                identificador,
                nombre,
                precio_dia,
                existencias,
                disponible
            )

        except (TypeError, ValueError) as error:
            # Auditoría del error en el archivo de registro.
            registrar_error(
                "Error durante la creación de un equipo",
                error
            )
            raise

        # Incorporación al catálogo del sistema si los datos son correctos.
        self.registrar_servicio(servicio)

        return servicio

    def crear_servicio_asesoria(
        self,
        identificador: str,
        nombre: str,
        especialidad: str,
        precio_hora: float,
        disponible: bool = True
    ) -> ServicioAsesoria:
        """
        Crea, valida y registra un nuevo servicio de consultoría o asesoría técnica.

        Instancia un objeto `ServicioAsesoria` validando que la especialidad no esté
        vacía y que el valor por hora sea un importe estrictamente positivo.

        Args:
            identificador (str): Identificador único del servicio (ej. 'SRV-003').
            nombre (str): Título o descripción del servicio de consultoría.
            especialidad (str): Área temática o disciplina técnica de la asesoría.
            precio_hora (float): Tarifa por hora de atención profesional (debe ser > 0).
            disponible (bool, optional): Estado de habilitación comercial. Por defecto True.

        Returns:
            ServicioAsesoria: Instancia del servicio de asesoría creado y catalogado.

        Raises:
            TypeError: Si los tipos de datos suministrados no corresponden.
            ValueError: Si el precio es inválido o los textos están vacíos.
            RegistroDuplicadoError: Si ya existe un servicio con ese identificador.
        """
        try:
            # Creación del objeto asesoría con validación de especialidad y tarifa horaria.
            servicio = ServicioAsesoria(
                identificador,
                nombre,
                especialidad,
                precio_hora,
                disponible
            )

        except (TypeError, ValueError) as error:
            # Registro en bitácora de incidencias.
            registrar_error(
                "Error durante la creación de una asesoría",
                error
            )
            raise

        # Incorporación formal al catálogo central de servicios.
        self.registrar_servicio(servicio)

        return servicio

    # ======================================================
    # ADMINISTRACIÓN Y BÚSQUEDA DE CLIENTES
    # ======================================================

    def registrar_cliente(self, cliente: Cliente) -> None:
        """
        Registra una instancia existente de `Cliente` en el repositorio del sistema.

        Verifica que el objeto sea de tipo `Cliente` y realiza una búsqueda exhaustiva
        para impedir que se dupliquen identificadores únicos o números de documento,
        garantizando la integridad de los datos comerciales. Utiliza el patrón
        try/except/else para auditar el resultado de la operación.

        Args:
            cliente (Cliente): Instancia de cliente que se desea añadir al sistema.

        Returns:
            None.

        Raises:
            TypeError: Si el objeto proporcionado no es una instancia de `Cliente`.
            RegistroDuplicadoError: Si ya existe un cliente con el mismo identificador
                o el mismo documento de identidad.
        """
        # Empleamos un bloque try/except/else para segregar claramente la lógica
        # de validación y almacenamiento, el manejo de errores y las acciones de éxito.
        try:
            # Validación de tipo defensiva para asegurar que solo se admitan objetos válidos.
            if not isinstance(cliente, Cliente):
                raise TypeError(
                    "Solo se pueden registrar objetos Cliente."
                )

            # Búsqueda lineal de duplicados en la lista de clientes registrados.
            # Esta comprobación protege la regla de negocio: no pueden coexistir dos clientes
            # con el mismo identificador de cuenta ni con el mismo documento de identidad (cédula).
            for existente in self.__clientes:
                # Verificación de colisión por identificador único del cliente.
                if existente.identificador == cliente.identificador:
                    raise RegistroDuplicadoError(
                        "Ya existe un cliente con ese identificador."
                    )

                # Verificación de colisión por número de documento legal.
                if existente.documento == cliente.documento:
                    raise RegistroDuplicadoError(
                        "Ya existe un cliente con ese documento."
                    )

            # Si todas las validaciones previas son superadas, se agrega a la lista interna.
            self.__clientes.append(cliente)

        except (TypeError, ValueError) as error:
            # En caso de error de tipo o duplicidad, se documenta el fallo en el log
            # y se relanza la excepción correspondiente para control del invocador.
            registrar_error(
                "Error al registrar un cliente",
                error
            )
            raise

        else:
            # El bloque else se ejecuta únicamente si el bloque try culminó sin errores.
            # Se asienta el evento exitoso de registro para trazabilidad del ciclo de vida.
            registrar_evento(
                f"Cliente registrado: {cliente.identificador}"
            )

    def buscar_cliente_por_documento(
        self,
        documento: str
    ) -> Cliente | None:
        """
        Busca un cliente registrado a partir de su número de documento de identidad.

        Recorre la lista interna de clientes comparando el documento exacto.
        Si encuentra coincidencia, retorna la instancia del cliente; de lo contrario,
        retorna `None`.

        Args:
            documento (str): Número de identificación o cédula a consultar.

        Returns:
            Cliente | None: Instancia del cliente encontrado, o `None` si no existe.
        """
        # Búsqueda secuencial sobre la colección de clientes en memoria.
        for cliente in self.__clientes:
            # Comparación exacta de la cadena de texto del documento.
            if cliente.documento == documento:
                # Retorno inmediato al encontrar la primera coincidencia garantizada como única.
                return cliente

        # Si finaliza el ciclo sin coincidencias, se indica la ausencia del registro con None.
        return None

    def buscar_cliente_por_identificador(
        self,
        identificador: str
    ) -> Cliente | None:
        """
        Busca un cliente registrado a partir de su identificador único de cuenta.

        Args:
            identificador (str): Código o identificador del cliente (ej. 'CLI-001').

        Returns:
            Cliente | None: Instancia del cliente coincidente, o `None` si no se localiza.
        """
        # Búsqueda lineal iterando sobre la colección de clientes.
        for cliente in self.__clientes:
            # Comprobación de coincidencia por identificador de entidad.
            if cliente.identificador == identificador:
                return cliente

        # Retorna None si ningún cliente posee dicho identificador.
        return None

    def buscar_cliente_por_id(
        self,
        identificador: str
    ) -> Cliente | None:
        """
        Alias de conveniencia para consultar un cliente por su identificador.

        Delega la operación en `buscar_cliente_por_identificador`.

        Args:
            identificador (str): Identificador único del cliente a localizar.

        Returns:
            Cliente | None: Instancia del cliente si existe, o `None` si no se halla.
        """
        # Delegación directa al método principal de búsqueda por identificador.
        return self.buscar_cliente_por_identificador(identificador)

    def listar_clientes(self) -> tuple[Cliente, ...]:
        """
        Retorna la totalidad de clientes registrados en el sistema.

        Para preservar el principio de encapsulamiento y evitar mutaciones
        accidentales desde el exterior, se retorna una tupla inmutable en lugar
        de la lista interna de clientes.

        Args:
            Ninguno.

        Returns:
            tuple[Cliente, ...]: Tupla inmutable con las instancias de clientes registrados.
        """
        # Se genera y retorna una tupla inmutable para proteger la lista interna privada.
        return tuple(self.__clientes)

    def cantidad_clientes(self) -> int:
        """
        Retorna la cantidad total de clientes registrados en el sistema.

        Args:
            Ninguno.

        Returns:
            int: Número de clientes actualmente almacenados en memoria.
        """
        # Conteo directo de elementos en la colección interna de clientes.
        return len(self.__clientes)

    # ======================================================
    # ADMINISTRACIÓN Y BÚSQUEDA DE SERVICIOS
    # ======================================================

    def registrar_servicio(self, servicio: Servicio) -> None:
        """
        Registra una instancia de servicio en el catálogo central del sistema.

        Verifica que el objeto sea una subclase válida de `Servicio` y asegura
        la unicidad de su identificador en el catálogo comercial. Utiliza el patrón
        try/except/else para asentar bitácora de auditoría.

        Args:
            servicio (Servicio): Instancia de ServicioSala, ServicioEquipo o
                ServicioAsesoria a catalogar.

        Returns:
            None.

        Raises:
            TypeError: Si el objeto no es una instancia de `Servicio`.
            RegistroDuplicadoError: Si ya existe un servicio con el mismo identificador.
        """
        try:
            # Comprobación de tipo polimórfica: admite cualquier subclase de Servicio.
            if not isinstance(servicio, Servicio):
                raise TypeError(
                    "Solo se pueden registrar objetos Servicio."
                )

            # Comprobación de identificadores duplicados en el catálogo existente.
            for existente in self.__servicios:
                if existente.identificador == servicio.identificador:
                    raise RegistroDuplicadoError(
                        "Ya existe un servicio con ese identificador."
                    )

            # Adición del nuevo servicio al catálogo central.
            self.__servicios.append(servicio)

        except (TypeError, ValueError) as error:
            # En caso de colisión o tipo incorrecto, se audita el fallo y se relanza.
            registrar_error(
                "Error al registrar un servicio",
                error
            )
            raise

        else:
            # En caso de éxito, se asienta en la bitácora la incorporación comercial del servicio.
            registrar_evento(
                f"Servicio registrado: {servicio.identificador} "
                f"| {servicio.nombre}"
            )

    def buscar_servicio_por_identificador(
        self,
        identificador: str
    ) -> Servicio | None:
        """
        Busca un servicio en el catálogo a partir de su identificador único.

        Args:
            identificador (str): Código o identificador del servicio (ej. 'SRV-001').

        Returns:
            Servicio | None: Instancia del servicio encontrado, o `None` si no existe.
        """
        # Recorrido secuencial del catálogo de servicios en memoria.
        for servicio in self.__servicios:
            if servicio.identificador == identificador:
                return servicio

        return None

    def buscar_servicio_por_id(
        self,
        identificador: str
    ) -> Servicio | None:
        """
        Alias de conveniencia para consultar un servicio por su identificador.

        Delega la operación en `buscar_servicio_por_identificador`.

        Args:
            identificador (str): Identificador único del servicio.

        Returns:
            Servicio | None: Instancia del servicio si existe, o `None` en caso contrario.
        """
        # Delegación hacia el método canónico de búsqueda de servicios.
        return self.buscar_servicio_por_identificador(identificador)

    def listar_servicios(self) -> tuple[Servicio, ...]:
        """
        Retorna la lista de todos los servicios registrados como una tupla inmutable.

        Args:
            Ninguno.

        Returns:
            tuple[Servicio, ...]: Tupla inmutable con los servicios del catálogo.
        """
        # Copia defensiva en tupla inmutable para proteger el catálogo interno.
        return tuple(self.__servicios)

    def cantidad_servicios(self) -> int:
        """
        Retorna la cantidad total de servicios registrados en el catálogo.

        Args:
            Ninguno.

        Returns:
            int: Número de servicios disponibles en el sistema.
        """
        return len(self.__servicios)

    # ======================================================
    # ADMINISTRACIÓN Y CONTROL DE RESERVAS
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
        Crea, valida y almacena una nueva reserva en estado inicial PENDIENTE.

        Aplica integridad referencial estricta: verifica que el cliente y el
        servicio existan previamente en el sistema antes de permitir la reserva.
        Asimismo, previene identificadores de reserva duplicados y delega la
        construcción y validaciones paramétricas a la clase `Reserva`.

        Args:
            identificador (str): Código único asignado a la reserva (ej. 'RES-001').
            identificador_cliente (str): Código del cliente previamente registrado.
            identificador_servicio (str): Código del servicio previamente registrado.
            duracion (float): Cantidad de tiempo (horas o días, según el servicio).
            cantidad (int, optional): Número de unidades requeridas (para equipos). Por defecto 1.
            personas (int, optional): Número de asistentes previstos (para salas). Por defecto 1.
            fecha_hora_inicio (datetime | None, optional): Fecha y hora programada de inicio.

        Returns:
            Reserva: Instancia de la reserva creada en estado 'PENDIENTE'.

        Raises:
            RegistroDuplicadoError: Si ya existe una reserva con el mismo identificador.
            OperacionNoPermitidaError: Si el cliente o el servicio no existen en el sistema.
            TypeError: Si alguno de los tipos de parámetros no es válido.
            ValueError: Si la duración, cantidad o personas contienen valores no permitidos.
        """
        try:
            # 1. Validación de no duplicidad de identificador de reserva.
            # Se examina la lista existente para asegurar que el ID sea único en el sistema.
            for existente in self.__reservas:
                if existente.identificador == identificador:
                    raise RegistroDuplicadoError(
                        "Ya existe una reserva con ese identificador."
                    )

            # 2. Control de integridad referencial: Búsqueda del cliente solicitante.
            # No se permite crear reservas para clientes anónimos o no registrados previamente.
            cliente = self.buscar_cliente_por_identificador(
                identificador_cliente
            )

            if cliente is None:
                raise OperacionNoPermitidaError(
                    "El cliente indicado no está registrado."
                )

            # 3. Control de integridad referencial: Búsqueda del servicio solicitado en el catálogo.
            # El servicio debe existir formalmente en el sistema.
            servicio = self.buscar_servicio_por_identificador(
                identificador_servicio
            )

            if servicio is None:
                raise OperacionNoPermitidaError(
                    "El servicio indicado no está registrado."
                )

            # 4. Construcción de la instancia Reserva.
            # La clase Reserva valida internamente duración positiva, parámetros numéricos y fechas.
            reserva = Reserva(
                identificador,
                cliente,
                servicio,
                duracion,
                cantidad,
                personas,
                fecha_hora_inicio
            )

            # 5. Inclusión de la reserva validada en la colección del sistema.
            self.__reservas.append(reserva)

        except (TypeError, ValueError) as error:
            # En caso de datos inválidos o fallos de negocio, se registra en la bitácora y se relanza.
            registrar_error(
                f"Error al crear reserva {identificador}",
                error
            )
            raise

        else:
            # Bloque else: Se ejecuta solo si la creación y guardado fueron completamente exitosos.
            registrar_evento(
                f"Reserva incorporada al sistema: {identificador}"
            )
            return reserva

    def buscar_reserva_por_identificador(
        self,
        identificador: str
    ) -> Reserva | None:
        """
        Busca una reserva en el sistema a partir de su identificador único.

        Args:
            identificador (str): Código o identificador de la reserva (ej. 'RES-001').

        Returns:
            Reserva | None: Instancia de la reserva si se encuentra, o `None` en caso contrario.
        """
        # Búsqueda secuencial sobre la lista interna de reservas registradas.
        for reserva in self.__reservas:
            if reserva.identificador == identificador:
                return reserva

        return None

    def buscar_reserva_por_id(
        self,
        identificador: str
    ) -> Reserva | None:
        """
        Alias de conveniencia para consultar una reserva por su identificador.

        Delega la operación en `buscar_reserva_por_identificador`.

        Args:
            identificador (str): Identificador único de la reserva a buscar.

        Returns:
            Reserva | None: Instancia de la reserva si se halla, o `None` si no existe.
        """
        # Delegación hacia la función principal de búsqueda de reservas.
        return self.buscar_reserva_por_identificador(identificador)

    def listar_reservas(self) -> tuple[Reserva, ...]:
        """
        Retorna la totalidad de reservas registradas como una tupla inmutable.

        Args:
            Ninguno.

        Returns:
            tuple[Reserva, ...]: Tupla inmutable con las reservas existentes en el sistema.
        """
        # Retorno de tupla inmutable para proteger la colección interna de mutaciones externas.
        return tuple(self.__reservas)

    def cantidad_reservas(self) -> int:
        """
        Retorna la cantidad total de reservas registradas en el sistema.

        Args:
            Ninguno.

        Returns:
            int: Número total de reservas almacenadas.
        """
        return len(self.__reservas)

    # ======================================================
    # PROCESAMIENTO FINANCIERO DE RESERVAS
    # ======================================================

    def procesar_reserva(
        self,
        identificador: str,
        impuesto: float = 0,
        descuento: float = 0
    ) -> None:
        """
        Calcula el costo total de una reserva y cambia su estado a PROCESADA.

        Localiza la reserva por su identificador y delega el cálculo financiero
        a la entidad `Reserva`, la cual aplica la tarifa base del servicio
        específico (empleando polimorfismo) e incorpora los porcentajes de
        impuesto y descuento suministrados.

        Args:
            identificador (str): Identificador de la reserva a procesar.
            impuesto (float, optional): Porcentaje de recargo fiscal (0 a 100). Por defecto 0.
            descuento (float, optional): Porcentaje de deducción comercial (0 a 100). Por defecto 0.

        Returns:
            None.

        Raises:
            OperacionNoPermitidaError: Si no se encuentra la reserva con el ID indicado.
            ErrorProcesamientoReserva: Si ocurre un error en el cálculo o estado de la reserva.
        """
        # Localización de la reserva en el repositorio central.
        reserva = self.buscar_reserva_por_identificador(
            identificador
        )

        # Si la reserva no existe, no es posible proceder con la liquidación financiera.
        if reserva is None:
            raise OperacionNoPermitidaError(
                "No se encontró la reserva solicitada."
            )

        # Delegación a la entidad Reserva, que valida estados previos y computa el costo total.
        reserva.procesar(impuesto, descuento)

    # ======================================================
    # CONFIRMACIÓN Y VALIDACIÓN DE TRASLAPE DE HORARIOS
    # ======================================================

    def confirmar_reserva(self, identificador: str) -> None:
        """
        Confirma una reserva previamente procesada, validando disponibilidad física y temporal.

        En el caso de servicios de tipo `ServicioSala`, ejecuta un algoritmo riguroso
        de detección de solapamiento de intervalos de tiempo (Schedule Overlap Detection)
        frente a todas las reservas activas (PROCESADA o CONFIRMADA) para esa misma sala.
        Si se detecta un conflicto horario, se rechaza la confirmación y se asienta el
        error en la bitácora.

        Para servicios de tipo `ServicioEquipo`, el método `confirmar()` de la reserva
        se encarga internamente de verificar y descontar las unidades del inventario.

        Args:
            identificador (str): Identificador único de la reserva a confirmar.

        Returns:
            None.

        Raises:
            OperacionNoPermitidaError: Si la reserva no existe en el sistema.
            RecursoNoDisponibleError: Si se detecta un cruce de horarios en la misma sala,
                o si las existencias de equipos son insuficientes.
            EstadoReservaError: Si la reserva no se encuentra en estado 'PROCESADA'.
        """
        # 1. Búsqueda y validación de existencia de la reserva solicitada.
        reserva = self.buscar_reserva_por_identificador(
            identificador
        )

        if reserva is None:
            raise OperacionNoPermitidaError(
                "No se encontró la reserva solicitada."
            )

        # 2. Control específico de concurrencia temporal y exclusividad física para salas.
        # Las salas son recursos no compartibles: no pueden ser ocupadas por dos clientes simultáneamente.
        if isinstance(reserva.servicio, ServicioSala):

            # Iteramos sobre todas las demás reservas para verificar posibles cruces de agenda.
            for otra in self.__reservas:

                # Omitimos la comparación de la reserva consigo misma.
                if otra.identificador == reserva.identificador:
                    continue

                # Verificamos si la otra reserva corresponde exactamente a la misma sala física.
                misma_sala = (
                    otra.servicio.identificador
                    == reserva.servicio.identificador
                )

                # Solo generan conflicto aquellas reservas que están activas y comprometidas
                # (es decir, en estado 'PROCESADA' en trámite o 'CONFIRMADA' en firme).
                # Las reservas pendientes no han sido liquidadas y las canceladas liberaron el espacio.
                reserva_activa = otra.estado in (
                    "PROCESADA",
                    "CONFIRMADA"
                )

                # Si es la misma sala física y la reserva evaluada se encuentra activa:
                if misma_sala and reserva_activa:

                    # Algoritmo matemático estándar de detección de traslape entre intervalos:
                    # Sean dos rangos [Inicio_A, Fin_A) e [Inicio_B, Fin_B).
                    # Existe solapamiento si y solo si:
                    #   (Inicio_A < Fin_B) Y (Inicio_B < Fin_A)
                    # Esta fórmula lógica contempla exhaustivamente todos los escenarios:
                    # - Caso 1: La nueva reserva empieza antes y termina en medio de la reserva existente.
                    # - Caso 2: La nueva reserva empieza durante la existente y termina después.
                    # - Caso 3: La nueva reserva está completamente contenida dentro del intervalo existente.
                    # - Caso 4: La nueva reserva envuelve o contiene por completo a la existente.
                    hay_cruce = (
                        reserva.fecha_hora_inicio
                        < otra.fecha_hora_fin
                        and
                        otra.fecha_hora_inicio
                        < reserva.fecha_hora_fin
                    )

                    # Si se comprueba el traslape de horarios, se bloquea la confirmación.
                    if hay_cruce:
                        # Se construye la excepción informativa indicando la sala y el conflicto.
                        error = RecursoNoDisponibleError(
                            f"La sala '{reserva.servicio.nombre}' "
                            "ya está ocupada en ese horario."
                        )

                        # Se asienta el conflicto en la bitácora para registro de incidentes de agenda.
                        registrar_error(
                            f"Conflicto de horario en {identificador}",
                            error
                        )

                        # Se interrumpe la operación arrojando la excepción al invocador.
                        raise error

        # 3. Si no hubo conflictos de horario (o si es otro tipo de servicio),
        # se delega la confirmación formal al método confirmar() de la Reserva.
        # Nota: En equipos, reserva.confirmar() descuenta las unidades de las existencias.
        reserva.confirmar()

    # ======================================================
    # CANCELACIÓN DE RESERVAS Y LIBERACIÓN DE RECURSOS
    # ======================================================

    def cancelar_reserva(self, identificador: str) -> None:
        """
        Cancela una reserva existente y restituye los recursos asociados al sistema.

        Busca la reserva en el repositorio del sistema y ejecuta su cancelación.
        Si la reserva estaba en estado 'CONFIRMADA' y correspondía a un alquiler de
        equipos, el método `cancelar()` de la reserva reintegrará de manera automática
        las unidades reservadas a las existencias físicas del inventario.

        Args:
            identificador (str): Identificador único de la reserva a cancelar.

        Returns:
            None.

        Raises:
            OperacionNoPermitidaError: Si la reserva indicada no existe en el sistema.
            EstadoReservaError: Si la reserva ya se encontraba cancelada previamente.
        """
        # Localización de la reserva en el registro central.
        reserva = self.buscar_reserva_por_identificador(
            identificador
        )

        # Validación de existencia previa.
        if reserva is None:
            raise OperacionNoPermitidaError(
                "No se encontró la reserva solicitada."
            )

        # Se delega la cancelación a la entidad Reserva.
        # Esto actualiza el estado a 'CANCELADA' y, si era un equipo confirmado,
        # incrementa nuevamente las existencias del equipo liberándolas para futuros alquileres.
        reserva.cancelar()
