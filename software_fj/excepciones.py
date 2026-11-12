# ==========================================================
# UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD
# ESCUELA DE CIENCIAS BÁSICAS, TECNOLOGÍA E INGENIERÍA - ECBTI
# SOFTWARE FJ - MÓDULO DE EXCEPCIONES PERSONALIZADAS
# ==========================================================

"""
Módulo de excepciones personalizadas para el sistema Software FJ.

Este módulo define una jerarquía orientada a objetos de excepciones de
dominio para el sistema de gestión. La estructura jerárquica permite
capturar errores de manera granular o agruparlos bajo una misma clase base,
garantizando robustez en el manejo de fallos y claridad diagnóstica.

Jerarquía de excepciones del sistema:
    ValueError (incorporada en Python)
        └── ErrorSoftwareFJ (clase base para todo error del sistema)
            ├── DatoInvalidoError (errores de formato o validación de campos)
            ├── RegistroDuplicadoError (intentos de registrar claves ya existentes)
            ├── RecursoNoDisponibleError (recursos o servicios no disponibles)
            ├── EstadoReservaError (transiciones de estado inválidas en reservas)
            ├── OperacionNoPermitidaError (violaciones de reglas de negocio)
            └── ErrorProcesamientoReserva (fallos durante el procesamiento o cálculo)

Justificación del diseño y cadena de herencia:
Todas las excepciones del sistema heredan directa o indirectamente de `ValueError`.
En la biblioteca estándar de Python, `ValueError` representa situaciones donde una
función u operación recibe un argumento del tipo esperado, pero con un valor inadecuado.
Dado que la gran mayoría de errores de negocio en Software FJ corresponden a entradas
con valores fuera de rango, formatos incorrectos, estados incompatibles o colisiones
de datos, hacer que `ErrorSoftwareFJ` herede de `ValueError` ofrece dos ventajas clave:
1. Polimorfismo y compatibilidad: El código cliente que use bloques genéricos
   `except ValueError:` podrá interceptar automáticamente cualquier fallo del sistema.
2. Granularidad semántica: Permite capturar selectivamente `ErrorSoftwareFJ` para
   aislar la lógica propia de Software FJ, o bien capturar subclases específicas
   para reaccionar puntualmente ante cada caso de fallo.
"""


# ==========================================================
# CLASE BASE DE EXCEPCIONES DEL SISTEMA
# ==========================================================

# Se hereda directamente de ValueError para mantener consistencia con el manejo
# estándar de datos incorrectos en Python y permitir compatibilidad polimórfica.
class ErrorSoftwareFJ(ValueError):
    """
    Clase base para todos los errores y excepciones del sistema Software FJ.

    Esta clase actúa como el nodo raíz de la jerarquía de excepciones del
    dominio. Permite a los módulos de control y a la interfaz de usuario
    capturar cualquier error originado en las operaciones de negocio de
    Software FJ mediante un único bloque `except ErrorSoftwareFJ:`.

    Hereda de:
        ValueError: Porque todas las anomalías del dominio representan
        valores, estados o parámetros incompatibles con las operaciones.

    Cuándo se utiliza:
        Generalmente no se instancia de forma directa; se utiliza como clase
        padre para las excepciones específicas del sistema o para atrapar
        de forma genérica cualquier error propio de la aplicación.
    """
    pass


# ==========================================================
# EXCEPCIONES ESPECÍFICAS DEL DOMINIO
# ==========================================================

# Hereda de ErrorSoftwareFJ para indicar que un valor de campo no cumple con las reglas.
class DatoInvalidoError(ErrorSoftwareFJ):
    """
    Excepción lanzada cuando un dato de entrada no cumple las reglas de validación.

    Contexto de aplicación:
        Se utiliza extensivamente en la capa de entidades (`Entidad`, `Cliente`),
        en la jerarquía de servicios (`ServicioSala`, `ServicioEquipo`,
        `ServicioAsesoria`) y en la creación de reservas (`Reserva`).

    Cuándo se lanza:
        - Al ingresar cadenas de texto vacías o compuestas únicamente por espacios en blanco.
        - Cuando un nombre contiene números, caracteres no autorizados o longitud fuera de rango (2 a 80).
        - Cuando un documento de identidad contiene caracteres ilegales o longitud inadecuada (5 a 20).
        - Cuando una dirección de correo no cumple con el formato estándar verificado mediante regex.
        - Cuando un número telefónico no contiene entre 7 y 15 dígitos numéricos válidos.
        - Cuando capacidades, duraciones o precios numéricos son negativos o nulos.
        - Cuando las fechas u horarios de reserva son incoherentes o están en el pasado.
    """
    pass


