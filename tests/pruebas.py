
# =============================================
# PRUEBAS INICIALES DE ENTIDAD Y CLIENTE
# SOFTWARE FJ
# =============================================

from software_fj.entidades import Entidad, Cliente
from software_fj.sistema import Sistema
from software_fj.servicios import (
    Servicio,
    ServicioSala,
    ServicioEquipo,
    ServicioAsesoria
)
from software_fj.reservas import Reserva
from software_fj.excepciones import (
    RegistroDuplicadoError,
    ErrorProcesamientoReserva
)
from software_fj.registro import ARCHIVO_LOG
from software_fj.excepciones import OperacionNoPermitidaError
from software_fj.excepciones import RecursoNoDisponibleError
from datetime import datetime, timedelta

print("\n========== PRUEBA 1 ==========")
print("CREACIÓN DE UN CLIENTE")

cliente = Cliente(
    "CLI-001",
    "Andrés Suárez",
    "12345678",
    "andres@gmail.com",
    "+573001234567"
)

print(cliente.obtener_informacion())


print("\n========== PRUEBA 2 ==========")
print("MODIFICACIÓN DE UN CORREO")

cliente.correo = "nuevo@gmail.com"

print("Nuevo correo:", cliente.correo)


print("\n========== PRUEBA 3 ==========")
print("VALIDACIÓN DE DATOS INCORRECTOS")

try:
    cliente.correo = "correo-invalido"

except ValueError as error:
    print("Error controlado:", error)


print("\n========== PRUEBA 4 ==========")
print("VERIFICACIÓN DE CLASE ABSTRACTA")

try:
    Entidad("ENT-001")

except TypeError as error:
    print("Correcto: no se puede crear una Entidad directamente.")
    print("Detalle:", error)


print("\n========== RESULTADO ==========")
print("TODAS LAS PRUEBAS FINALIZARON")


# ==================================================
# PRUEBAS DEL ADMINISTRADOR DE CLIENTES
# ==================================================

print("\n========== PRUEBA 5 ==========")
print("REGISTRAR CLIENTES")

sistema = Sistema()

# Registrar el primer cliente.
sistema.registrar_cliente(cliente)

# Crear y registrar un segundo cliente.
cliente2 = Cliente(
    "CLI-002",
    "Carlos Pérez",
    "87654321",
    "carlos@gmail.com",
    "+573001112233"
)

sistema.registrar_cliente(cliente2)

print("Clientes registrados:", sistema.cantidad_clientes())


print("\n========== PRUEBA 6 ==========")
print("IMPEDIR DOCUMENTOS DUPLICADOS")

try:
    cliente3 = Cliente(
        "CLI-003",
        "María Gómez",
        "12345678",
        "maria@gmail.com",
        "+573009998877"
    )

    sistema.registrar_cliente(cliente3)

except ValueError as error:
    print("Error controlado:", error)


print("\n========== PRUEBA 7 ==========")
print("IMPEDIR IDENTIFICADORES DUPLICADOS")

try:
    cliente4 = Cliente(
        "CLI-001",
        "Pedro Ramírez",
        "99887766",
        "pedro@gmail.com",
        "+573008887766"
    )

    sistema.registrar_cliente(cliente4)

except ValueError as error:
    print("Error controlado:", error)


print("\n========== PRUEBA 8 ==========")
print("BUSCAR CLIENTE POR DOCUMENTO")

cliente_encontrado = sistema.buscar_cliente_por_documento(
    "87654321"
)

if cliente_encontrado is not None:
    print(cliente_encontrado.obtener_informacion())
else:
    print("Cliente no encontrado.")


print("\n========== PRUEBA 9 ==========")
print("MOSTRAR TODOS LOS CLIENTES")

for cliente_registrado in sistema.listar_clientes():
    print(cliente_registrado.obtener_informacion())


print("\n========== PRUEBA 10 ==========")
print("CONTAR CLIENTES")

print("Total de clientes:", sistema.cantidad_clientes())


print("\n========== RESULTADO ==========")
print("PRUEBAS DEL ADMINISTRADOR FINALIZADAS")


