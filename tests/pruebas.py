"""
Módulo de Pruebas Unitarias e Integración Progresiva - SOFTWARE FJ.

Este módulo contiene la suite integral de pruebas para validar el correcto
funcionamiento de todas las capas arquitectónicas del sistema 'SOFTWARE FJ'.
Las pruebas están diseñadas de manera secuencial y progresiva, permitiendo
verificar desde el comportamiento individual de las clases del modelo de
dominio hasta la integración completa mediante el controlador central.

Estructura de las pruebas contenidas en este módulo:
1. Pruebas de Entidad y Cliente (Pruebas 1 a 4):
   - Creación, encapsulamiento e inmutabilidad de identificadores.
   - Modificación de atributos mediante propiedades (@property y setters).
   - Validación rigurosa de formato y tipos de datos (control de errores).
   - Verificación del principio de abstracción en la clase base Entidad.

2. Pruebas del Administrador de Clientes (Pruebas 5 a 10):
   - Registro en memoria de clientes dentro del repositorio del sistema.
   - Prevención de duplicados por número de documento de identidad.
   - Prevención de duplicados por código identificador único.
   - Búsqueda, conteo y listado de los clientes almacenados.

3. Pruebas de los Servicios de Software FJ (Pruebas 11 a 17):
   - Instanciación de servicios derivados (Salas, Equipos y Asesorías).
   - Comprobación del polimorfismo mediante el cálculo dinámico de costos.
   - Aplicación de reglas financieras: recargo de impuestos y descuentos.
   - Validaciones de límites operativos: capacidad física, stock y estado.
   - Imposibilidad de instanciar directamente la clase abstracta Servicio.

4. Pruebas del Sistema de Reservas (Pruebas 18 a 23):
   - Ciclo de vida y transición de estados: PENDIENTE -> PROCESADA -> CONFIRMADA.
   - Restricciones de flujo: confirmación condicionada al cálculo de costos previo.
   - Cancelación de solicitudes y protección contra operaciones inválidas.

5. Pruebas de Excepciones Personalizadas y Auditoría (Pruebas 24 a 26):
   - Lanzamiento y captura de la jerarquía propia de excepciones de negocio.
   - Encadenamiento semántico de excepciones (raise ... from ...) y uso de __cause__.
   - Inspección física y verificación de registros en el archivo de auditoría (log).

6. Pruebas de Integración del Sistema Central (Pruebas 27 a 33):
   - Registro de catálogo de servicios mediante el orquestador central (Sistema).
   - Creación y gestión de reservas utilizando el patrón Fachada.
   - Control de integridad referencial: validación de existencia de clientes y servicios.
   - Confirmación, consulta y cancelación a través del sistema unificado.

7. Pruebas de Control de Disponibilidad y Concurrencia Temporal (Pruebas 34 a 39):
   - Programación de reservas con fecha y hora específicas.
   - Detección y bloqueo de solapamiento de horarios (cruces) en una misma sala.
   - Liberación de franjas horarias tras la cancelación de solicitudes.
   - Descuento atómico y restitución de stock físico en el alquiler de equipos.

Proyecto: SOFTWARE FJ - Sistema Integral de Gestión de Recursos.
Universidad Nacional Abierta y a Distancia (UNAD).
"""

# ==========================================================
# IMPORTACIONES DE MÓDULOS Y DEPENDENCIAS
# ==========================================================

# 1. Biblioteca estándar de Python: manejo de fechas y deltas temporales
from datetime import datetime, timedelta

# 2. Clases del dominio: entidades base y clientes
from software_fj.entidades import Entidad, Cliente

# 3. Servicios especializados ofrecidos por la empresa
from software_fj.servicios import (
    Servicio,
    ServicioSala,
    ServicioEquipo,
    ServicioAsesoria
)

# 4. Modelo de reservas y orquestador central del sistema
from software_fj.reservas import Reserva
from software_fj.sistema import Sistema

# 5. Sistema de auditoría y persistencia de eventos en disco
from software_fj.registro import ARCHIVO_LOG

# 6. Jerarquía de excepciones personalizadas de negocio
# Se unifican todas las excepciones en una única sentencia organizada alfabéticamente
from software_fj.excepciones import (
    ErrorProcesamientoReserva,
    OperacionNoPermitidaError,
    RecursoNoDisponibleError,
    RegistroDuplicadoError
)


