
# ==========================================================
# SOFTWARE FJ
# PRUEBAS DE ACEPTACION DEL PROYECTO
# ==========================================================

from datetime import datetime, timedelta

from software_fj.sistema import Sistema

from software_fj.excepciones import (
    ErrorProcesamientoReserva,
    OperacionNoPermitidaError,
    RecursoNoDisponibleError
)

from software_fj.registro import ARCHIVO_LOG


# ==========================================================
# CONFIGURACION DE LAS PRUEBAS
# ==========================================================

sistema = Sistema()

datos = {}

resultados = {
    "correctas": 0,
    "fallidas": 0
}


def ejecutar_operacion(numero, descripcion, accion):
    """
    Ejecuta cada operación independientemente.
    Si una prueba falla, las siguientes pueden continuar.
    """

    print(f"\n========== OPERACION {numero} ==========")
    print(descripcion)

    try:
        accion()

    except Exception as error:

        resultados["fallidas"] += 1

        print("RESULTADO: FALLIDO")
        print("Tipo de error:", type(error).__name__)
        print("Detalle:", error)

    else:

        resultados["correctas"] += 1

        print("RESULTADO: CORRECTO")


def verificar_error(tipo_esperado, funcion):
    """
    Comprueba que una operación genere el error esperado.
    """

    try:
        funcion()

    except tipo_esperado as error:

        print("Error esperado detectado:", error)

        return error

    except Exception as error:

        raise AssertionError(
            f"Se esperaba {tipo_esperado.__name__}, "
            f"pero ocurrió {type(error).__name__}."
        ) from error

    else:

        raise AssertionError(
            f"No se produjo el error esperado: "
            f"{tipo_esperado.__name__}."
        )


# ==========================================================
# OPERACION 1: REGISTRO CORRECTO DE CLIENTE
# ==========================================================

def operacion_1():

    cliente = sistema.crear_cliente(
        "CLI-901",
        "Laura Méndez",
        "1098765432",
        "laura@gmail.com",
        "+573001234567"
    )

    datos["cliente"] = cliente

    print(cliente.obtener_informacion())

    assert sistema.cantidad_clientes() == 1


# ==========================================================
# OPERACION 2: REGISTRO INVALIDO DE CLIENTE
# ==========================================================

def operacion_2():

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

    assert sistema.cantidad_clientes() == 1

    print("El cliente inválido no fue registrado.")


# ==========================================================
# OPERACION 3: CREACION CORRECTA DE SERVICIO
# ==========================================================

def operacion_3():

    sala = sistema.crear_servicio_sala(
        "SRV-901",
        "Sala de reuniones Norte",
        10,
        60000
    )

    datos["sala"] = sala

    print(sala.describir_servicio())


# ==========================================================
# OPERACION 4: CREACION INCORRECTA DE SERVICIO
# ==========================================================

def operacion_4():

    cantidad_anterior = sistema.cantidad_servicios()

    verificar_error(
        ValueError,
        lambda: sistema.crear_servicio_sala(
            "SRV-902",
            "Sala inválida",
            0,
            50000
        )
    )

    assert sistema.cantidad_servicios() == cantidad_anterior

    print("El servicio inválido no fue registrado.")


# ==========================================================
# OPERACION 5: CREAR SERVICIO DE EQUIPOS
# ==========================================================

def operacion_5():

    equipo = sistema.crear_servicio_equipo(
        "SRV-903",
        "Portátiles Lenovo",
        90000,
        3
    )

    datos["equipo"] = equipo

    print(equipo.describir_servicio())


# ==========================================================
# OPERACION 6: CREAR SERVICIO DE ASESORIA
# ==========================================================

def operacion_6():

    asesoria = sistema.crear_servicio_asesoria(
        "SRV-904",
        "Asesoría de Python",
        "Desarrollo de software",
        75000
    )

    datos["asesoria"] = asesoria

    print(asesoria.describir_servicio())


# ==========================================================
# FECHA BASE PARA LAS RESERVAS
# ==========================================================

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

def operacion_7():

    reserva = sistema.crear_reserva(
        "RES-901",
        "CLI-901",
        "SRV-901",
        2,
        personas=5,
        fecha_hora_inicio=fecha_base
    )

    sistema.procesar_reserva(
        "RES-901",
        impuesto=19,
        descuento=10
    )

    sistema.confirmar_reserva("RES-901")

    datos["reserva_sala"] = reserva

    print(reserva.obtener_informacion())

    assert reserva.estado == "CONFIRMADA"

    assert reserva.costo_total == 128520.0


# ==========================================================
# OPERACION 8: RESERVA FALLIDA POR CRUCE DE HORARIOS
# ==========================================================