# Hereda de ErrorSoftwareFJ para señalar colisiones de clave primaria o registros unívocos.
class RegistroDuplicadoError(ErrorSoftwareFJ):
    """
    Excepción lanzada al intentar registrar un elemento que ya existe en el sistema.

    Contexto de aplicación:
        Se utiliza en el módulo `Sistema` durante las operaciones de alta y registro
        en las colecciones internas de datos (diccionarios y listas maestras).

    Cuándo se lanza:
        - Al intentar agregar un cliente cuyo identificador único (ID) ya está registrado.
        - Al intentar agregar un cliente cuyo documento de identidad ya pertenece a otro cliente.
        - Al registrar un servicio con un código identificador previamente asignado.
        - Al registrar una reserva con un identificador unívoco preexistente.
    """
    pass


# Hereda de ErrorSoftwareFJ para indicar la falta de cupo o indisponibilidad física.
class RecursoNoDisponibleError(ErrorSoftwareFJ):
    """
    Excepción lanzada cuando un servicio o recurso solicitado no puede ser asignado.

    Contexto de aplicación:
        Se utiliza en los módulos `servicios`, `reservas` y `sistema` durante la
        verificación de disponibilidad para la programación de reservas.

    Cuándo se lanza:
        - Cuando un servicio (sala, equipo o asesoría) tiene su estado de disponibilidad en False.
        - Cuando una sala solicitada ya se encuentra apartada para el horario seleccionado.
        - Cuando la cantidad solicitada de un equipo de cómputo supera el inventario disponible.
        - Cuando un asesor profesional no cuenta con agenda habilitada para la fecha indicada.
    """
    pass


# Hereda de ErrorSoftwareFJ para señalar transiciones ilegales en el ciclo de vida de la reserva.
class EstadoReservaError(ErrorSoftwareFJ):
    """
    Excepción lanzada cuando una operación no corresponde al estado actual de la reserva.

    Contexto de aplicación:
        Se utiliza en el módulo `reservas` dentro de la máquina de estados que gobierna
        el ciclo de vida de la clase `Reserva` (PENDIENTE, CONFIRMADA, CANCELADA, FINALIZADA).

    Cuándo se lanza:
        - Al intentar confirmar una reserva que ya fue cancelada o finalizada.
        - Al intentar cancelar una reserva que ya se encuentra en estado cancelado.
        - Al intentar modificar parámetros de una reserva cuyo estado no permite cambios.
        - Al intentar finalizar una reserva que no ha sido confirmada previamente.
    """
    pass


# Hereda de ErrorSoftwareFJ para advertir violaciones directas a las directivas del negocio.
class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """
    Excepción lanzada cuando se intenta realizar una acción prohibida por las reglas de negocio.

    Contexto de aplicación:
        Se utiliza en los módulos `sistema` y `reservas` para proteger la integridad
        operacional, aplicar políticas de tiempo y controlar el flujo de trabajo.

    Cuándo se lanza:
        - Al intentar cancelar una reserva fuera del tiempo límite permitido por la política empresarial.
        - Al intentar aplicar descuentos o promociones no aplicables para un tipo de servicio.
        - Al solicitar operaciones sobre registros inactivos, bloqueados o inexistentes.
        - Al intentar ejecutar transacciones que violan los límites administrativos establecidos.
    """
    pass


# Hereda de ErrorSoftwareFJ para agrupar fallas en la lógica transaccional o matemática de la reserva.
class ErrorProcesamientoReserva(ErrorSoftwareFJ):
    """
    Excepción lanzada cuando ocurre un error crítico durante el procesamiento de una reserva.

    Contexto de aplicación:
        Se utiliza en el módulo `reservas` y `sistema` durante la liquidación de cobros,
        generación de facturación o persistencia transaccional de una reserva.

    Cuándo se lanza:
        - Cuando el cálculo de la tarifa total falla por inconsistencias en la duración o tarifas horarias.
        - Cuando se produce una condición de carrera o conflicto de concurrencia al reservar simultáneamente.
        - Cuando la integración entre cliente, servicio y reserva no puede ser completada satisfactoriamente.
    """
    pass
