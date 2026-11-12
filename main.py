"""
Módulo Principal de la Aplicación - Software FJ.
Universidad Nacional Abierta y a Distancia (UNAD).

Este módulo constituye el punto de entrada principal y la interfaz de usuario
por consola (CLI) para el sistema de gestión de Software FJ.

Proporciona las siguientes funcionalidades principales:
1. Captura y validación robusta de datos de entrada desde teclado:
   - Cadenas de texto no vacías (`leer_texto`).
   - Números enteros con validación de límite inferior (`leer_entero`).
   - Números decimales positivos y finitos (`leer_decimal`).
   - Valores porcentuales dentro del rango [0, 100] (`leer_porcentaje`).
   - Fechas y horas en formato 'AAAA-MM-DD HH:MM' con reintentos (`leer_fecha_hora`).
2. Menús interactivos para la gestión de las entidades del negocio:
   - Registro de clientes con validación de formato y unicidad.
   - Registro de servicios especializados (salas, equipos y asesorías).
   - Creación, procesamiento financiero, confirmación y cancelación de reservas.
   - Consulta y listado tabular de clientes, servicios y reservas registradas.
   - Visualización y auditoría del historial de eventos y errores en `sistema.log`.
3. Manejo integral de excepciones para prevenir interrupciones inesperadas
   durante la ejecución del programa y garantizar una experiencia de usuario fluida.
"""

from datetime import datetime
import math

from software_fj.sistema import Sistema
from software_fj.servicios import (
    ServicioSala,
    ServicioEquipo,
    ServicioAsesoria
)
from software_fj.registro import (
    ARCHIVO_LOG,
    registrar_evento,
    registrar_error
)


# ==========================================================
# FUNCIONES DE ENTRADA Y VALIDACION DE DATOS
# ==========================================================

def leer_texto(mensaje: str) -> str:
    """
    Solicita una cadena de texto no vacía al usuario por teclado.

    Repite la solicitud de forma continua hasta que el usuario introduzca
    una cadena con contenido real, eliminando espacios en blanco innecesarios
    al inicio y al final.

    Args:
        mensaje (str): Texto explicativo o prompt que se muestra en consola.

    Returns:
        str: Cadena de texto depurada y garantizada no vacía.
    """
    # Bucle infinito que se ejecuta hasta obtener una entrada válida
    while True:

        # Capturamos la entrada del usuario y removemos espacios en blanco iniciales y finales
        valor = input(mensaje).strip()

        # Si la cadena no quedó vacía tras el strip, retornamos el texto válido
        if valor:
            return valor

        # Si el usuario solo pulsó Enter o espacios en blanco, notificamos y reintentamos
        print("El dato no puede estar vacío.")


def leer_entero(
    mensaje: str,
    minimo: int = 1
) -> int:
    """
    Solicita un número entero por teclado asegurando que cumpla con un valor mínimo.

    Maneja internamente errores de conversión numérica (ValueError) y valida
    que el número suministrado no sea menor al umbral mínimo permitido.

    Args:
        mensaje (str): Prompt que se le muestra al usuario en la consola.
        minimo (int, opcional): Valor entero mínimo aceptable. Por defecto es 1.

    Returns:
        int: Número entero validado que cumple con la cota mínima.
    """
    # Bucle interactivo de captura hasta recibir un número entero válido
    while True:

        try:

            # Convertimos la entrada textual del usuario a un entero primitivo
            valor = int(input(mensaje))

            # Verificamos si el número entero cumple con el límite inferior exigido
            if valor < minimo:
                print(f"El valor mínimo permitido es {minimo}.")
                continue

            # Si el dato es correcto y cumple el mínimo, se devuelve el valor
            return valor

        except ValueError:
            # Capturamos entradas que contengan letras, símbolos o formatos incompatibles
            print("Introduce un número entero válido.")