# ==========================================================
# ETAPA 1: PRUEBAS INICIALES DE ENTIDAD Y CLIENTE
# ==========================================================

print("\n========== PRUEBA 1 ==========")
print("CREACIÓN DE UN CLIENTE")

# Instanciamos un objeto de la clase Cliente con datos personales válidos
# Los parámetros representan: identificador único, nombre completo, documento, correo y teléfono
cliente = Cliente(
    "CLI-001",
    "Andrés Suárez",
    "12345678",
    "andres@gmail.com",
    "+573001234567"
)

# Invocamos el método polimórfico obtener_informacion() para comprobar
# que todos los campos fueron formateados y asignados correctamente
print(cliente.obtener_informacion())


print("\n========== PRUEBA 2 ==========")
print("MODIFICACIÓN DE UN CORREO")

# Modificamos el correo electrónico utilizando el decorador @correo.setter
# El setter encapsula la validación sintáctica mediante expresión regular
cliente.correo = "nuevo@gmail.com"

# Verificamos que la propiedad almacena efectivamente el nuevo valor asignado
print("Nuevo correo:", cliente.correo)


print("\n========== PRUEBA 3 ==========")
print("VALIDACIÓN DE DATOS INCORRECTOS")

# Evaluamos la robustez del setter intentando asignar un correo sin formato válido
try:
    # Se pasa una cadena que carece del caracter '@' y dominio válido
    cliente.correo = "correo-invalido"

# Se espera que el setter intercepte el error y lance un ValueError explicativo
except ValueError as error:
    print("Error controlado:", error)


print("\n========== PRUEBA 4 ==========")
print("VERIFICACIÓN DE CLASE ABSTRACTA")

# Comprobamos que la clase base Entidad cumpla con el principio de abstracción
try:
    # Entidad hereda de ABC y posee métodos abstractos sin implementar,
    # por lo que Python debe rechazar su instanciación directa
    Entidad("ENT-001")

# La captura de TypeError confirma que el lenguaje protege la clase abstracta
except TypeError as error:
    print("Correcto: no se puede crear una Entidad directamente.")
    print("Detalle:", error)


print("\n========== RESULTADO ==========")
print("TODAS LAS PRUEBAS FINALIZARON")


# ==========================================================
# ETAPA 2: PRUEBAS DEL ADMINISTRADOR DE CLIENTES
# ==========================================================

print("\n========== PRUEBA 5 ==========")
print("REGISTRAR CLIENTES")

# Creamos una instancia del orquestador Sistema para gestionar colecciones de entidades
sistema = Sistema()

# Registramos el primer cliente creado previamente en el repositorio interno del sistema
sistema.registrar_cliente(cliente)

# Creamos un segundo cliente con identificador y documento únicos para ampliar el catálogo
cliente2 = Cliente(
    "CLI-002",
    "Carlos Pérez",
    "87654321",
    "carlos@gmail.com",
    "+573001112233"
)

# Almacenamos el segundo cliente en el sistema
sistema.registrar_cliente(cliente2)

# Comprobamos que el contador de clientes registrados refleje exactamente 2 elementos
print("Clientes registrados:", sistema.cantidad_clientes())


print("\n========== PRUEBA 6 ==========")
print("IMPEDIR DOCUMENTOS DUPLICADOS")

# Validamos la regla de negocio que prohíbe dos clientes con el mismo documento
try:
    # Se crea un tercer cliente con un documento idéntico al de cliente1 ("12345678")
    cliente3 = Cliente(
        "CLI-003",
        "María Gómez",
        "12345678",
        "maria@gmail.com",
        "+573009998877"
    )

    # El sistema debe rechazar el registro por colisión de documento de identidad
    sistema.registrar_cliente(cliente3)

# Capturamos el ValueError disparado por el validador de unicidad
except ValueError as error:
    print("Error controlado:", error)


print("\n========== PRUEBA 7 ==========")
print("IMPEDIR IDENTIFICADORES DUPLICADOS")