# ==========================================================
# PRUEBAS DE LOS SERVICIOS DE SOFTWARE FJ
# ==========================================================

print("\n========== PRUEBA 11 ==========")
print("CREAR LOS TRES SERVICIOS")

sala = ServicioSala(
    "SRV-001",
    "Sala de juntas A",
    12,
    50000
)

equipo = ServicioEquipo(
    "SRV-002",
    "Portatil Lenovo",
    100000,
    5
)

asesoria = ServicioAsesoria(
    "SRV-003",
    "Asesoria en programacion",
    "Desarrollo de software",
    80000
)

servicios = [sala, equipo, asesoria]

for servicio in servicios:
    print(servicio.describir_servicio())


print("\n========== PRUEBA 12 ==========")
print("COMPROBAR POLIMORFISMO")

for servicio in servicios:
    print(servicio.nombre)
    print("Costo por 2 unidades de tiempo:",
          servicio.calcular_costo(2))


print("\n========== PRUEBA 13 ==========")
print("CALCULAR COSTOS CON IMPUESTOS Y DESCUENTOS")

costo = sala.calcular_costo(
    2,
    impuesto=19,
    descuento=10,
    personas=5
)

print("Costo final de la sala:", costo)


print("\n========== PRUEBA 14 ==========")
print("VALIDAR CAPACIDAD DE UNA SALA")

try:
    sala.calcular_costo(2, personas=15)

except ValueError as error:
    print("Error controlado:", error)


print("\n========== PRUEBA 15 ==========")
print("VALIDAR EXISTENCIAS DE EQUIPOS")

try:
    equipo.calcular_costo(2, cantidad=10)

except ValueError as error:
    print("Error controlado:", error)


print("\n========== PRUEBA 16 ==========")
print("VALIDAR SERVICIO NO DISPONIBLE")

asesoria.disponible = False

try:
    asesoria.calcular_costo(2)

except ValueError as error:
    print("Error controlado:", error)


print("\n========== PRUEBA 17 ==========")
print("VERIFICAR CLASE ABSTRACTA SERVICIO")

try:
    Servicio(
        "SRV-004",
        "Servicio general",
        "Servicio de prueba"
    )

except TypeError as error:
    print("Correcto: Servicio es una clase abstracta.")
    print("Detalle:", error)


print("\n========== RESULTADO ==========")
print("PRUEBAS DE SERVICIOS FINALIZADAS")


# ==========================================================
# PRUEBAS DEL SISTEMA DE RESERVAS
# ==========================================================

print("\n========== PRUEBA 18 ==========")
print("CREAR Y PROCESAR UNA RESERVA")

reserva1 = Reserva(
    "RES-001",
    cliente,
    sala,
    2,
    personas=5
)

print(reserva1.obtener_informacion())

reserva1.procesar(
    impuesto=19,
    descuento=10
)

print("Costo calculado:", reserva1.costo_total)
print("Estado:", reserva1.estado)


print("\n========== PRUEBA 19 ==========")
print("CONFIRMAR UNA RESERVA")

reserva1.confirmar()

print("Reserva confirmada.")
print("Estado:", reserva1.estado)


print("\n========== PRUEBA 20 ==========")
print("IMPEDIR CONFIRMACION SIN PROCESAMIENTO")

reserva2 = Reserva(
    "RES-002",
    cliente2,
    sala,
    1,
    personas=3
)

try:
    reserva2.confirmar()

except ValueError as error:
    print("Error controlado:", error)


print("\n========== PRUEBA 21 ==========")
print("CANCELAR UNA RESERVA")

reserva2.cancelar()

print("Estado de la reserva:", reserva2.estado)


print("\n========== PRUEBA 22 ==========")
print("IMPEDIR RESERVA CON CAPACIDAD EXCEDIDA")

reserva3 = Reserva(
    "RES-003",
    cliente,
    sala,
    2,
    personas=20
)

try:
    reserva3.procesar()

except ValueError as error:
    print("Error controlado:", error)

print("Estado de la reserva:", reserva3.estado)


print("\n========== PRUEBA 23 ==========")
print("IMPEDIR PROCESAR UNA RESERVA CANCELADA")

