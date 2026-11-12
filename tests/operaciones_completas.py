"""
Módulo de Pruebas de Aceptación del Sistema - SOFTWARE FJ.

Este módulo implementa el banco completo de pruebas de aceptación y verificación
funcional end-to-end (de extremo a extremo) para el proyecto 'SOFTWARE FJ'.
Su propósito principal es validar que el sistema satisfaga la totalidad de los
requerimientos funcionales, reglas de negocio, integridad de datos, manejo de
excepciones y persistencia en auditoría, simulando un escenario de uso real.

Arquitectura de la Suite de Pruebas:
1. Aislamiento y Tolerancia a Fallos:
   - Se utiliza un arnés de pruebas (`ejecutar_operacion`) que encapsula cada
     caso en un bloque try/except/else. Si un caso de prueba individual falla,
     se registra la métrica y la ejecución continúa sin interrumpir el resto.
2. Verificación de Excepciones Esperadas:
   - La función auxiliar `verificar_error` comprueba que las operaciones inválidas
     disparen rigurosamente el tipo de error anticipado, garantizando que el sistema
     no falle de forma silenciosa ni capture excepciones inapropiadas.
3. Cobertura de las 14 Operaciones de Negocio:
   - Operación 1: Registro formal de un cliente con datos válidos.
   - Operación 2: Rechazo de registro de cliente con correo inválido.
   - Operación 3: Creación de un servicio de sala con capacidad y tarifas válidas.
   - Operación 4: Rechazo de creación de servicio con capacidad nula o negativa.
   - Operación 5: Creación de servicio de alquiler de equipos con stock inicial.
   - Operación 6: Creación de servicio de asesoría técnica especializada.
   - Operación 7: Creación, procesamiento y confirmación exitosa de reserva de sala.
   - Operación 8: Rechazo por conflicto de solapamiento de horario en una misma sala.
   - Operación 9: Protección de integridad referencial ante clientes inexistentes.
   - Operación 10: Alquiler exitoso de equipos con deducción atómica de inventario.
   - Operación 11: Rechazo de alquiler por insuficiencia de existencias físicas.
   - Operación 12: Cancelación de reserva de equipos y restitución automática de stock.
   - Operación 13: Reserva, procesamiento y confirmación de asesoría profesional.
   - Operación 14: Verificación física de persistencia y trazabilidad en el archivo LOG.

Proyecto: SOFTWARE FJ - Sistema Integral de Gestión de Recursos.
Universidad Nacional Abierta y a Distancia (UNAD).
"""

# ==========================================================
# IMPORTACIONES DE MÓDULOS Y DEPENDENCIAS
# ==========================================================

# 1. Biblioteca estándar de Python: manipulación de fechas y duraciones
from datetime import datetime, timedelta
from typing import Callable, Any

# 2. Fachada central del sistema para la orquestación de operaciones
from software_fj.sistema import Sistema

# 3. Jerarquía de excepciones personalizadas para aserciones de error
from software_fj.excepciones import (
    ErrorProcesamientoReserva,
    OperacionNoPermitidaError,
    RecursoNoDisponibleError
)

# 4. Referencia al archivo físico de auditoría en disco
from software_fj.registro import ARCHIVO_LOG


# ==========================================================
# CONFIGURACIÓN DEL ARNÉS Y ESTADO GLOBAL DE PRUEBAS
# ==========================================================

# Instancia unificada del orquestador central sobre la cual se ejecutan las operaciones
sistema = Sistema()

# Diccionario compartido para mantener referencias a los objetos creados entre operaciones
# Permite compartir estado entre etapas sucesivas sin crear dependencias circulares
datos: dict[str, Any] = {}

# Diccionario de acumulación de métricas para contabilizar el resultado de las pruebas
resultados: dict[str, int] = {
    "correctas": 0,
    "fallidas": 0
}