# Validamos la regla de integridad de clave primaria (identificador de cliente)
try:
    # Se intenta registrar un cliente con el identificador "CLI-001", ya asignado a cliente1
    cliente4 = Cliente(
        "CLI-001",
        "Pedro Ramírez",
        "99887766",
        "pedro@gmail.com",
        "+573008887766"
    )

    # El registro debe fallar impidiendo inconsistencias en las claves del diccionario
    sistema.registrar_cliente(cliente4)

# Capturamos la excepción que notifica la duplicidad del identificador
except ValueError as error:
    print("Error controlado:", error)


print("\n========== PRUEBA 8 ==========")
print("BUSCAR CLIENTE POR DOCUMENTO")

# Consultamos un cliente específico mediante su clave de negocio (número de documento)
cliente_encontrado = sistema.buscar_cliente_por_documento(
    "87654321"
)

# Validamos que la búsqueda haya retornado una instancia y no el valor None
if cliente_encontrado is not None:
    # Mostramos los datos formateados del cliente localizado exitosamente
    print(cliente_encontrado.obtener_informacion())
else:
    print("Cliente no encontrado.")


print("\n========== PRUEBA 9 ==========")
print("MOSTRAR TODOS LOS CLIENTES")

# Iteramos sobre la lista inmutable de clientes devuelta por el sistema
for cliente_registrado in sistema.listar_clientes():
    # Invocamos el método de información para auditar los clientes almacenados
    print(cliente_registrado.obtener_informacion())


print("\n========== PRUEBA 10 ==========")
print("CONTAR CLIENTES")

# Consultamos la cardinalidad total de clientes almacenados en la estructura interna
print("Total de clientes:", sistema.cantidad_clientes())


print("\n========== RESULTADO ==========")
print("PRUEBAS DEL ADMINISTRADOR FINALIZADAS")


# ==========================================================
# ETAPA 3: PRUEBAS DE LOS SERVICIOS DE SOFTWARE FJ
# ==========================================================

print("\n========== PRUEBA 11 ==========")
print("CREAR LOS TRES SERVICIOS")

# Instanciamos un servicio de alquiler de sala con capacidad para 12 personas y tarifa de 50.000
sala = ServicioSala(
    "SRV-001",
    "Sala de juntas A",
    12,
    50000
)

# Instanciamos un servicio de alquiler de equipos con precio base 100.000 y 5 unidades en stock
equipo = ServicioEquipo(
    "SRV-002",
    "Portatil Lenovo",
    100000,
    5
)

# Instanciamos una asesoría técnica especializada con tarifa por hora de 80.000
asesoria = ServicioAsesoria(
    "SRV-003",
    "Asesoria en programacion",
    "Desarrollo de software",
    80000
)

# Agrupamos los servicios heterogéneos en una lista para demostrar polimorfismo
servicios = [sala, equipo, asesoria]

# Recorremos la lista ejecutando el método describir_servicio() en cada subtipo
for servicio in servicios:
    print(servicio.describir_servicio())


print("\n========== PRUEBA 12 ==========")
print("COMPROBAR POLIMORFISMO")

# Demostramos que cada subtipo responde al mismo mensaje calcular_costo() con su propia lógica
for servicio in servicios:
    # Mostramos el nombre identificador del servicio
    print(servicio.nombre)
    # Calculamos el costo base para una duración estándar de 2 unidades de tiempo
    print("Costo por 2 unidades de tiempo:",
          servicio.calcular_costo(2))


print("\n========== PRUEBA 13 ==========")
print("CALCULAR COSTOS CON IMPUESTOS Y DESCUENTOS")

# Probamos la fórmula financiera de la sala aplicando 19% de IVA y 10% de descuento comercial
# La sala recibe también el parámetro adicional 'personas' para validar que no exceda el aforo
costo = sala.calcular_costo(
    2,
    impuesto=19,
    descuento=10,
    personas=5
)

# Mostramos el resultado del cálculo con los recargos y deducciones aplicados
print("Costo final de la sala:", costo)


print("\n========== PRUEBA 14 ==========")
print("VALIDAR CAPACIDAD DE UNA SALA")

# Evaluamos la restricción de aforo: intentar alojar 15 personas cuando la sala solo admite 12
try:
    sala.calcular_costo(2, personas=15)

# El método debe rechazar la operación lanzando ValueError al superar la capacidad máxima
except ValueError as error:
    print("Error controlado:", error)