def leer_decimal(
    mensaje: str,
    minimo: float = 0.01
) -> float:
    """
    Solicita un número decimal por teclado verificando su validez y rango mínimo.

    Permite tanto el uso de comas como de puntos como separador decimal,
    comprueba que el número sea finito y que sea mayor o igual al valor mínimo.

    Args:
        mensaje (str): Mensaje indicativo para solicitar el dato en consola.
        minimo (float, opcional): Valor decimal mínimo permitido. Por defecto es 0.01.

    Returns:
        float: Número decimal en punto flotante validado.
    """
    # Ciclo de solicitud iterativa para garantizar un valor numérico conforme
    while True:

        try:

            # Reemplazamos posibles comas por puntos para compatibilidad con float()
            valor = float(
                input(mensaje).replace(",", ".")
            )

            # Comprobamos que el número no sea infinito o NaN y que cumpla el mínimo
            if not math.isfinite(valor) or valor < minimo:
                print(
                    f"Introduce un número mayor o igual a {minimo}."
                )
                continue

            # Retornamos el número en punto flotante debidamente validado
            return valor

        except ValueError:
            # Capturamos excepciones generadas por caracteres no numéricos
            print("Introduce un número válido.")


def leer_porcentaje(mensaje: str) -> float:
    """
    Solicita un valor porcentual al usuario acotado estrictamente entre 0 y 100.

    Admite coma o punto decimal y valida que el valor se encuentre en el
    intervalo cerrado [0.0, 100.0] para aplicar impuestos o descuentos.

    Args:
        mensaje (str): Mensaje a mostrar al usuario para solicitar el porcentaje.

    Returns:
        float: Valor numérico flotante en el rango de 0 a 100.
    """
    # Bucle que persiste hasta que el usuario digite un porcentaje dentro de los límites
    while True:

        try:

            # Reemplazamos coma por punto decimal y convertimos a número flotante
            valor = float(
                input(mensaje).replace(",", ".")
            )

            # Validamos que sea un número finito y que esté estrictamente entre 0 y 100
            if not math.isfinite(valor) or not 0 <= valor <= 100:
                print("El porcentaje debe estar entre 0 y 100.")
                continue

            # Devolvemos el porcentaje válido
            return valor

        except ValueError:
            # Manejamos errores en caso de entradas alfabéticas o con formato incorrecto
            print("Introduce un porcentaje válido.")


def leer_fecha_hora() -> datetime | None:
    """
    Solicita al usuario una fecha y hora por teclado con control de reintentos.

    Permite ingresar una fecha bajo el formato 'AAAA-MM-DD HH:MM'. Si el usuario
    presiona Enter sin escribir texto, retorna None para indicar el uso de la
    fecha y hora actual del sistema. En caso de error de sintaxis, captura la
    excepción internamente y solicita el dato de nuevo mediante un ciclo while,
    evitando la pérdida de información en el formulario de reservas.

    Returns:
        datetime | None: Objeto datetime correspondiente a la fecha ingresada,
        o None si se optó por la fecha y hora actual del sistema.
    """
    # Mostramos la guía visual del formato esperado para orientar al usuario
    print("Formato de fecha: AAAA-MM-DD HH:MM")

    # Bucle interactivo para capturar la fecha sin interrumpir el flujo del menú
    while True:

        # Leemos el texto eliminando espacios sobrantes en los extremos
        valor = input(
            "Fecha y hora de inicio (Enter = ahora): "
        ).strip()

        # Si el usuario presiona Enter dejando el campo vacío, se asume la fecha actual
        if not valor:
            return None

        try:

            # Parseamos la cadena aplicando la máscara año-mes-día hora:minuto
            fecha = datetime.strptime(
                valor,
                "%Y-%m-%d %H:%M"
            )

            # Retornamos el objeto datetime resultante si la conversión fue exitosa
            return fecha

        except ValueError:
            # Capturamos el error de parseo y solicitamos reintentar sin lanzar excepción
            print(
                "Fecha u hora incorrecta. Ejemplo válido: 2026-12-15 10:00. Intenta de nuevo."
            )


# ==========================================================
# MOSTRAR MENU PRINCIPAL
# ==========================================================