reserva4 = Reserva(
    "RES-004",
    cliente2,
    equipo,
    2,
    cantidad=1
)

reserva4.cancelar()

try:
    reserva4.procesar()

except ValueError as error:
    print("Error controlado:", error)

print("Estado:", reserva4.estado)


print("\n========== RESULTADO ==========")
print("PRUEBAS DE RESERVAS FINALIZADAS")


# ==========================================================
# ETAPA 5: EXCEPCIONES PERSONALIZADAS Y LOGS
# ==========================================================

print("\n========== PRUEBA 24 ==========")
print("EXCEPCION PERSONALIZADA: CLIENTE DUPLICADO")

try:

    sistema.registrar_cliente(cliente)

except RegistroDuplicadoError as error:

    print("Excepción personalizada:", type(error).__name__)
    print("Mensaje:", error)


print("\n========== PRUEBA 25 ==========")
print("ENCADENAMIENTO DE EXCEPCIONES")

# La asesoría fue marcada como no disponible
# durante la prueba 16.

reserva5 = Reserva(
    "RES-005",
    cliente,
    asesoria,
    1
)

try:

    reserva5.procesar()

except ErrorProcesamientoReserva as error:

    print("Error principal:", type(error).__name__)
    print("Mensaje:", error)

    print(
        "Causa original:",
        type(error.__cause__).__name__
    )

    print("Detalle original:", error.__cause__)
# Restaurar la disponibilidad para las pruebas posteriores.
asesoria.disponible = True

print("\n========== PRUEBA 26 ==========")
print("VERIFICAR ARCHIVO LOG")

if ARCHIVO_LOG.exists():

    print("Archivo LOG encontrado:", ARCHIVO_LOG.name)

    contenido = ARCHIVO_LOG.read_text(
        encoding="utf-8"
    )

    cantidad_registros = len(
        [linea for linea in contenido.splitlines() if linea.strip()]
    )

    print("Cantidad de registros:", cantidad_registros)

    print("\nULTIMOS REGISTROS:")

    for linea in contenido.splitlines()[-8:]:
        print(linea)

else:

    print("No se encontró el archivo LOG.")


print("\n========== RESULTADO ==========")
print("PRUEBAS DE EXCEPCIONES Y LOGS FINALIZADAS")


# ==========================================================
# ETAPA 6: INTEGRACION DEL SISTEMA CENTRAL
# ==========================================================

print("\n========== PRUEBA 27 ==========")
print("REGISTRAR SERVICIOS EN EL SISTEMA")

sistema.registrar_servicio(sala)
sistema.registrar_servicio(equipo)
sistema.registrar_servicio(asesoria)

print("Servicios registrados:", sistema.cantidad_servicios())

for servicio in sistema.listar_servicios():
    print(servicio.describir_servicio())


print("\n========== PRUEBA 28 ==========")
print("CREAR RESERVA DESDE EL ADMINISTRADOR CENTRAL")

reserva_central = sistema.crear_reserva(
    "RES-100",
    "CLI-001",
    "SRV-001",
    2,
    personas=5
)

print(reserva_central.obtener_informacion())


print("\n========== PRUEBA 29 ==========")
print("IMPEDIR REGISTRO DE SERVICIOS DUPLICADOS")

try:

    servicio_duplicado = ServicioSala(
        "SRV-001",
        "Otra sala",
        10,
        40000
    )

    sistema.registrar_servicio(servicio_duplicado)

except RegistroDuplicadoError as error:

    print("Error controlado:", error)


print("\n========== PRUEBA 30 ==========")
print("IMPEDIR RESERVA CON CLIENTE NO REGISTRADO")

try:

    sistema.crear_reserva(
        "RES-101",
        "CLI-999",
        "SRV-001",
        2,
        personas=3
    )

except OperacionNoPermitidaError as error:

    print("Error controlado:", error)


print("\n========== PRUEBA 31 ==========")
print("PROCESAR Y CONFIRMAR DESDE EL SISTEMA CENTRAL")

sistema.procesar_reserva(
    "RES-100",
    impuesto=19,
    descuento=10
)