print("\n========== PRUEBA 15 ==========")
print("VALIDAR EXISTENCIAS DE EQUIPOS")

# Evaluamos la restricción de inventario: solicitar 10 equipos cuando el stock disponible es 5
try:
    equipo.calcular_costo(2, cantidad=10)

# El cálculo debe abortar arrojando ValueError por falta de unidades físicas
except ValueError as error:
    print("Error controlado:", error)


print("\n========== PRUEBA 16 ==========")
print("VALIDAR SERVICIO NO DISPONIBLE")

# Modificamos el estado operativo del servicio para marcarlo como fuera de servicio
asesoria.disponible = False

# Intentamos solicitar el cálculo de un servicio marcado como inactivo
try:
    asesoria.calcular_costo(2)

# El sistema debe prohibir transacciones sobre servicios inactivos mediante ValueError
except ValueError as error:
    print("Error controlado:", error)


print("\n========== PRUEBA 17 ==========")
print("VERIFICAR CLASE ABSTRACTA SERVICIO")

# Validamos que la clase base Servicio mantenga su condición abstracta (no instanciable)
try:
    Servicio(
        "SRV-004",
        "Servicio general",
        "Servicio de prueba"
    )

# Python debe interceptar la instanciación directa arrojando un TypeError
except TypeError as error:
    print("Correcto: Servicio es una clase abstracta.")
    print("Detalle:", error)


print("\n========== RESULTADO ==========")
print("PRUEBAS DE SERVICIOS FINALIZADAS")


# ==========================================================
# ETAPA 4: PRUEBAS DEL SISTEMA DE RESERVAS
# ==========================================================

print("\n========== PRUEBA 18 ==========")
print("CREAR Y PROCESAR UNA RESERVA")

# Creamos una reserva directa vinculando cliente, servicio de sala, 2 horas y 5 asistentes
# El estado inicial de la reserva debe ser 'PENDIENTE'
reserva1 = Reserva(
    "RES-001",
    cliente,
    sala,
    2,
    personas=5
)

# Verificamos los metadatos iniciales de la solicitud de reserva
print(reserva1.obtener_informacion())

# Procesamos la reserva aplicando los porcentajes fiscales y descuentos comerciales
# Este método calcula el costo total y realiza la transición de estado a 'PROCESADA'
reserva1.procesar(
    impuesto=19,
    descuento=10
)

# Comprobamos el costo liquidado y el nuevo estado operativo de la reserva
print("Costo calculado:", reserva1.costo_total)
print("Estado:", reserva1.estado)


print("\n========== PRUEBA 19 ==========")
print("CONFIRMAR UNA RESERVA")

# Confirmamos formalmente la reserva que ya se encuentra en estado 'PROCESADA'
reserva1.confirmar()

# Notificamos el éxito de la confirmación y mostramos el estado final 'CONFIRMADA'
print("Reserva confirmada.")
print("Estado:", reserva1.estado)


print("\n========== PRUEBA 20 ==========")
print("IMPEDIR CONFIRMACION SIN PROCESAMIENTO")

# Creamos una nueva reserva en estado inicial 'PENDIENTE'
reserva2 = Reserva(
    "RES-002",
    cliente2,
    sala,
    1,
    personas=3
)

# Intentamos saltar el paso de procesamiento llamando directamente a confirmar()
try:
    reserva2.confirmar()

# La máquina de estados debe lanzar ValueError al no permitir confirmar reservas pendientes
except ValueError as error:
    print("Error controlado:", error)


print("\n========== PRUEBA 21 ==========")
print("CANCELAR UNA RESERVA")

# Cancelamos la reserva no confirmada para liberar la solicitud
reserva2.cancelar()

# Comprobamos que el atributo estado de la reserva haya cambiado a 'CANCELADA'
print("Estado de la reserva:", reserva2.estado)


print("\n========== PRUEBA 22 ==========")
print("IMPEDIR RESERVA CON CAPACIDAD EXCEDIDA")

# Instanciamos una reserva solicitando una sala para 20 personas (la capacidad es 12)
reserva3 = Reserva(
    "RES-003",
    cliente,
    sala,
    2,
    personas=20
)

# Al procesar la reserva, la lógica interna delega la validación de aforo al servicio
try:
    reserva3.procesar()