def mostrar_menu() -> None:
    """
    Despliega en la consola el menú principal de opciones de Software FJ.

    Presenta de manera organizada y visual las distintas acciones que el
    usuario puede ejecutar en el sistema de gestión.

    Returns:
        None
    """
    # Encabezado visual y título de la aplicación
    print("\n")
    print("=" * 60)
    print("                  SOFTWARE FJ")
    print("=" * 60)

    # Subtítulo con los módulos principales del sistema
    print(" SISTEMA INTEGRAL DE GESTION")
    print(" Clientes | Servicios | Reservas")

    print("-" * 60)

    # Listado numerado de las opciones interactivas disponibles
    print(" 1. Registrar cliente")
    print(" 2. Registrar servicio")
    print(" 3. Crear reserva")
    print(" 4. Consultar clientes")
    print(" 5. Consultar servicios")
    print(" 6. Consultar reservas")
    print(" 7. Procesar reserva")
    print(" 8. Confirmar reserva")
    print(" 9. Cancelar reserva")
    print(" 10. Ver registro de logs")
    print(" 0. Salir")

    print("=" * 60)


# ==========================================================
# 1. REGISTRAR CLIENTE
# ==========================================================

def menu_registrar_cliente(sistema: Sistema) -> None:
    """
    Gestiona el registro interactivo de un nuevo cliente en el sistema.

    Solicita por teclado los datos personales requeridos (identificador,
    nombre completo, documento, correo electrónico y teléfono) y los valida
    a través de las reglas de dominio del modelo de Cliente.

    Args:
        sistema (Sistema): Instancia central del sistema donde se registrará el cliente.

    Returns:
        None
    """
    print("\nREGISTRO DE CLIENTE")

    # Captura validada del código identificador único del cliente
    identificador = leer_texto("Identificador: ")

    # Captura del nombre completo del cliente
    nombre = leer_texto("Nombre completo: ")

    # Captura del documento de identidad
    documento = leer_texto("Documento: ")

    # Captura del correo electrónico (validado internamente por Cliente)
    correo = leer_texto("Correo electrónico: ")

    # Captura del número telefónico de contacto
    telefono = leer_texto("Teléfono: ")

    # Creamos el cliente delegando en la capa de negocio del sistema
    cliente = sistema.crear_cliente(
        identificador,
        nombre,
        documento,
        correo,
        telefono
    )

    # Informamos la confirmación del registro y mostramos los datos almacenados
    print("\nCliente registrado correctamente.")
    print(cliente.obtener_informacion())


# ==========================================================
# 2. REGISTRAR SERVICIO
# ==========================================================

def menu_registrar_servicio(sistema: Sistema) -> None:
    """
    Gestiona la creación interactiva de un servicio en el catálogo de Software FJ.

    Permite al usuario elegir entre tres tipos de servicios (salas, equipos o
    asesorías especializadas) empleando un bucle de reintento para evitar
    abortar si se ingresa una opción inválida. Luego solicita los atributos
    comunes y específicos de la categoría seleccionada.

    Args:
        sistema (Sistema): Instancia central del sistema donde se añadirá el servicio.

    Returns:
        None
    """
    print("\nREGISTRO DE SERVICIOS")

    # Bucle interactivo para la selección del tipo de servicio con reintento ante opción inválida
    while True:

        # Desplegamos las opciones de tipos de servicio disponibles
        print("\nTipos de servicio:")
        print("1. Reservas de salas")
        print("2. Alquiler de equipos")
        print("3. Asesorías especializadas")

        # Capturamos la opción digitada por el usuario
        opcion = input("Selecciona el tipo de servicio (1-3): ").strip()

        # Verificamos si la opción corresponde a una de las categorías válidas
        if opcion in ("1", "2", "3"):
            break

        # Si el usuario ingresa una opción no reconocida, notificamos y solicitamos nuevamente
        print("Tipo de servicio no válido. Por favor selecciona una opción entre 1 y 3.")

    # Capturamos los campos generales compartidos por todos los servicios
    identificador = leer_texto("Identificador: ")
    nombre = leer_texto("Nombre del servicio: ")

    # Evaluamos la opción seleccionada para pedir los datos particulares de cada tipo
    if opcion == "1":

        # Para salas se requiere la capacidad máxima de aforo y el precio por hora
        capacidad = leer_entero("Capacidad de la sala: ")
        precio = leer_decimal("Precio por hora: ")

        # Instanciamos y almacenamos el servicio de sala en el sistema
        servicio = sistema.crear_servicio_sala(
            identificador,
            nombre,
            capacidad,
            precio
        )

    elif opcion == "2":

        # Para alquiler de equipos se requiere la tarifa diaria y las unidades físicas en stock
        precio = leer_decimal("Precio por día: ")
        existencias = leer_entero("Cantidad de equipos: ")

        # Instanciamos y registramos el servicio de equipos con inventario
        servicio = sistema.crear_servicio_equipo(
            identificador,
            nombre,
            precio,
            existencias
        )

    else:

        # Para asesorías especializadas se requiere la disciplina técnica y la tarifa horaria
        especialidad = leer_texto("Especialidad: ")
        precio = leer_decimal("Precio por hora: ")

        # Instanciamos y registramos el servicio de asesoría especializada
        servicio = sistema.crear_servicio_asesoria(
            identificador,
            nombre,
            especialidad,
            precio
        )

    # Notificamos el registro exitoso y mostramos la descripción polimórfica del servicio
    print("\nServicio registrado correctamente.")
    print(servicio.describir_servicio())


