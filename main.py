
# ==========================================================
# SOFTWARE FJ
# SISTEMA INTEGRAL DE GESTION
# PROGRAMA PRINCIPAL
# ==========================================================

from datetime import datetime
import math

from software_fj.sistema import Sistema

from software_fj.servicios import (
    ServicioSala,
    ServicioEquipo,
    ServicioAsesoria
)

from software_fj.registro import (
    registrar_evento,
    registrar_error
)


# ==========================================================
# FUNCIONES PARA LEER DATOS
# ==========================================================

def leer_texto(mensaje: str) -> str:

    while True:

        valor = input(mensaje).strip()

        if valor:
            return valor

        print("El dato no puede estar vacío.")


def leer_entero(
    mensaje: str,
    minimo: int = 1
) -> int:

    while True:

        try:

            valor = int(input(mensaje))

            if valor < minimo:
                print(f"El valor mínimo permitido es {minimo}.")
                continue

            return valor

        except ValueError:
            print("Introduce un número entero válido.")


def leer_decimal(
    mensaje: str,
    minimo: float = 0.01
) -> float:

    while True:

        try:

            valor = float(
                input(mensaje).replace(",", ".")
            )

            if not math.isfinite(valor) or valor < minimo:
                print(
                    f"Introduce un número mayor o igual a {minimo}."
                )
                continue

            return valor

        except ValueError:
            print("Introduce un número válido.")


def leer_porcentaje(mensaje: str) -> float:

    while True:

        try:

            valor = float(
                input(mensaje).replace(",", ".")
            )

            if not math.isfinite(valor) or not 0 <= valor <= 100:
                print("El porcentaje debe estar entre 0 y 100.")
                continue

            return valor

        except ValueError:
            print("Introduce un porcentaje válido.")


def leer_fecha_hora() -> datetime | None:

    print("Formato de fecha: AAAA-MM-DD HH:MM")

    valor = input(
        "Fecha y hora de inicio (Enter = ahora): "
    ).strip()

    if not valor:
        return None

    try:

        fecha = datetime.strptime(
            valor,
            "%Y-%m-%d %H:%M"
        )

        return fecha

    except ValueError as error:

        raise ValueError(
            "Fecha incorrecta. Ejemplo: 2026-12-15 10:00"
        ) from error


# ==========================================================
# MOSTRAR MENU PRINCIPAL
# ==========================================================

def mostrar_menu() -> None:

    print("\n")
    print("=" * 60)
    print("                  SOFTWARE FJ")
    print("=" * 60)

    print(" SISTEMA INTEGRAL DE GESTION")
    print(" Clientes | Servicios | Reservas")

    print("-" * 60)

    print(" 1. Registrar cliente")
    print(" 2. Registrar servicio")
    print(" 3. Crear reserva")
    print(" 4. Consultar clientes")
    print(" 5. Consultar servicios")
    print(" 6. Consultar reservas")
    print(" 7. Procesar reserva")
    print(" 8. Confirmar reserva")
    print(" 9. Cancelar reserva")
    print(" 0. Salir")

    print("=" * 60)


# ==========================================================
# 1. REGISTRAR CLIENTE
# ==========================================================

def menu_registrar_cliente(sistema: Sistema) -> None:

    print("\nREGISTRO DE CLIENTE")

    identificador = leer_texto("Identificador: ")
    nombre = leer_texto("Nombre completo: ")
    documento = leer_texto("Documento: ")
    correo = leer_texto("Correo electrónico: ")
    telefono = leer_texto("Teléfono: ")

    cliente = sistema.crear_cliente(
        identificador,
        nombre,
        documento,
        correo,
        telefono
    )

    print("\nCliente registrado correctamente.")
    print(cliente.obtener_informacion())


# ==========================================================
# 2. REGISTRAR SERVICIO
# ==========================================================

def menu_registrar_servicio(sistema: Sistema) -> None:

    print("\nREGISTRO DE SERVICIOS")

    print("1. Reservas de salas")
    print("2. Alquiler de equipos")
    print("3. Asesorías especializadas")

    opcion = input("Selecciona el tipo de servicio: ").strip()

    identificador = leer_texto("Identificador: ")
    nombre = leer_texto("Nombre del servicio: ")

    if opcion == "1":

        capacidad = leer_entero("Capacidad de la sala: ")
        precio = leer_decimal("Precio por hora: ")

        servicio = sistema.crear_servicio_sala(
            identificador,
            nombre,
            capacidad,
            precio
        )

    elif opcion == "2":

        precio = leer_decimal("Precio por día: ")
        existencias = leer_entero("Cantidad de equipos: ")

        servicio = sistema.crear_servicio_equipo(
            identificador,
            nombre,
            precio,
            existencias
        )

    elif opcion == "3":

        especialidad = leer_texto("Especialidad: ")
        precio = leer_decimal("Precio por hora: ")

        servicio = sistema.crear_servicio_asesoria(
            identificador,
            nombre,
            especialidad,
            precio
        )

    else:

        raise ValueError("Tipo de servicio no válido.")

    print("\nServicio registrado correctamente.")
    print(servicio.describir_servicio())


# ==========================================================
# 3. CREAR RESERVA
# ==========================================================