# Se intercepta el ValueError generado por exceder la capacidad permitida
except ValueError as error:
    print("Error controlado:", error)

# Verificamos que el estado de la reserva permanezca en 'PENDIENTE' al fallar el cálculo
print("Estado de la reserva:", reserva3.estado)


print("\n========== PRUEBA 23 ==========")
print("IMPEDIR PROCESAR UNA RESERVA CANCELADA")

# Instanciamos una reserva asociada a un servicio de equipo
reserva4 = Reserva(
    "RES-004",
    cliente2,
    equipo,
    2,
    cantidad=1
)

# Procedemos a cancelar la reserva de forma anticipada
reserva4.cancelar()

# Intentamos procesar una reserva que ya ostenta el estado terminal 'CANCELADA'
try:
    reserva4.procesar()

# El sistema debe rechazar el procesamiento sobre solicitudes ya canceladas
except ValueError as error:
    print("Error controlado:", error)

# Comprobamos que el estado inalterado continúe siendo 'CANCELADA'
print("Estado:", reserva4.estado)


print("\n========== RESULTADO ==========")
print("PRUEBAS DE RESERVAS FINALIZADAS")


# ==========================================================
# ETAPA 5: EXCEPCIONES PERSONALIZADAS Y LOGS
# ==========================================================

print("\n========== PRUEBA 24 ==========")
print("EXCEPCION PERSONALIZADA: CLIENTE DUPLICADO")

# Evaluamos la jerarquía propia de errores intentando registrar nuevamente al primer cliente
try:
    # 'cliente' ya existe en el sistema desde la Prueba 5
    sistema.registrar_cliente(cliente)

# Capturamos la excepción semántica específica en lugar de un error genérico
except RegistroDuplicadoError as error:
    # Verificamos la identidad de la clase de excepción levantada
    print("Excepción personalizada:", type(error).__name__)
    print("Mensaje:", error)


print("\n========== PRUEBA 25 ==========")
print("ENCADENAMIENTO DE EXCEPCIONES")

# La asesoría técnica fue marcada como no disponible (disponible = False) en la Prueba 16
# Creamos una reserva vinculada a dicho servicio inactivo
reserva5 = Reserva(
    "RES-005",
    cliente,
    asesoria,
    1
)

# Intentamos procesar la reserva para provocar un fallo por recurso no disponible
try:
    reserva5.procesar()

# El sistema debe envolver el error original en un ErrorProcesamientoReserva semántico
except ErrorProcesamientoReserva as error:
    # Informamos el tipo y mensaje del error de alto nivel
    print("Error principal:", type(error).__name__)
    print("Mensaje:", error)

    # Inspeccionamos el atributo __cause__ generado mediante la cláusula 'raise ... from ...'
    print(
        "Causa original:",
        type(error.__cause__).__name__
    )
    print("Detalle original:", error.__cause__)

# Restauramos el estado disponible de la asesoría para no afectar las pruebas posteriores
asesoria.disponible = True


print("\n========== PRUEBA 26 ==========")
print("VERIFICAR ARCHIVO LOG")

# Comprobamos la existencia física del archivo de auditoría gestionado por pathlib.Path
if ARCHIVO_LOG.exists():
    print("Archivo LOG encontrado:", ARCHIVO_LOG.name)

    # Leemos la totalidad del archivo en codificación estándar UTF-8
    contenido = ARCHIVO_LOG.read_text(
        encoding="utf-8"
    )

    # Calculamos la cantidad de entradas no vacías registradas en la bitácora
    cantidad_registros = len(
        [linea for linea in contenido.splitlines() if linea.strip()]
    )

    print("Cantidad de registros:", cantidad_registros)

    print("\nULTIMOS REGISTROS:")
    # Extraemos y mostramos las últimas 8 líneas para verificar la trazabilidad de eventos
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

# Registramos el catálogo de los tres servicios en el repositorio central del Sistema
sistema.registrar_servicio(sala)
sistema.registrar_servicio(equipo)
sistema.registrar_servicio(asesoria)

# Verificamos que el inventario global contabilice exactamente 3 servicios activos
print("Servicios registrados:", sistema.cantidad_servicios())