# ==========================================================
# 3. CREAR RESERVA
# ==========================================================

def menu_crear_reserva(sistema: Sistema) -> None:
    """
    Gestiona la creación interactiva de una nueva reserva en el sistema.

    Muestra los clientes y servicios registrados para facilitar la selección.
    Solicita los identificadores, la duración requerida, parámetros específicos
    según la naturaleza del servicio (aforo para salas o unidades para equipos)
    y la fecha y hora de inicio de la reserva.

    Args:
        sistema (Sistema): Instancia central del sistema que gestiona las reservas.

    Returns:
        None

    Raises:
        ValueError: Si el identificador de servicio proporcionado no existe en el sistema.
    """
    print("\nCREACION DE RESERVA")

    # Mostramos los clientes disponibles para que el usuario conozca los identificadores válidos
    print("\nCLIENTES DISPONIBLES:")
    for cliente in sistema.listar_clientes():
        print(
            cliente.identificador,
            "-",
            cliente.nombre
        )

    # Capturamos el identificador único para la nueva reserva a registrar
    identificador = leer_texto("\nID de la reserva: ")

    # Capturamos el identificador del cliente que solicita la reserva
    identificador_cliente = leer_texto(
        "ID del cliente: "
    )

    # Listamos el catálogo de servicios disponibles para apoyar la selección del usuario
    print("\nSERVICIOS DISPONIBLES:")
    for servicio in sistema.listar_servicios():
        print(
            servicio.identificador,
            "-",
            servicio.describir_servicio()
        )

    # Solicitamos el identificador del servicio que el cliente desea reservar
    identificador_servicio = leer_texto(
        "\nID del servicio: "
    )

    # Buscamos la instancia del servicio en el sistema para validar su existencia y tipo
    servicio = sistema.buscar_servicio_por_identificador(
        identificador_servicio
    )

    # Si no se encuentra el servicio, lanzamos una excepción explicativa
    if servicio is None:
        raise ValueError("El servicio seleccionado no existe.")

    # Solicitamos la duración del servicio (en horas o días según el tipo)
    duracion = leer_decimal(
        "Duración (horas o días, según el servicio): "
    )

    # Valores por defecto para parámetros condicionales
    cantidad = 1
    personas = 1

    # Determinamos datos adicionales requeridos según la categoría específica del servicio
    if isinstance(servicio, ServicioSala):
        # Para salas de reuniones o eventos se debe validar el número de asistentes frente al aforo
        personas = leer_entero(
            "Número de personas: "
        )

    elif isinstance(servicio, ServicioEquipo):
        # Para equipos se debe validar la cantidad de unidades solicitadas frente al inventario
        cantidad = leer_entero(
            "Cantidad de equipos que desea alquilar: "
        )

    # Solicitamos la fecha y hora programada para el inicio del servicio
    fecha_inicio = leer_fecha_hora()

    # Delegamos al sistema central la creación y registro formal de la reserva
    reserva = sistema.crear_reserva(
        identificador,
        identificador_cliente,
        identificador_servicio,
        duracion,
        cantidad,
        personas,
        fecha_inicio
    )

    # Informamos el éxito de la operación y mostramos los detalles de la reserva generada
    print("\nReserva creada correctamente.")
    print(reserva.obtener_informacion())


# ==========================================================
# 4. CONSULTAR Y LISTAR CLIENTES
# ==========================================================