def operacion_8():

    reserva = sistema.crear_reserva(
        "RES-902",
        "CLI-901",
        "SRV-901",
        2,
        personas=4,
        fecha_hora_inicio=fecha_base + timedelta(hours=1)
    )

    sistema.procesar_reserva("RES-902")

    verificar_error(
        RecursoNoDisponibleError,
        lambda: sistema.confirmar_reserva("RES-902")
    )

    datos["reserva_conflicto"] = reserva

    assert reserva.estado == "PROCESADA"

    print("La reserva no fue confirmada.")


# ==========================================================
# OPERACION 9: RESERVA CON CLIENTE INEXISTENTE
# ==========================================================

def operacion_9():

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

    print("No se permitió reservar con un cliente inexistente.")


# ==========================================================
# OPERACION 10: ALQUILER EXITOSO DE EQUIPOS
# ==========================================================

def operacion_10():

    equipo = datos["equipo"]

    reserva = sistema.crear_reserva(
        "RES-904",
        "CLI-901",
        "SRV-903",
        2,
        cantidad=2,
        fecha_hora_inicio=fecha_base
    )

    sistema.procesar_reserva("RES-904")

    sistema.confirmar_reserva("RES-904")

    datos["reserva_equipo"] = reserva

    print("Costo del alquiler:", reserva.costo_total)

    print("Existencias restantes:", equipo.existencias)

    assert reserva.estado == "CONFIRMADA"

    assert equipo.existencias == 1


# ==========================================================
# OPERACION 11: ALQUILER FALLIDO POR FALTA DE EXISTENCIAS
# ==========================================================

def operacion_11():

    reserva = sistema.crear_reserva(
        "RES-905",
        "CLI-901",
        "SRV-903",
        2,
        cantidad=2,
        fecha_hora_inicio=fecha_base + timedelta(days=3)
    )

    error = verificar_error(
        ErrorProcesamientoReserva,
        lambda: sistema.procesar_reserva("RES-905")
    )

    print(
        "Causa original:",
        type(error.__cause__).__name__
    )

    print("Detalle:", error.__cause__)

    assert reserva.estado == "PENDIENTE"

    assert datos["equipo"].existencias == 1


# ==========================================================
# OPERACION 12: CANCELAR ALQUILER Y DEVOLVER EQUIPOS
# ==========================================================

def operacion_12():

    equipo = datos["equipo"]

    print("Existencias antes de cancelar:", equipo.existencias)

    sistema.cancelar_reserva("RES-904")

    print("Estado:", datos["reserva_equipo"].estado)

    print("Existencias después de cancelar:", equipo.existencias)

    assert equipo.existencias == 3

    assert datos["reserva_equipo"].estado == "CANCELADA"


# ==========================================================
# OPERACION 13: RESERVA EXITOSA DE ASESORIA
# ==========================================================

def operacion_13():

    reserva = sistema.crear_reserva(
        "RES-906",
        "CLI-901",
        "SRV-904",
        2,
        fecha_hora_inicio=fecha_base + timedelta(days=5)
    )

    sistema.procesar_reserva("RES-906")

    sistema.confirmar_reserva("RES-906")

    datos["reserva_asesoria"] = reserva

    print(reserva.obtener_informacion())

    assert reserva.estado == "CONFIRMADA"


# ==========================================================
# OPERACION 14: VERIFICAR ARCHIVO LOG
# ==========================================================

def operacion_14():

    assert ARCHIVO_LOG.exists(), "No existe el archivo LOG."

    contenido = ARCHIVO_LOG.read_text(encoding="utf-8")

    assert contenido.strip(), "El archivo LOG está vacío."

    print("Archivo:", ARCHIVO_LOG.name)

    print("Tamaño:", ARCHIVO_LOG.stat().st_size, "bytes")

    print("Registros encontrados:", len(contenido.splitlines()))


# ==========================================================
# EJECUCION GENERAL
# ==========================================================

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


print("\n")
print("=" * 60)
print("SOFTWARE FJ - PRUEBAS DE ACEPTACION")
print("=" * 60)

for numero, descripcion, accion in operaciones:

    ejecutar_operacion(numero, descripcion, accion)


# ==========================================================
# RESUMEN FINAL
# ==========================================================

print("\n")
print("=" * 60)
print("RESUMEN DE LAS PRUEBAS DE ACEPTACION")
print("=" * 60)

print("Operaciones ejecutadas:", len(operaciones))
print("Operaciones correctas:", resultados["correctas"])
print("Operaciones fallidas:", resultados["fallidas"])

if resultados["fallidas"] == 0:

    print("\nTODAS LAS OPERACIONES FUERON EXITOSAS.")

else:

    print("\nSE DEBEN REVISAR LAS OPERACIONES FALLIDAS.")

print("=" * 60)