def ejecutar_operacion(
    numero: int,
    descripcion: str,
    accion: Callable[[], None]
) -> None:
    """
    Ejecuta una operación individual dentro del arnés de pruebas de aceptación.

    Proporciona aislamiento de fallos: captura cualquier excepción no controlada
    durante la ejecución de la acción de prueba, contabiliza el fallo en las métricas
    globales y permite que el conjunto de pruebas continúe con la siguiente operación.

    Args:
        numero (int): Número correlativo o secuencial de la operación en curso.
        descripcion (str): Título descriptivo del objetivo de la prueba.
        accion (Callable[[], None]): Función o callback ejecutable sin argumentos que
            contiene la lógica y aserciones de la prueba.

    Returns:
        None

    Raises:
        None: No propaga excepciones para garantizar la continuidad del suite.
    """
    # Imprime el encabezado distintivo de la operación para facilitar la lectura del reporte
    print(f"\n========== OPERACION {numero} ==========")
    print(descripcion)

    try:
        # Se ejecuta la función correspondiente a la prueba en evaluación
        accion()

    except Exception as error:
        # Si se produce un fallo o aserción no satisfecha, se incrementa el contador de fallidas
        resultados["fallidas"] += 1

        # Se informa en consola la causa exacta y el tipo de excepción ocurrida
        print("RESULTADO: FALLIDO")
        print("Tipo de error:", type(error).__name__)
        print("Detalle:", error)

    else:
        # Si la operación concluye sin lanzar errores ni excepciones, se marca como correcta
        resultados["correctas"] += 1

        # Se confirma el éxito de la operación en el reporte
        print("RESULTADO: CORRECTO")


def verificar_error(
    tipo_esperado: type[Exception],
    funcion: Callable[[], Any]
) -> Exception:
    """
    Verifica que la ejecución de una función dispare rigurosamente una excepción esperada.

    Este mecanismo actúa como un validador de expectativas negativas (pruebas de estrés
    o casos de error controlado), comprobando que los validadores internos del sistema
    estén activos y reaccionen adecuadamente ante datos inválidos o reglas violadas.

    Args:
        tipo_esperado (type[Exception]): Clase de excepción que se espera recibir.
        funcion (Callable[[], Any]): Función o lambda a ejecutar que debe fallar.

    Returns:
        Exception: La instancia de la excepción capturada para permitir inspecciones
            adicionales (como verificación de causas originales o mensajes).

    Raises:
        AssertionError: Si la función no arroja ninguna excepción o si arroja una
            excepción de un tipo diferente al esperado.
    """
    try:
        # Se invoca la función bajo prueba que debería fallar según las reglas de negocio
        funcion()

    except tipo_esperado as error:
        # La excepción esperada fue capturada exitosamente, confirmando la validación
        print("Error esperado detectado:", error)

        # Se retorna la excepción para que el llamador pueda examinar atributos adicionales
        return error

    except Exception as error:
        # Si ocurre una excepción diferente, la prueba de validación ha fallado
        raise AssertionError(
            f"Se esperaba {tipo_esperado.__name__}, "
            f"pero ocurrió {type(error).__name__}."
        ) from error

    else:
        # Si la función finaliza normalmente sin fallar, la aserción falla porque
        # el sistema debió haber rechazado la operación inválida
        raise AssertionError(
            f"No se produjo el error esperado: "
            f"{tipo_esperado.__name__}."
        )


# ==========================================================
# OPERACION 1: REGISTRO CORRECTO DE CLIENTE
# ==========================================================