def menu_listar_clientes(sistema: Sistema) -> None:
    """
    Consulta y muestra en pantalla la lista de todos los clientes registrados.

    Recorre la colección de clientes almacenada en el sistema y presenta
    la ficha de información detallada de cada uno de ellos junto con el total.

    Args:
        sistema (Sistema): Instancia central del sistema que contiene los clientes.

    Returns:
        None
    """
    # Obtenemos la lista completa de clientes registrados en el sistema
    clientes = sistema.listar_clientes()

    print("\nCLIENTES REGISTRADOS")

    # Si no existen clientes en el registro, informamos al usuario y finalizamos
    if not clientes:
        print("Todavía no hay clientes registrados.")
        return

    # Iteramos sobre la lista para imprimir la información estructurada de cada cliente
    for cliente in clientes:
        print(cliente.obtener_informacion())

    # Mostramos el conteo total de clientes activos en el sistema
    print("Total:", sistema.cantidad_clientes())


def menu_consultar_clientes(sistema: Sistema) -> None:
    """
    Muestra en pantalla la lista de todos los clientes registrados en el sistema.

    Función complementaria que ejecuta la consulta y listado de clientes
    invocando la lógica central de `menu_listar_clientes`.

    Args:
        sistema (Sistema): Instancia central del sistema que contiene los clientes.

    Returns:
        None
    """
    # Delegamos la visualización a la función principal de listado de clientes
    menu_listar_clientes(sistema)


# ==========================================================
# 5. CONSULTAR Y LISTAR SERVICIOS
# ==========================================================

def menu_listar_servicios(sistema: Sistema) -> None:
    """
    Consulta y despliega en pantalla todos los servicios registrados en el catálogo.

    Itera sobre la lista de servicios del sistema, mostrando la descripción
    específica de cada uno según su tipo polimórfico (sala, equipo o asesoría).

    Args:
        sistema (Sistema): Instancia central del sistema que contiene los servicios.

    Returns:
        None
    """
    # Obtenemos todos los servicios actualmente registrados en el sistema
    servicios = sistema.listar_servicios()

    print("\nSERVICIOS REGISTRADOS")

    # Verificamos si la lista está vacía para dar un mensaje claro
    if not servicios:
        print("Todavía no hay servicios registrados.")
        return

    # Recorremos cada servicio imprimiendo su descripción polimórfica detallada
    for servicio in servicios:
        print(servicio.describir_servicio())

    # Mostramos la métrica de cantidad total de servicios registrados
    print("Total:", sistema.cantidad_servicios())


def menu_consultar_servicios(sistema: Sistema) -> None:
    """
    Muestra en pantalla el catálogo completo de servicios disponibles en el sistema.

    Función complementaria que ejecuta la consulta y listado de servicios
    invocando la lógica central de `menu_listar_servicios`.

    Args:
        sistema (Sistema): Instancia central del sistema que contiene los servicios.

    Returns:
        None
    """
    # Delegamos la visualización a la función principal de listado de servicios
    menu_listar_servicios(sistema)


# ==========================================================
# 6. CONSULTAR Y LISTAR RESERVAS
# ==========================================================

def menu_listar_reservas(sistema: Sistema) -> None:
    """
    Consulta y muestra en pantalla todas las reservas registradas en el sistema.

    Presenta el estado y detalle de cada reserva (pendiente, procesada,
    confirmada o cancelada) junto con el total general.

    Args:
        sistema (Sistema): Instancia central del sistema que contiene las reservas.

    Returns:
        None
    """
    # Obtenemos el registro de todas las reservas almacenadas en memoria
    reservas = sistema.listar_reservas()

    print("\nRESERVAS REGISTRADAS")

    # Si no hay reservas registradas, notificamos al usuario
    if not reservas:
        print("Todavía no hay reservas registradas.")
        return

    # Presentamos la información completa de cada reserva individual
    for reserva in reservas:
        print(reserva.obtener_informacion())

    # Indicamos el total acumulado de reservas en el sistema
    print("Total:", sistema.cantidad_reservas())