print("Costo:", reserva_central.costo_total)

sistema.confirmar_reserva("RES-100")

print("Estado:", reserva_central.estado)


print("\n========== PRUEBA 32 ==========")
print("CONSULTAR RESERVAS REGISTRADAS")

for reserva_registrada in sistema.listar_reservas():
    print(reserva_registrada.obtener_informacion())

print("Total de reservas:", sistema.cantidad_reservas())


print("\n========== PRUEBA 33 ==========")
print("CANCELAR RESERVA DESDE EL SISTEMA CENTRAL")

sistema.cancelar_reserva("RES-100")

print("Estado final:", reserva_central.estado)


print("\n========== RESULTADO ==========")
print("PRUEBAS DE INTEGRACION FINALIZADAS")


# ==========================================================
# ETAPA 7: CONTROL DE DISPONIBILIDAD
# ==========================================================

print("\n========== PRUEBA 34 ==========")
print("CREAR RESERVA CON FECHA Y HORA")

fecha_base = (
    datetime.now() + timedelta(days=5)
).replace(
    hour=10,
    minute=0,
    second=0,
    microsecond=0
)

reserva_horario1 = sistema.crear_reserva(
    "RES-200",
    "CLI-001",
    "SRV-001",
    2,
    personas=5,
    fecha_hora_inicio=fecha_base
)

print(reserva_horario1.obtener_informacion())


print("\n========== PRUEBA 35 ==========")
print("IMPEDIR CRUCE DE HORARIOS EN UNA SALA")

# Registrar y confirmar la primera reserva.
sistema.procesar_reserva("RES-200")
sistema.confirmar_reserva("RES-200")

# Crear otra reserva que comienza una hora después.
reserva_horario2 = sistema.crear_reserva(
    "RES-201",
    "CLI-002",
    "SRV-001",
    2,
    personas=4,
    fecha_hora_inicio=fecha_base + timedelta(hours=1)
)

sistema.procesar_reserva("RES-201")

try:

    sistema.confirmar_reserva("RES-201")

except RecursoNoDisponibleError as error:

    print("Conflicto detectado:", error)


print("Estado primera reserva:", reserva_horario1.estado)
print("Estado segunda reserva:", reserva_horario2.estado)


print("\n========== PRUEBA 36 ==========")
print("LIBERAR HORARIOS AL CANCELAR")

sistema.cancelar_reserva("RES-201")
sistema.cancelar_reserva("RES-200")

print("Primera reserva:", reserva_horario1.estado)
print("Segunda reserva:", reserva_horario2.estado)


print("\n========== PRUEBA 37 ==========")
print("DESCONTAR EXISTENCIAS AL CONFIRMAR UN ALQUILER")

print("Existencias iniciales:", equipo.existencias)

reserva_equipo = sistema.crear_reserva(
    "RES-300",
    "CLI-001",
    "SRV-002",
    2,
    cantidad=4,
    fecha_hora_inicio=fecha_base
)

sistema.procesar_reserva("RES-300")
sistema.confirmar_reserva("RES-300")

print("Equipos alquilados:", reserva_equipo.cantidad)
print("Existencias restantes:", equipo.existencias)


print("\n========== PRUEBA 38 ==========")
print("IMPEDIR ALQUILAR MAS EQUIPOS DE LOS DISPONIBLES")

reserva_equipo2 = sistema.crear_reserva(
    "RES-301",
    "CLI-002",
    "SRV-002",
    2,
    cantidad=2,
    fecha_hora_inicio=fecha_base + timedelta(days=3)
)

try:

    sistema.procesar_reserva("RES-301")

except ErrorProcesamientoReserva as error:

    print("Error controlado:", error)
    print("Causa original:", error.__cause__)


print("\n========== PRUEBA 39 ==========")
print("DEVOLVER EQUIPOS AL CANCELAR")

sistema.cancelar_reserva("RES-300")

print("Estado de la reserva:", reserva_equipo.estado)
print("Existencias recuperadas:", equipo.existencias)


print("\n========== RESULTADO ==========")
print("PRUEBAS DE DISPONIBILIDAD FINALIZADAS")