def menu_crear_reserva(sistema: Sistema) -> None:

    print("\nCREACION DE RESERVA")

    print("\nCLIENTES DISPONIBLES:")

    for cliente in sistema.listar_clientes():
        print(
            cliente.identificador,
            "-",
            cliente.nombre
        )

    identificador = leer_texto("\nID de la reserva: ")

    identificador_cliente = leer_texto(
        "ID del cliente: "
    )

    print("\nSERVICIOS DISPONIBLES:")

    for servicio in sistema.listar_servicios():
        print(
            servicio.identificador,
            "-",
            servicio.describir_servicio()
        )

    identificador_servicio = leer_texto(
        "\nID del servicio: "
    )

    servicio = sistema.buscar_servicio_por_identificador(
        identificador_servicio
    )

    if servicio is None:
        raise ValueError("El servicio seleccionado no existe.")

    duracion = leer_decimal(
        "Duración (horas o días, según el servicio): "
    )

    cantidad = 1
    personas = 1

    if isinstance(servicio, ServicioSala):

        personas = leer_entero(
            "Número de personas: "
        )

    elif isinstance(servicio, ServicioEquipo):

        cantidad = leer_entero(
            "Cantidad de equipos que desea alquilar: "
        )

    fecha_inicio = leer_fecha_hora()

    reserva = sistema.crear_reserva(
        identificador,
        identificador_cliente,
        identificador_servicio,
        duracion,
        cantidad,
        personas,
        fecha_inicio
    )

    print("\nReserva creada correctamente.")
    print(reserva.obtener_informacion())


# ==========================================================
# 4. CONSULTAR CLIENTES
# ==========================================================

def menu_consultar_clientes(sistema: Sistema) -> None:

    clientes = sistema.listar_clientes()

    print("\nCLIENTES REGISTRADOS")

    if not clientes:
        print("Todavía no hay clientes registrados.")
        return

    for cliente in clientes:
        print(cliente.obtener_informacion())

    print("Total:", sistema.cantidad_clientes())


# ==========================================================
# 5. CONSULTAR SERVICIOS
# ==========================================================

def menu_consultar_servicios(sistema: Sistema) -> None:

    servicios = sistema.listar_servicios()

    print("\nSERVICIOS REGISTRADOS")

    if not servicios:
        print("Todavía no hay servicios registrados.")
        return

    for servicio in servicios:
        print(servicio.describir_servicio())

    print("Total:", sistema.cantidad_servicios())


# ==========================================================
# 6. CONSULTAR RESERVAS
# ==========================================================

def menu_consultar_reservas(sistema: Sistema) -> None:

    reservas = sistema.listar_reservas()

    print("\nRESERVAS REGISTRADAS")

    if not reservas:
        print("Todavía no hay reservas registradas.")
        return

    for reserva in reservas:
        print(reserva.obtener_informacion())

    print("Total:", sistema.cantidad_reservas())


# ==========================================================
# 7. PROCESAR RESERVA
# ==========================================================

def menu_procesar_reserva(sistema: Sistema) -> None:

    print("\nPROCESAR RESERVA")

    identificador = leer_texto(
        "Identificador de la reserva: "
    )

    impuesto = leer_porcentaje(
        "Porcentaje de impuesto (0 si no aplica): "
    )

    descuento = leer_porcentaje(
        "Porcentaje de descuento (0 si no aplica): "
    )

    sistema.procesar_reserva(
        identificador,
        impuesto,
        descuento
    )

    reserva = sistema.buscar_reserva_por_identificador(
        identificador
    )

    print("\nReserva procesada correctamente.")
    print(reserva.obtener_informacion())


# ==========================================================
# 8. CONFIRMAR RESERVA
# ==========================================================

def menu_confirmar_reserva(sistema: Sistema) -> None:

    print("\nCONFIRMAR RESERVA")

    identificador = leer_texto(
        "Identificador de la reserva: "
    )

    sistema.confirmar_reserva(identificador)

    print("Reserva confirmada correctamente.")


# ==========================================================
# 9. CANCELAR RESERVA
# ==========================================================

def menu_cancelar_reserva(sistema: Sistema) -> None:

    print("\nCANCELAR RESERVA")

    identificador = leer_texto(
        "Identificador de la reserva: "
    )

    sistema.cancelar_reserva(identificador)

    print("Reserva cancelada correctamente.")


# ==========================================================
# PROGRAMA PRINCIPAL
# ==========================================================

def main() -> None:

    sistema = Sistema()

    registrar_evento(
        "Aplicación principal de Software FJ iniciada."
    )

    acciones = {
        "1": menu_registrar_cliente,
        "2": menu_registrar_servicio,
        "3": menu_crear_reserva,
        "4": menu_consultar_clientes,
        "5": menu_consultar_servicios,
        "6": menu_consultar_reservas,
        "7": menu_procesar_reserva,
        "8": menu_confirmar_reserva,
        "9": menu_cancelar_reserva
    }

    while True:

        mostrar_menu()

        opcion = input(
            "Selecciona una opción: "
        ).strip()

        if opcion == "0":

            registrar_evento(
                "Aplicación principal de Software FJ finalizada."
            )

            print("\nGracias por utilizar Software FJ.")
            break

        accion = acciones.get(opcion)

        if accion is None:

            print("Opción incorrecta. Intenta nuevamente.")
            continue

        try:

            accion(sistema)

        except (TypeError, ValueError) as error:

            registrar_error(
                f"Error en la operación del menú {opcion}",
                error
            )

            print("\nNo se pudo completar la operación.")
            print("Detalle:", error)

            if error.__cause__ is not None:
                print("Causa original:", error.__cause__)

        except Exception as error:

            registrar_error(
                f"Error inesperado en el menú {opcion}",
                error
            )

            print("\nSe produjo un error inesperado.")
            print("Detalle:", error)

        input("\nPresiona ENTER para regresar al menú.")


if __name__ == "__main__":

    main()