# Listamos las fichas descriptivas de los servicios registrados mediante el orquestador
for servicio in sistema.listar_servicios():
    print(servicio.describir_servicio())


print("\n========== PRUEBA 28 ==========")
print("CREAR RESERVA DESDE EL ADMINISTRADOR CENTRAL")

# Creamos una reserva utilizando el método orquestador de la clase fachada Sistema
# El método busca internamente al cliente y al servicio por sus respectivos identificadores
reserva_central = sistema.crear_reserva(
    "RES-100",
    "CLI-001",
    "SRV-001",
    2,
    personas=5
)

# Imprimimos la información de la reserva generada centralizadamente
print(reserva_central.obtener_informacion())


print("\n========== PRUEBA 29 ==========")
print("IMPEDIR REGISTRO DE SERVICIOS DUPLICADOS")

# Intentamos registrar un nuevo servicio utilizando un identificador existente ("SRV-001")
try:
    servicio_duplicado = ServicioSala(
        "SRV-001",
        "Otra sala",
        10,
        40000
    )

    sistema.registrar_servicio(servicio_duplicado)

# El sistema debe interceptar la colisión de claves arrojando RegistroDuplicadoError
except RegistroDuplicadoError as error:
    print("Error controlado:", error)


print("\n========== PRUEBA 30 ==========")
print("IMPEDIR RESERVA CON CLIENTE NO REGISTRADO")

# Evaluamos la integridad referencial intentando crear una reserva para un cliente inexistente
try:
    sistema.crear_reserva(
        "RES-101",
        "CLI-999",
        "SRV-001",
        2,
        personas=3
    )

# El sistema detecta la ausencia del cliente y genera OperacionNoPermitidaError
except OperacionNoPermitidaError as error:
    print("Error controlado:", error)


print("\n========== PRUEBA 31 ==========")
print("PROCESAR Y CONFIRMAR DESDE EL SISTEMA CENTRAL")

# Procesamos financieramente la reserva delegando la operación al sistema central
sistema.procesar_reserva(
    "RES-100",
    impuesto=19,
    descuento=10
)

# Inspeccionamos el costo total liquidado en la reserva
print("Costo:", reserva_central.costo_total)

# Confirmamos la reserva mediante el método de coordinación del Sistema
sistema.confirmar_reserva("RES-100")

# Verificamos que el estado de la reserva se encuentre formalmente en 'CONFIRMADA'
print("Estado:", reserva_central.estado)


print("\n========== PRUEBA 32 ==========")
print("CONSULTAR RESERVAS REGISTRADAS")

# Iteramos sobre el catálogo de reservas registradas para consultar su detalle
for reserva_registrada in sistema.listar_reservas():
    print(reserva_registrada.obtener_informacion())

# Comprobamos la cantidad total de reservas administradas por la instancia del Sistema
print("Total de reservas:", sistema.cantidad_reservas())


print("\n========== PRUEBA 33 ==========")
print("CANCELAR RESERVA DESDE EL SISTEMA CENTRAL")

# Cancelamos la reserva utilizando el identificador mediante la interfaz del Sistema
sistema.cancelar_reserva("RES-100")

# Confirmamos que el estado terminal de la reserva sea 'CANCELADA'
print("Estado final:", reserva_central.estado)


print("\n========== RESULTADO ==========")
print("PRUEBAS DE INTEGRACION FINALIZADAS")


# ==========================================================
# ETAPA 7: CONTROL DE DISPONIBILIDAD Y CONCURRENCIA
# ==========================================================

print("\n========== PRUEBA 34 ==========")
print("CREAR RESERVA CON FECHA Y HORA")

# Establecemos una fecha base futura fija (5 días a partir de hoy a las 10:00:00 exactas)
fecha_base = (
    datetime.now() + timedelta(days=5)
).replace(
    hour=10,
    minute=0,
    second=0,
    microsecond=0
)

# Creamos una reserva especificando la franja horaria de inicio (10:00 a 12:00 por 2 horas)
reserva_horario1 = sistema.crear_reserva(
    "RES-200",
    "CLI-001",
    "SRV-001",
    2,
    personas=5,
    fecha_hora_inicio=fecha_base
)

# Mostramos los datos de la reserva incluyendo su intervalo temporal
print(reserva_horario1.obtener_informacion())