def menu_consultar_reservas(sistema: Sistema) -> None:
    """
    Muestra en pantalla el histórico y estado de todas las reservas registradas.

    Función complementaria que ejecuta la consulta y listado de reservas
    invocando la lógica central de `menu_listar_reservas`.

    Args:
        sistema (Sistema): Instancia central del sistema que contiene las reservas.

    Returns:
        None
    """
    # Delegamos la visualización a la función principal de listado de reservas
    menu_listar_reservas(sistema)


# ==========================================================
# 7. PROCESAR RESERVA
# ==========================================================

def menu_procesar_reserva(sistema: Sistema) -> None:
    """
    Conduce el procesamiento financiero y cálculo del costo final de una reserva.

    Solicita al usuario el identificador de la reserva y los porcentajes de
    impuesto y descuento aplicables, actualizando su liquidación y estado a PROCESADA.

    Args:
        sistema (Sistema): Instancia central del sistema donde reside la reserva.

    Returns:
        None
    """
    print("\nPROCESAR RESERVA")

    # Solicitamos el código identificador de la reserva a procesar
    identificador = leer_texto(
        "Identificador de la reserva: "
    )

    # Capturamos el porcentaje de impuestos aplicable a la transacción (0 a 100%)
    impuesto = leer_porcentaje(
        "Porcentaje de impuesto (0 si no aplica): "
    )

    # Capturamos el porcentaje de descuento comercial a aplicar (0 a 100%)
    descuento = leer_porcentaje(
        "Porcentaje de descuento (0 si no aplica): "
    )

    # Ejecutamos el procesamiento financiero a través del método central del sistema
    sistema.procesar_reserva(
        identificador,
        impuesto,
        descuento
    )

    # Buscamos la reserva actualizada para mostrar la liquidación económica al usuario
    reserva = sistema.buscar_reserva_por_identificador(
        identificador
    )

    # Verificamos que la reserva exista tras procesarla y mostramos su información detallada
    if reserva is not None:
        print("\nReserva procesada correctamente.")
        print(reserva.obtener_informacion())


# ==========================================================
# 8. CONFIRMAR RESERVA
# ==========================================================

def menu_confirmar_reserva(sistema: Sistema) -> None:
    """
    Confirma una reserva previamente procesada, pasando su estado a CONFIRMADA.

    Valida con el sistema central que la reserva cumpla las precondiciones
    necesarias para quedar en firme.

    Args:
        sistema (Sistema): Instancia central del sistema que gestiona la reserva.

    Returns:
        None
    """
    print("\nCONFIRMAR RESERVA")

    # Solicitamos el identificador de la reserva que se desea confirmar
    identificador = leer_texto(
        "Identificador de la reserva: "
    )

    # Invocamos la confirmación en el sistema central
    sistema.confirmar_reserva(identificador)

    # Informamos al usuario que la confirmación se completó exitosamente
    print("Reserva confirmada correctamente.")


# ==========================================================
# 9. CANCELAR RESERVA
# ==========================================================

def menu_cancelar_reserva(sistema: Sistema) -> None:
    """
    Cancela una reserva existente y libera los recursos comprometidos.

    Invoca la cancelación en el sistema, lo cual cambia el estado a CANCELADA
    y restituye el stock en caso de servicios de alquiler de equipos.

    Args:
        sistema (Sistema): Instancia central del sistema que gestiona la reserva.

    Returns:
        None
    """
    print("\nCANCELAR RESERVA")

    # Solicitamos el identificador de la reserva que el usuario desea anular
    identificador = leer_texto(
        "Identificador de la reserva: "
    )

    # Ejecutamos la cancelación a través de las reglas de negocio del sistema
    sistema.cancelar_reserva(identificador)

    # Informamos al usuario que la cancelación fue efectuada con éxito
    print("Reserva cancelada correctamente.")


# ==========================================================
# 10. VER REGISTRO DE LOGS
# ==========================================================