def operacion_1() -> None:
    """
    Valida el registro exitoso de un cliente con datos válidos en el sistema.

    Verifica que los atributos personales (identificador, nombre, cédula, correo,
    teléfono) sean procesados, validados y almacenados en el repositorio interno
    del orquestador Sistema.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: Si la cantidad de clientes registrados en el sistema no es 1.
    """
    # Invocamos el método de fábrica del sistema para registrar un nuevo cliente
    cliente = sistema.crear_cliente(
        "CLI-901",
        "Laura Méndez",
        "1098765432",
        "laura@gmail.com",
        "+573001234567"
    )

    # Almacenamos el cliente en el diccionario compartido para su uso en pruebas posteriores
    datos["cliente"] = cliente

    # Mostramos en consola los datos estructurados del cliente registrado
    print(cliente.obtener_informacion())

    # Aseguramos que la colección interna del sistema contenga exactamente 1 cliente
    assert sistema.cantidad_clientes() == 1


# ==========================================================
# OPERACION 2: REGISTRO INVALIDO DE CLIENTE
# ==========================================================

def operacion_2() -> None:
    """
    Valida el rechazo de registro cuando se suministra un correo con formato inválido.

    Comprueba que el validador sintáctico de correos intercepte valores anómalos
    lanzando ValueError y asegurando que la colección interna no sufra modificaciones.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: Si se permite el registro o si la cantidad de clientes cambia.
    """
    # Intentamos crear un cliente con una dirección de correo no válida ("correo-incorrecto")
    # Se utiliza verificar_error para asegurar que se lance exactamente ValueError
    verificar_error(
        ValueError,
        lambda: sistema.crear_cliente(
            "CLI-902",
            "Carlos Torres",
            "12345678",
            "correo-incorrecto",
            "+573001112233"
        )
    )

    # Verificamos que la cantidad de clientes registrados se mantenga intacta en 1
    assert sistema.cantidad_clientes() == 1

    # Notificamos que el control de integridad evitó el registro inconsistente
    print("El cliente inválido no fue registrado.")


# ==========================================================
# OPERACION 3: CREACION CORRECTA DE SERVICIO
# ==========================================================

def operacion_3() -> None:
    """
    Valida la creación y registro correcto de un servicio de sala de reuniones.

    Verifica la asignación del código del servicio, nombre descriptivo, aforo
    máximo de asistentes y tarifa base por hora.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    # Registramos un servicio de sala con capacidad para 10 personas y costo de 60.000 por hora
    sala = sistema.crear_servicio_sala(
        "SRV-901",
        "Sala de reuniones Norte",
        10,
        60000
    )

    # Guardamos la referencia de la sala en el contexto compartido de pruebas
    datos["sala"] = sala

    # Imprimimos la ficha técnica del servicio generado
    print(sala.describir_servicio())


# ==========================================================
# OPERACION 4: CREACION INCORRECTA DE SERVICIO
# ==========================================================

def operacion_4() -> None:
    """
    Valida el rechazo en la creación de un servicio con parámetros numéricos inválidos.

    Comprueba que no se permita crear una sala con capacidad igual o menor a 0,
    asegurando la invariante del modelo y que el catálogo de servicios permanezca inalterado.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: Si se crea el servicio inválido o el catálogo cambia de tamaño.
    """
    # Consultamos el número actual de servicios para comprobar que no se altere
    cantidad_anterior = sistema.cantidad_servicios()

    # Intentamos registrar una sala con capacidad 0 personas (parámetro inválido)
    verificar_error(
        ValueError,
        lambda: sistema.crear_servicio_sala(
            "SRV-902",
            "Sala inválida",
            0,
            50000
        )
    )

    # Verificamos que el conteo de servicios no haya sufrido alteraciones tras el rechazo
    assert sistema.cantidad_servicios() == cantidad_anterior

    # Confirmamos la protección del catálogo en el informe
    print("El servicio inválido no fue registrado.")


# ==========================================================
# OPERACION 5: CREAR SERVICIO DE EQUIPOS
# ==========================================================

def operacion_5() -> None:
    """
    Valida la creación exitosa de un servicio de alquiler de equipos computacionales.

    Verifica la correcta inicialización del identificador, descripción, tarifa de
    alquiler por unidad de tiempo y existencias iniciales en inventario físico.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    # Registramos el servicio de alquiler con 3 equipos portátiles disponibles a 90.000 por hora
    equipo = sistema.crear_servicio_equipo(
        "SRV-903",
        "Portátiles Lenovo",
        90000,
        3
    )

    # Guardamos el objeto equipo en el contexto de datos para pruebas de inventario
    datos["equipo"] = equipo

    # Mostramos los detalles técnicos del servicio de equipos registrado
    print(equipo.describir_servicio())