print("\n========== PRUEBA 35 ==========")
print("IMPEDIR CRUCE DE HORARIOS EN UNA SALA")

# Procesamos y confirmamos la primera reserva para ocupar formalmente la sala de 10:00 a 12:00
sistema.procesar_reserva("RES-200")
sistema.confirmar_reserva("RES-200")

# Creamos una segunda reserva para la misma sala que inicia a las 11:00 (solapamiento horario)
reserva_horario2 = sistema.crear_reserva(
    "RES-201",
    "CLI-002",
    "SRV-001",
    2,
    personas=4,
    fecha_hora_inicio=fecha_base + timedelta(hours=1)
)

# Procesamos la segunda reserva exitosamente
sistema.procesar_reserva("RES-201")

# Al intentar confirmar la segunda reserva, el algoritmo de detección de solapamientos
# debe identificar que la sala ya está comprometida en ese rango temporal
try:
    sistema.confirmar_reserva("RES-201")

# El sistema protege la integridad del calendario arrojando RecursoNoDisponibleError
except RecursoNoDisponibleError as error:
    print("Conflicto detectado:", error)

# Verificamos que la primera reserva siga 'CONFIRMADA' y la segunda permanezca en 'PROCESADA'
print("Estado primera reserva:", reserva_horario1.estado)
print("Estado segunda reserva:", reserva_horario2.estado)


print("\n========== PRUEBA 36 ==========")
print("LIBERAR HORARIOS AL CANCELAR")

# Cancelamos ambas reservas para liberar el horario previamente ocupado
sistema.cancelar_reserva("RES-201")
sistema.cancelar_reserva("RES-200")

# Verificamos que ambas solicitudes hayan pasado formalmente a estado 'CANCELADA'
print("Primera reserva:", reserva_horario1.estado)
print("Segunda reserva:", reserva_horario2.estado)


print("\n========== PRUEBA 37 ==========")
print("DESCONTAR EXISTENCIAS AL CONFIRMAR UN ALQUILER")

# Consultamos las existencias iniciales en inventario del equipo (5 unidades)
print("Existencias iniciales:", equipo.existencias)

# Creamos una reserva para alquilar 4 unidades de portátiles
reserva_equipo = sistema.crear_reserva(
    "RES-300",
    "CLI-001",
    "SRV-002",
    2,
    cantidad=4,
    fecha_hora_inicio=fecha_base
)

# Procesamos la solicitud liquidando los importes
sistema.procesar_reserva("RES-300")

# Al confirmar la reserva de equipos, el sistema descuenta atómicamente el stock físico
sistema.confirmar_reserva("RES-300")

# Verificamos la cantidad alquilada y que las existencias restantes se hayan reducido a 1
print("Equipos alquilados:", reserva_equipo.cantidad)
print("Existencias restantes:", equipo.existencias)


print("\n========== PRUEBA 38 ==========")
print("IMPEDIR ALQUILAR MAS EQUIPOS DE LOS DISPONIBLES")

# Intentamos crear una segunda reserva para 2 equipos (solo queda 1 disponible en stock)
reserva_equipo2 = sistema.crear_reserva(
    "RES-301",
    "CLI-002",
    "SRV-002",
    2,
    cantidad=2,
    fecha_hora_inicio=fecha_base + timedelta(days=3)
)

# El procesamiento debe fallar porque las existencias físicas actuales no satisfacen la solicitud
try:
    sistema.procesar_reserva("RES-301")

# Capturamos el error de alto nivel y mostramos la causa técnica encadenada
except ErrorProcesamientoReserva as error:
    print("Error controlado:", error)
    print("Causa original:", error.__cause__)


print("\n========== PRUEBA 39 ==========")
print("DEVOLVER EQUIPOS AL CANCELAR")

# Al cancelar la reserva 'RES-300', el sistema debe reintegrar los 4 equipos al inventario
sistema.cancelar_reserva("RES-300")

# Verificamos que el estado sea 'CANCELADA' y las existencias hayan regresado a su total inicial (5)
print("Estado de la reserva:", reserva_equipo.estado)
print("Existencias recuperadas:", equipo.existencias)


print("\n========== RESULTADO ==========")
print("PRUEBAS DE DISPONIBILIDAD FINALIZADAS")