def menu_ver_logs(sistema: Sistema | None = None) -> None:
    """
    Visualiza el registro histórico de eventos y errores del sistema (archivo de logs).

    Lee el archivo 'sistema.log' ubicado en la carpeta de logs del proyecto y
    despliega su contenido en la consola para tareas de auditoría y diagnóstico.

    Args:
        sistema (Sistema | None, opcional): Parámetro opcional para mantener compatibilidad
            de firma con el despachador de opciones del menú. Por defecto es None.

    Returns:
        None
    """
    print("\n" + "=" * 60)
    print("           REGISTRO DE EVENTOS DEL SISTEMA (LOGS)")
    print("=" * 60)

    # Comprobamos si el archivo físico de log existe en el almacenamiento
    if not ARCHIVO_LOG.exists():
        print("No se encontró el archivo de registro en la ruta esperada.")
        return

    # Leemos la totalidad de las entradas de log con codificación UTF-8
    contenido = ARCHIVO_LOG.read_text(encoding="utf-8").strip()

    # Si el archivo existe pero no tiene líneas de texto, notificamos al usuario
    if not contenido:
        print("El archivo de registro está vacío actualmente.")
        return

    # Obtenemos las líneas registradas y mostramos el resumen cuantitativo
    lineas = contenido.splitlines()
    print(f"Total de eventos registrados: {len(lineas)}\n")

    # Presentamos cada entrada de log preservando el formato temporal y nivel de severidad
    for linea in lineas:
        print(linea)


# ==========================================================
# PROGRAMA PRINCIPAL
# ==========================================================

def main() -> None:
    """
    Punto de entrada principal para la ejecución de la aplicación Software FJ.

    Inicializa la instancia central del sistema, registra el evento de inicio,
    construye el mapeo de opciones a funciones operativas (despachador) y mantiene
    el ciclo de vida interactivo por consola con captura y control de excepciones.

    Returns:
        None
    """
    # Instanciamos el controlador central que gestiona la información en memoria
    sistema = Sistema()

    # Registramos en el archivo de logs el inicio exitoso de la aplicación
    registrar_evento(
        "Aplicación principal de Software FJ iniciada."
    )

    # Mapeo de opciones de consola a sus respectivas funciones controladoras
    acciones = {
        "1": menu_registrar_cliente,
        "2": menu_registrar_servicio,
        "3": menu_crear_reserva,
        "4": menu_consultar_clientes,
        "5": menu_consultar_servicios,
        "6": menu_consultar_reservas,
        "7": menu_procesar_reserva,
        "8": menu_confirmar_reserva,
        "9": menu_cancelar_reserva,
        "10": menu_ver_logs
    }

    # Bucle interactivo principal que mantiene la aplicación activa
    while True:

        # Desplegamos las opciones del menú interactivo en cada ciclo
        mostrar_menu()

        # Solicitamos la selección del usuario eliminando espacios adicionales
        opcion = input(
            "Selecciona una opción: "
        ).strip()

        # Condición de salida del programa (opción 0)
        if opcion == "0":

            # Registramos en el log la finalización normal de la aplicación
            registrar_evento(
                "Aplicación principal de Software FJ finalizada."
            )

            # Mensaje de agradecimiento y cierre
            print("\nGracias por utilizar Software FJ.")
            break

        # Recuperamos la función controladora asociada a la opción digitada
        accion = acciones.get(opcion)

        # Si el usuario ingresó un valor fuera de las opciones válidas
        if accion is None:

            print("Opción incorrecta. Intenta nuevamente.")
            continue

        # Bloque de ejecución protegida para atrapar y registrar errores operacionales
        try:

            # Ejecutamos la acción seleccionada pasando la referencia del sistema
            accion(sistema)

        except (TypeError, ValueError) as error:

            # Registramos los errores de validación de datos en el sistema de logs
            registrar_error(
                f"Error en la operación del menú {opcion}",
                error
            )

            # Informamos de forma amigable al usuario sobre la causa del error
            print("\nNo se pudo completar la operación.")
            print("Detalle:", error)

            # Si el error contiene una causa original encadenada, la mostramos
            if error.__cause__ is not None:
                print("Causa original:", error.__cause__)

        except Exception as error:

            # Registramos cualquier error imprevisto para posterior análisis forense
            registrar_error(
                f"Error inesperado en el menú {opcion}",
                error
            )

            # Notificamos al usuario del problema sin colapsar la aplicación
            print("\nSe produjo un error inesperado.")
            print("Detalle:", error)

        # Pausa antes de redibujar el menú para que el usuario pueda leer los resultados
        input("\nPresiona ENTER para regresar al menú.")


if __name__ == "__main__":

    main()