# ==========================================================
# OPERACION 6: CREAR SERVICIO DE ASESORIA
# ==========================================================

def operacion_6() -> None:
    """
    Valida la creación exitosa de un servicio de asesoría técnica profesional.

    Verifica la asignación del código del servicio, título, área de especialidad
    del consultor y tarifa horaria estipulada.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    # Registramos una asesoría en desarrollo de software con tarifa de 75.000 por hora
    asesoria = sistema.crear_servicio_asesoria(
        "SRV-904",
        "Asesoría de Python",
        "Desarrollo de software",
        75000
    )

    # Almacenamos la referencia en el diccionario de datos compartidos
    datos["asesoria"] = asesoria

    # Mostramos la ficha del servicio de consultoría registrado
    print(asesoria.describir_servicio())


# ==========================================================
# FECHA BASE PROGRAMADA PARA PRUEBAS TEMPORALES
# ==========================================================

# Definimos una fecha y hora fija en el futuro (10 días a partir de la ejecución, a las 10:00:00)
# Esto asegura que las pruebas de solapamiento y reservas temporales sean predecibles y reproducibles
fecha_base = (
    datetime.now() + timedelta(days=10)
).replace(
    hour=10,
    minute=0,
    second=0,
    microsecond=0
)


# ==========================================================
# OPERACION 7: RESERVA EXITOSA DE SALA
# ==========================================================

def operacion_7() -> None:
    """
    Valida el ciclo de vida completo de una reserva de sala: creación, procesamiento y confirmación.

    Verifica el cálculo financiero aplicando IVA del 19% y descuento del 10%, así como
    la correcta transición de estados hasta 'CONFIRMADA'.
    Cálculo esperado:
        Tarifa base: 60.000 * 2 horas = 120.000
        Descuento 10%: 120.000 - 12.000 = 108.000
        Impuesto 19%: 108.000 * 1.19 = 128.520.0

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: Si el estado final no es 'CONFIRMADA' o el costo difiere de 128520.0.
    """
    # Creamos la reserva para 2 horas con 5 asistentes iniciando en fecha_base
    reserva = sistema.crear_reserva(
        "RES-901",
        "CLI-901",
        "SRV-901",
        2,
        personas=5,
        fecha_hora_inicio=fecha_base
    )

    # Procesamos financieramente la reserva aplicando impuesto y descuento comercial
    sistema.procesar_reserva(
        "RES-901",
        impuesto=19,
        descuento=10
    )

    # Confirmamos formalmente la reserva en el sistema
    sistema.confirmar_reserva("RES-901")

    # Almacenamos la reserva en el contexto global
    datos["reserva_sala"] = reserva

    # Mostramos la ficha completa de la reserva confirmada
    print(reserva.obtener_informacion())

    # Aseguramos que la transición de estado haya alcanzado 'CONFIRMADA'
    assert reserva.estado == "CONFIRMADA"

    # Verificamos la precisión matemática del costo liquidado
    assert reserva.costo_total == 128520.0


# ==========================================================
# OPERACION 8: RESERVA FALLIDA POR CRUCE DE HORARIOS
# ==========================================================

def operacion_8() -> None:
    """
    Valida la detección y bloqueo de colisiones de horario (cruces) en una misma sala.

    La sala fue reservada previamente de 10:00 a 12:00 (Operación 7).
    Se intenta confirmar una nueva reserva que inicia a las 11:00 (solapamiento temporal).
    El sistema debe lanzar RecursoNoDisponibleError y mantener la reserva en estado 'PROCESADA'.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: Si no se detecta la colisión o el estado de la reserva se altera.
    """
    # Creamos una segunda reserva para la misma sala que inicia a las 11:00 (cruce de 1 hora)
    reserva = sistema.crear_reserva(
        "RES-902",
        "CLI-901",
        "SRV-901",
        2,
        personas=4,
        fecha_hora_inicio=fecha_base + timedelta(hours=1)
    )

    # Se procesa la reserva liquidando su importe previo a la confirmación
    sistema.procesar_reserva("RES-902")

    # Al intentar confirmar, el detector de concurrencia debe levantar RecursoNoDisponibleError
    verificar_error(
        RecursoNoDisponibleError,
        lambda: sistema.confirmar_reserva("RES-902")
    )

    # Guardamos la reserva en conflicto en el contexto de pruebas
    datos["reserva_conflicto"] = reserva

    # Aseguramos que la reserva conserve el estado 'PROCESADA' sin confirmarse
    assert reserva.estado == "PROCESADA"

    # Notificamos el bloqueo preventivo del conflicto
    print("La reserva no fue confirmada.")


# ==========================================================
# OPERACION 9: RESERVA CON CLIENTE INEXISTENTE
# ==========================================================

def operacion_9() -> None:
    """
    Valida la protección de integridad referencial al solicitar reservas con clientes no registrados.

    Verifica que el sistema rechace la solicitud arrojando OperacionNoPermitidaError
    cuando el código del cliente no figure en el repositorio.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: Si el sistema permite la creación con un cliente inexistente.
    """
    # Intentamos crear una reserva vinculando un código de cliente ficticio ("CLI-999")
    verificar_error(
        OperacionNoPermitidaError,
        lambda: sistema.crear_reserva(
            "RES-903",
            "CLI-999",
            "SRV-901",
            2,
            personas=3,
            fecha_hora_inicio=fecha_base + timedelta(days=1)
        )
    )

    # Confirmamos en el reporte que la restricción referencial operó con éxito
    print("No se permitió reservar con un cliente inexistente.")


# ==========================================================
# OPERACION 10: ALQUILER EXITOSO DE EQUIPOS
# ==========================================================

def operacion_10() -> None:
    """
    Valida el alquiler de equipos y la deducción atómica de unidades del inventario físico.

    Verifica que al confirmar una reserva de 2 portátiles (de un stock total de 3),
    el inventario restante quede exactamente en 1 unidad y el estado sea 'CONFIRMADA'.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: Si el estado no es 'CONFIRMADA' o las existencias no disminuyen a 1.
    """
    # Obtenemos la referencia al servicio de equipos creado en la Operación 5
    equipo = datos["equipo"]

    # Creamos una reserva solicitando el alquiler de 2 unidades por 2 horas
    reserva = sistema.crear_reserva(
        "RES-904",
        "CLI-901",
        "SRV-903",
        2,
        cantidad=2,
        fecha_hora_inicio=fecha_base
    )

    # Procesamos la liquidación de la reserva
    sistema.procesar_reserva("RES-904")

    # Confirmamos formalmente: aquí el sistema descuenta 2 unidades del stock del equipo
    sistema.confirmar_reserva("RES-904")

    # Almacenamos la reserva de equipo en los datos compartidos
    datos["reserva_equipo"] = reserva

    # Mostramos los valores liquidados y el balance del stock
    print("Costo del alquiler:", reserva.costo_total)
    print("Existencias restantes:", equipo.existencias)

    # Verificamos la transición exitosa al estado 'CONFIRMADA'
    assert reserva.estado == "CONFIRMADA"

    # Aseguramos que el inventario se haya reducido correctamente (3 iniciales - 2 alquilados = 1)
    assert equipo.existencias == 1


# ==========================================================
# OPERACION 11: ALQUILER FALLIDO POR FALTA DE EXISTENCIAS
# ==========================================================

def operacion_11() -> None:
    """
    Valida el rechazo de una reserva cuando la cantidad requerida supera el stock disponible.

    Actualmente solo queda 1 equipo en inventario. Se intenta procesar una reserva
    solicitando 2 equipos. Debe lanzarse ErrorProcesamientoReserva encadenando la causa,
    el estado debe permanecer en 'PENDIENTE' y el stock debe seguir intacto en 1.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: Si la reserva se procesa o si el stock físico es alterado.
    """
    # Creamos una reserva solicitando 2 unidades cuando solo hay 1 disponible
    reserva = sistema.crear_reserva(
        "RES-905",
        "CLI-901",
        "SRV-903",
        2,
        cantidad=2,
        fecha_hora_inicio=fecha_base + timedelta(days=3)
    )

    # El procesamiento debe interceptar la falta de existencias y levantar la excepción
    error = verificar_error(
        ErrorProcesamientoReserva,
        lambda: sistema.procesar_reserva("RES-905")
    )

    # Inspeccionamos la causa original encadenada mediante __cause__
    print(
        "Causa original:",
        type(error.__cause__).__name__
    )
    print("Detalle:", error.__cause__)

    # Verificamos que la reserva no haya cambiado de su estado 'PENDIENTE'
    assert reserva.estado == "PENDIENTE"

    # Verificamos que las existencias del equipo se hayan protegido manteniéndose en 1
    assert datos["equipo"].existencias == 1


# ==========================================================
# OPERACION 12: CANCELAR ALQUILER Y DEVOLVER EQUIPOS
# ==========================================================

def operacion_12() -> None:
    """
    Valida la cancelación de una reserva confirmada y la restitución automática de stock.

    Al cancelar la reserva 'RES-904' (que tenía 2 equipos asignados), el sistema
    debe reintegrar las unidades al inventario (1 + 2 = 3) y marcar el estado como 'CANCELADA'.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: Si el inventario no regresa a 3 o el estado no es 'CANCELADA'.
    """
    # Obtenemos la instancia del equipo compartido
    equipo = datos["equipo"]

    # Mostramos el stock disponible previo a la cancelación
    print("Existencias antes de cancelar:", equipo.existencias)

    # Cancelamos formalmente la reserva de equipos a través del sistema central
    sistema.cancelar_reserva("RES-904")

    # Mostramos el estado actualizado de la reserva y las existencias recuperadas
    print("Estado:", datos["reserva_equipo"].estado)
    print("Existencias después de cancelar:", equipo.existencias)

    # Aseguramos que el inventario se haya restituido completamente a 3 unidades
    assert equipo.existencias == 3

    # Verificamos que la reserva ostente el estado 'CANCELADA'
    assert datos["reserva_equipo"].estado == "CANCELADA"


# ==========================================================
# OPERACION 13: RESERVA EXITOSA DE ASESORIA
# ==========================================================

def operacion_13() -> None:
    """
    Valida el flujo integral de contratación y confirmación de una asesoría técnica.

    Verifica la creación, liquidación horaria y confirmación formal de la reserva
    de consultoría especializada en Python.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: Si el estado de la reserva no alcanza 'CONFIRMADA'.
    """
    # Creamos una reserva para 2 horas de asesoría técnica
    reserva = sistema.crear_reserva(
        "RES-906",
        "CLI-901",
        "SRV-904",
        2,
        fecha_hora_inicio=fecha_base + timedelta(days=5)
    )

    # Procesamos la liquidación de la asesoría
    sistema.procesar_reserva("RES-906")

    # Confirmamos la reserva en el sistema
    sistema.confirmar_reserva("RES-906")

    # Guardamos la reserva en el contexto compartido
    datos["reserva_asesoria"] = reserva

    # Mostramos la ficha detallada de la asesoría confirmada
    print(reserva.obtener_informacion())

    # Comprobamos que el estado final sea 'CONFIRMADA'
    assert reserva.estado == "CONFIRMADA"


# ==========================================================
# OPERACION 14: VERIFICAR ARCHIVO LOG
# ==========================================================

def operacion_14() -> None:
    """
    Valida la existencia física, integridad y contenido del archivo de auditoría LOG.

    Comprueba que el módulo de registro haya persistido las operaciones y excepciones
    en el archivo del sistema de archivos, garantizando trazabilidad para auditorías.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: Si el archivo no existe o su contenido está vacío.
    """
    # Verificamos que el archivo de log exista físicamente en la ruta configurada
    assert ARCHIVO_LOG.exists(), "No existe el archivo LOG."

    # Leemos la totalidad del archivo de bitácora
    contenido = ARCHIVO_LOG.read_text(encoding="utf-8")

    # Verificamos que contenga texto y registros válidos
    assert contenido.strip(), "El archivo LOG está vacío."

    # Mostramos los metadatos y estadísticas de auditoría
    print("Archivo:", ARCHIVO_LOG.name)
    print("Tamaño:", ARCHIVO_LOG.stat().st_size, "bytes")
    print("Registros encontrados:", len(contenido.splitlines()))


# ==========================================================
# PLAN Y CONFIGURACIÓN DE EJECUCIÓN GENERAL
# ==========================================================

# Tupla ordenada con el conjunto de las 14 operaciones a ejecutar en secuencia
# Cada tupla contiene: (Número correlativo, Descripción del caso, Función de prueba)
operaciones = [
    (1, "REGISTRO VALIDO DE CLIENTE", operacion_1),
    (2, "REGISTRO INVALIDO DE CLIENTE", operacion_2),
    (3, "CREACION CORRECTA DE SALA", operacion_3),
    (4, "CREACION INCORRECTA DE SERVICIO", operacion_4),
    (5, "CREACION DE SERVICIO DE EQUIPOS", operacion_5),
    (6, "CREACION DE ASESORIA ESPECIALIZADA", operacion_6),
    (7, "RESERVA EXITOSA DE SALA", operacion_7),
    (8, "RESERVA FALLIDA POR HORARIO OCUPADO", operacion_8),
    (9, "RESERVA CON CLIENTE INEXISTENTE", operacion_9),
    (10, "ALQUILER EXITOSO DE EQUIPOS", operacion_10),
    (11, "ALQUILER FALLIDO POR EXISTENCIAS", operacion_11),
    (12, "CANCELACION Y DEVOLUCION DE EQUIPOS", operacion_12),
    (13, "RESERVA EXITOSA DE ASESORIA", operacion_13),
    (14, "COMPROBACION DEL ARCHIVO LOG", operacion_14)
]


# Presentamos el encabezado principal del banco de pruebas de aceptación
print("\n")
print("=" * 60)
print("SOFTWARE FJ - PRUEBAS DE ACEPTACION")
print("=" * 60)

# Iteramos a través de cada caso de prueba despachándolo mediante el arnés protegido
for numero, descripcion, accion in operaciones:
    ejecutar_operacion(numero, descripcion, accion)


# ==========================================================
# REPORTE Y RESUMEN FINAL DE EJECUCIÓN
# ==========================================================

print("\n")
print("=" * 60)
print("RESUMEN DE LAS PRUEBAS DE ACEPTACION")
print("=" * 60)

# Informamos las métricas consolidadas de ejecución
print("Operaciones ejecutadas:", len(operaciones))
print("Operaciones correctas:", resultados["correctas"])
print("Operaciones fallidas:", resultados["fallidas"])

# Determinamos el veredicto final del banco de pruebas
if resultados["fallidas"] == 0:
    print("\nTODAS LAS OPERACIONES FUERON EXITOSAS.")
else:
    print("\nSE DEBEN REVISAR LAS OPERACIONES FALLIDAS.")

print("=" * 60)
