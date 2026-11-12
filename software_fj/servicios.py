# ==========================================================
# SOFTWARE FJ
# MODULO DE SERVICIOS
# ==========================================================

"""
Módulo de Servicios - Software FJ.

Este módulo define la jerarquía de servicios que ofrece la empresa Software FJ,
aplicando conceptos fundamentales de la Programación Orientada a Objetos (POO):
abstracción, encapsulamiento, herencia y polimorfismo.

Estructura del módulo:
- Servicio: Clase abstracta base que hereda de Entidad y ABC. Establece los
  atributos universales (identificador, nombre, descripción, disponibilidad),
  las validaciones numéricas transversales, el cálculo financiero base y el
  contrato polimórfico mediante métodos abstractos.
- ServicioSala: Especialización para el alquiler de salas de reuniones, tarificado
  por hora y restringido por la capacidad máxima de personas.
- ServicioEquipo: Especialización para el arrendamiento de equipos tecnológicos,
  tarificado por día, con soporte de inventario físico (reserva y liberación de stock).
- ServicioAsesoria: Especialización para asesorías profesionales, tarificado por
  hora según la disciplina o especialidad técnica requerida.

Diseño Polimórfico:
En Python no existe la sobrecarga de métodos nativa en función del tipo o número de
argumentos (method overloading) como en otros lenguajes (Java, C++). Para lograr
un comportamiento polimórfico unificado donde un cliente pueda invocar
`validar_parametros` o `calcular_costo` sin importar el tipo específico de servicio,
las subclases extienden la firma mediante parámetros opcionales con valores por
defecto (ej. `personas: int = 1`, `cantidad: int = 1`). Esto permite cumplir el
principio de sustitución de Liskov (LSP) y simular sobrecarga manteniendo compatibilidad.
"""

from abc import ABC, abstractmethod

from software_fj.entidades import Entidad
from software_fj.excepciones import (
    DatoInvalidoError,
    RecursoNoDisponibleError,
)


# ==========================================================
# CLASE ABSTRACTA SERVICIO
# ==========================================================

class Servicio(Entidad, ABC):
    """
    Clase abstracta base que representa un servicio general ofrecido por Software FJ.

    Hereda de Entidad (para la gestión del identificador único) y de ABC (Abstract
    Base Class) para forzar la implementación de métodos polimórficos en las
    clases derivadas. Provee encapsulamiento estricto para atributos comunes y
    métodos de validación reutilizables en toda la jerarquía de servicios.
    """

    def __init__(
        self,
        identificador: str,
        nombre: str,
        descripcion: str,
        disponible: bool = True
    ) -> None:
        """
        Inicializa los atributos base de un servicio en el sistema.

        Args:
            identificador (str): Código alfanumérico único del servicio.
            nombre (str): Nombre descriptivo comercial del servicio.
            descripcion (str): Detalle de las características del servicio.
            disponible (bool, optional): Estado de habilitación operativa.
                Por defecto es True.

        Raises:
            TypeError: Si el identificador, nombre o descripción no son cadenas,
                o si disponible no es booleano.
            DatoInvalidoError: Si el identificador, nombre o descripción están vacíos.
        """
        # Invocar el constructor de la clase padre Entidad para validar y registrar el identificador
        super().__init__(identificador)

        # Validar y almacenar el nombre comercial como atributo privado
        self.__nombre = self._validar_texto(nombre, "Nombre")

        # Validar y almacenar la descripción del servicio como atributo privado
        self.__descripcion = self._validar_texto(
            descripcion, "Descripción"
        )

        # Validación estricta de tipo para el estado de disponibilidad operativa
        if not isinstance(disponible, bool):
            raise TypeError(
                "La disponibilidad debe ser verdadera o falsa."
            )

        # Asignar el estado de disponibilidad inicial del servicio en el atributo privado
        self.__disponible = disponible

    # ------------------------------------------------------
    # PROPIEDADES (GETTERS Y SETTERS)
    # ------------------------------------------------------

    @property
    def nombre(self) -> str:
        """
        Obtiene el nombre comercial del servicio.

        Returns:
            str: Nombre asignado al servicio.
        """
        # Retorna el atributo privado que almacena el nombre del servicio
        return self.__nombre

    @property
    def descripcion(self) -> str:
        """
        Obtiene la descripción detallada del servicio.

        Returns:
            str: Descripción textual del servicio.
        """
        # Retorna el atributo privado con la descripción del servicio
        return self.__descripcion

    @property
    def disponible(self) -> bool:
        """
        Obtiene el estado de disponibilidad operativa actual del servicio.

        Returns:
            bool: True si el servicio puede ser reservado, False de lo contrario.
        """
        # Retorna la bandera booleana privada de disponibilidad
        return self.__disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        """
        Actualiza el estado de disponibilidad operativa del servicio.

        Args:
            valor (bool): Nuevo estado de disponibilidad (True o False).

        Raises:
            TypeError: Si el valor proporcionado no es de tipo booleano.
        """
        # Comprobar que el nuevo valor sea estrictamente de tipo booleano
        if not isinstance(valor, bool):
            raise TypeError(
                "La disponibilidad debe ser un valor booleano."
            )

        # Actualizar el atributo privado con el nuevo estado verificado
        self.__disponible = valor

    # ------------------------------------------------------
    # VALIDACIONES GENERALES DE NEGOCIO
    # ------------------------------------------------------

    @staticmethod
    def _validar_numero_positivo(
        valor: int | float,
        campo: str
    ) -> float:
        """
        Valida que un valor numérico sea estrictamente positivo mayor que cero.

        Args:
            valor (int | float): Valor numérico a comprobar.
            campo (str): Nombre descriptivo del campo para los mensajes de error.

        Returns:
            float: El valor numérico convertido a tipo flotante.

        Raises:
            TypeError: Si el valor es de tipo booleano o no es numérico (int/float).
            DatoInvalidoError: Si el valor es menor o igual a cero.
        """
        # En Python, bool es subclase de int; se descarta explícitamente bool antes de validar número
        if isinstance(valor, bool) or not isinstance(
            valor, (int, float)
        ):
            raise TypeError(
                f"{campo} debe ser un número."
            )

        # Regla de negocio: valores como tarifas o duraciones deben ser estrictamente positivos
        if valor <= 0:
            raise DatoInvalidoError(
                f"{campo} debe ser mayor que cero."
            )

        # Retornar el número como punto flotante para uniformidad en cálculos matemáticos
        return float(valor)

    @staticmethod
    def _validar_entero_positivo(
        valor: int,
        campo: str
    ) -> int:
        """
        Valida que un valor sea un número entero estrictamente mayor que cero.

        Args:
            valor (int): Número entero a verificar.
            campo (str): Nombre del campo para identificarlo en las excepciones.

        Returns:
            int: El número entero validado.

        Raises:
            TypeError: Si el dato es booleano o no es de tipo entero.
            DatoInvalidoError: Si el valor es menor o igual a cero.
        """
        # Se verifica que sea entero estricto, excluyendo booleanos
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise TypeError(
                f"{campo} debe ser un número entero."
            )

        # Regla de negocio: cantidades, existencias o aforos deben ser enteros mayores a cero
        if valor <= 0:
            raise DatoInvalidoError(
                f"{campo} debe ser mayor que cero."
            )

        # Retornar el entero validado
        return valor

    @staticmethod
    def _validar_porcentaje(
        valor: int | float,
        campo: str
    ) -> float:
        """
        Valida que una tasa porcentual se ubique en el rango permitido de 0 a 100.

        Args:
            valor (int | float): Porcentaje a evaluar (ej. impuestos o descuentos).
            campo (str): Nombre del campo porcentual para reportes de error.

        Returns:
            float: El valor del porcentaje convertido a flotante.

        Raises:
            TypeError: Si el valor es booleano o no es numérico.
            DatoInvalidoError: Si el porcentaje es menor que 0 o mayor que 100.
        """
        # Garantizar que el porcentaje sea de naturaleza numérica, evitando booleanos
        if isinstance(valor, bool) or not isinstance(
            valor, (int, float)
        ):
            raise TypeError(
                f"{campo} debe ser un número."
            )

        # Restricción matemática y de negocio: un porcentaje válido debe estar entre 0% y 100%
        if not 0 <= valor <= 100:
            raise DatoInvalidoError(
                f"{campo} debe estar entre 0 y 100."
            )

        # Retornar la tasa porcentual en formato de punto flotante
        return float(valor)

    def _validar_disponibilidad(self) -> None:
        """
        Verifica si el servicio se encuentra activo para ser reservado o contratado.

        Raises:
            RecursoNoDisponibleError: Si el servicio se encuentra inhabilitado (disponible == False).
        """
        # Evaluar la propiedad de disponibilidad operativa del servicio
        if not self.disponible:
            raise RecursoNoDisponibleError(
                f"El servicio '{self.nombre}' no está disponible."
            )

    # ------------------------------------------------------
    # CALCULO GENERAL DE COSTOS
    # ------------------------------------------------------

    def _calcular_total(
        self,
        tarifa: float,
        duracion: float,
        impuesto: float = 0,
        descuento: float = 0,
        cantidad: int = 1
    ) -> float:
        """
        Calcula el costo total aplicando tarifa, duración, cantidad, descuentos e impuestos.

        Lógica financiera aplicada:
        1. Se valida que el impuesto y descuento sean porcentajes válidos (0 a 100).
        2. Se valida que la cantidad de unidades sea un entero positivo.
        3. Subtotal bruto = tarifa * duración * cantidad.
        4. Descuento comercial = Subtotal bruto * (descuento / 100).
        5. Subtotal neto = Subtotal bruto - Descuento comercial.
        6. Impuesto = Subtotal neto * (impuesto / 100).
        7. Total final = Subtotal neto + Impuesto.
        8. Se redondea a 2 decimales para evitar imprecisiones de coma flotante.

        Args:
            tarifa (float): Precio unitario base por unidad de tiempo.
            duracion (float): Cantidad de tiempo solicitada (horas o días).
            impuesto (float, optional): Porcentaje de gravamen tributario (0-100). Por defecto 0.
            descuento (float, optional): Porcentaje de rebaja comercial (0-100). Por defecto 0.
            cantidad (int, optional): Unidades del recurso solicitadas. Por defecto 1.

        Returns:
            float: Monto monetario final redondeado a dos cifras decimales.

        Raises:
            TypeError: Si algún parámetro no cumple el tipo numérico esperado.
            DatoInvalidoError: Si algún parámetro numérico está fuera de los rangos válidos.
        """
        # Validar que el porcentaje tributario esté en el rango de 0 a 100
        impuesto = self._validar_porcentaje(
            impuesto, "Impuesto"
        )

        # Validar que el porcentaje de descuento comercial esté en el rango de 0 a 100
        descuento = self._validar_porcentaje(
            descuento, "Descuento"
        )

        # Validar que la cantidad de unidades solicitadas sea un entero positivo
        cantidad = self._validar_entero_positivo(
            cantidad, "Cantidad"
        )

        # Calcular el subtotal bruto: tarifa base multiplicada por duración y cantidad solicitada
        subtotal = tarifa * duracion * cantidad

        # Calcular el valor monetario correspondiente al descuento comercial
        valor_descuento = subtotal * descuento / 100

        # Restar el descuento al subtotal para obtener la base gravable neta
        subtotal -= valor_descuento

        # Calcular el valor del impuesto aplicado sobre el subtotal neto con descuento
        valor_impuesto = subtotal * impuesto / 100

        # Sumar el impuesto al subtotal neto para obtener el valor total consolidado
        total = subtotal + valor_impuesto

        # Redondear el total final a 2 decimales para precisión monetaria (evita errores IEEE 754)
        return round(total, 2)

    # ------------------------------------------------------
    # METODOS ABSTRACTOS (CONTRATO POLIMORFICO)
    # ------------------------------------------------------

    @abstractmethod
    def validar_parametros(self, duracion: float) -> None:
        """
        Valida que los parámetros temporales y de recursos sean aptos para el servicio.

        Método abstracto que obliga a cada tipo de servicio a implementar sus
        propias reglas de negocio (ej. validación de aforo en salas o existencias en equipos).

        Args:
            duracion (float): Duración del uso del servicio (horas o días según corresponda).

        Raises:
            RecursoNoDisponibleError: Si el servicio está inhabilitado o no hay existencias.
            TypeError: Si los parámetros no corresponden a los tipos esperados.
            DatoInvalidoError: Si los valores numéricos violan restricciones de negocio.
        """
        pass

    @abstractmethod
    def calcular_costo(
        self,
        duracion: float,
        impuesto: float = 0,
        descuento: float = 0
    ) -> float:
        """
        Calcula el valor económico total a cobrar por la prestación del servicio.

        Método abstracto que garantiza el polimorfismo, permitiendo calcular costos
        de manera uniforme a través de la interfaz base común.

        Args:
            duracion (float): Tiempo de uso del servicio.
            impuesto (float, optional): Porcentaje tributario a sumar. Por defecto 0.
            descuento (float, optional): Porcentaje comercial a restar. Por defecto 0.

        Returns:
            float: Costo total final calculado.

        Raises:
            RecursoNoDisponibleError: Si el servicio no está operativo.
            TypeError: Si los tipos numéricos son incorrectos.
            DatoInvalidoError: Si los parámetros temporales o porcentuales son inválidos.
        """
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        """
        Genera una descripción detallada en texto con los atributos del servicio.

        Método abstracto que debe sobreescribir cada subclase para mostrar sus
        atributos especializados (capacidad, existencias, especialidad, etc.).

        Returns:
            str: Ficha descriptiva formateada del servicio.
        """
        pass

    # ------------------------------------------------------
    # IMPLEMENTACION DEL METODO HEREDADO DE ENTIDAD
    # ------------------------------------------------------

    def obtener_informacion(self) -> str:
        """
        Implementa el método abstracto exigido por la clase padre Entidad.

        Delega la responsabilidad en el método polimórfico `describir_servicio()`,
        garantizando que cualquier servicio pueda ser tratado genéricamente como Entidad.

        Returns:
            str: Cadena de texto con la información completa del servicio.
        """
        # Reutilizar la descripción polimórfica específica de la subclase concreta
        return self.describir_servicio()


# ==========================================================
# SERVICIO 1: RESERVA DE SALAS
# ==========================================================

class ServicioSala(Servicio):
    """
    Administra las reservas de salas de reuniones y conferencias de Software FJ.

    Hereda de Servicio y especializa el cobro por hora de uso, incorporando
    la restricción de aforo o capacidad máxima física de asistentes.
    """

    def __init__(
        self,
        identificador: str,
        nombre: str,
        capacidad: int,
        precio_hora: float,
        disponible: bool = True
    ) -> None:
        """
        Inicializa una sala de reuniones con sus características y restricciones.

        Args:
            identificador (str): Código identificador único de la sala.
            nombre (str): Nombre comercial o número de sala.
            capacidad (int): Cantidad máxima de personas permitidas simultáneamente.
            precio_hora (float): Tarifa monetaria base por cada hora de reserva.
            disponible (bool, optional): Estado operativo de la sala. Por defecto True.

        Raises:
            TypeError: Si algún parámetro no coincide con el tipo de dato requerido.
            DatoInvalidoError: Si el aforo o el precio por hora son menores o iguales a cero.
        """
        # Inicializar atributos de la clase abstracta padre con una descripción predeterminada
        super().__init__(
            identificador,
            nombre,
            "Servicio de reserva de salas.",
            disponible
        )

        # Validar que la capacidad máxima sea un número entero estrictamente positivo
        self.__capacidad = self._validar_entero_positivo(
            capacidad, "Capacidad"
        )

        # Validar que la tarifa por hora sea un número positivo mayor que cero
        self.__precio_hora = self._validar_numero_positivo(
            precio_hora, "Precio por hora"
        )

    @property
    def capacidad(self) -> int:
        """
        Obtiene la capacidad máxima de asistentes permitida en la sala.

        Returns:
            int: Aforo límite de la sala.
        """
        # Retorna el atributo privado con la capacidad máxima de personas
        return self.__capacidad

    @property
    def precio_hora(self) -> float:
        """
        Obtiene el precio de alquiler por hora fijado para la sala.

        Returns:
            float: Tarifa por hora en moneda local.
        """
        # Retorna el atributo privado con el precio fijado por hora
        return self.__precio_hora

    def validar_parametros(
        self,
        duracion: float,
        personas: int = 1
    ) -> None:
        """
        Valida que la duración y la cantidad de asistentes sean válidas para la sala.

        Diseño polimórfico:
        En Python no existe la sobrecarga de métodos nativa por firma de tipos. Para
        mantener la compatibilidad polimórfica con el método base `validar_parametros(duracion)`,
        se implementa `personas: int = 1` como parámetro opcional con valor por defecto,
        simulando sobrecarga sin romper el principio de sustitución de Liskov.

        Args:
            duracion (float): Tiempo de reserva expresado en horas.
            personas (int, optional): Número de asistentes previstos. Por defecto 1.

        Raises:
            RecursoNoDisponibleError: Si la sala está marcada como no disponible.
            TypeError: Si la duración o la cantidad de personas no tienen el tipo correcto.
            DatoInvalidoError: Si la duración <= 0, personas <= 0 o personas supera la capacidad.
        """
        # Paso 1: Verificar que la sala se encuentre disponible operativamente
        self._validar_disponibilidad()

        # Paso 2: Validar que la duración en horas sea un valor numérico positivo
        self._validar_numero_positivo(
            duracion, "Duración"
        )

        # Paso 3: Validar que la cantidad de asistentes sea un número entero positivo
        personas = self._validar_entero_positivo(
            personas, "Número de personas"
        )

        # Paso 4: Regla de negocio crucial: la concurrencia no puede sobrepasar el aforo de la sala
        if personas > self.capacidad:
            raise DatoInvalidoError(
                "La cantidad de personas supera la capacidad de la sala."
            )

    def calcular_costo(
        self,
        duracion: float,
        impuesto: float = 0,
        descuento: float = 0,
        personas: int = 1
    ) -> float:
        """
        Calcula el valor económico total para la reserva de la sala.

        Simula sobrecarga mediante el parámetro opcional `personas: int = 1` para
        permitir tanto la invocación polimórfica genérica como la invocación específica.

        Args:
            duracion (float): Duración de la reserva expresada en horas.
            impuesto (float, optional): Porcentaje tributario a sumar (0-100). Por defecto 0.
            descuento (float, optional): Porcentaje comercial a restar (0-100). Por defecto 0.
            personas (int, optional): Asistentes previstos para comprobar capacidad. Por defecto 1.

        Returns:
            float: Costo final de la reserva con impuestos y descuentos aplicados.

        Raises:
            RecursoNoDisponibleError: Si la sala no está disponible.
            TypeError: Si los parámetros contienen tipos inadecuados.
            DatoInvalidoError: Si los parámetros violan restricciones de negocio.
        """
        # Validar todas las condiciones previas de negocio: disponibilidad, duración y aforo
        self.validar_parametros(duracion, personas)

        # Invocar el cálculo general heredado con la tarifa horaria de la sala (cantidad implícita 1)
        return self._calcular_total(
            self.precio_hora,
            duracion,
            impuesto,
            descuento
        )

    def describir_servicio(self) -> str:
        """
        Genera una descripción textual estructurada con la información de la sala.

        Returns:
            str: Ficha técnica de la sala incluyendo capacidad y tarifa por hora.
        """
        # Formatear la cadena representativa con identificador, nombre, aforo, precio y estado
        return (
            f"SERVICIO DE SALA | "
            f"ID: {self.identificador} | "
            f"Nombre: {self.nombre} | "
            f"Capacidad: {self.capacidad} personas | "
            f"Precio por hora: ${self.precio_hora:,.2f} | "
            f"Disponible: {self.disponible}"
        )


# ==========================================================
# SERVICIO 2: ALQUILER DE EQUIPOS
# ==========================================================

class ServicioEquipo(Servicio):
    """
    Administra el alquiler de equipos tecnológicos y audiovisuales de Software FJ.

    Hereda de Servicio y especializa el cobro por día de uso, incorporando
    el control de inventario de existencias físicas disponibles para arriendo.
    """

    def __init__(
        self,
        identificador: str,
        nombre: str,
        precio_dia: float,
        existencias: int,
        disponible: bool = True
    ) -> None:
        """
        Inicializa un equipo tecnológico con su inventario y tarifa diaria.

        Args:
            identificador (str): Código identificador único del equipo.
            nombre (str): Nombre comercial o referencia del equipo (ej. 'Portátil Lenovo').
            precio_dia (float): Tarifa monetaria de alquiler por día y por unidad.
            existencias (int): Cantidad inicial de unidades disponibles en inventario.
            disponible (bool, optional): Estado de disponibilidad operativa. Por defecto True.

        Raises:
            TypeError: Si los parámetros no cumplen con los tipos de datos esperados.
            DatoInvalidoError: Si el precio por día o las existencias no son positivos.
        """
        # Inicializar la clase padre Servicio con la descripción correspondiente a equipos
        super().__init__(
            identificador,
            nombre,
            "Servicio de alquiler de equipos.",
            disponible
        )

        # Validar y almacenar la tarifa de alquiler por día como flotante positivo
        self.__precio_dia = self._validar_numero_positivo(
            precio_dia, "Precio por día"
        )

        # Validar y almacenar el inventario inicial de unidades físicas en bodega
        self.__existencias = self._validar_entero_positivo(
            existencias, "Existencias"
        )

    @property
    def precio_dia(self) -> float:
        """
        Obtiene la tarifa de alquiler por día para el equipo.

        Returns:
            float: Costo por día de uso de una unidad.
        """
        # Retorna el atributo privado con el precio diario por equipo
        return self.__precio_dia

    @property
    def existencias(self) -> int:
        """
        Obtiene la cantidad actual de unidades disponibles en inventario.

        Returns:
            int: Unidades físicas en bodega no reservadas.
        """
        # Retorna el atributo privado que rastrea el stock físico en bodega
        return self.__existencias

    # ------------------------------------------------------
    # CONTROL DE INVENTARIO
    # ------------------------------------------------------

    def reservar_existencias(self, cantidad: int) -> None:
        """
        Descuenta las unidades del inventario físico cuando se confirma un alquiler.

        Args:
            cantidad (int): Número de unidades a descontar del stock.

        Raises:
            TypeError: Si la cantidad no es un número entero.
            DatoInvalidoError: Si la cantidad es menor o igual a cero.
            RecursoNoDisponibleError: Si el servicio está inhabilitado o si la cantidad
                solicitada supera las existencias físicas disponibles.
        """
        # Validar que la cantidad solicitada sea un número entero positivo
        cantidad = self._validar_entero_positivo(
            cantidad, "Cantidad de equipos"
        )

        # Verificar que el servicio de equipos se encuentre habilitado operativamente
        self._validar_disponibilidad()

        # Comprobar si el stock actual en bodega es suficiente para cubrir la demanda
        if cantidad > self.__existencias:
            raise RecursoNoDisponibleError(
                f"Existencias insuficientes para '{self.nombre}'. "
                f"Disponibles: {self.__existencias}."
            )

        # Descontar del inventario disponible las unidades comprometidas en la reserva
        self.__existencias -= cantidad

    def liberar_existencias(self, cantidad: int) -> None:
        """
        Restituye las unidades al inventario cuando se cancela o finaliza una reserva.

        Args:
            cantidad (int): Cantidad de equipos que retornan al inventario.

        Raises:
            TypeError: Si la cantidad no es un número entero.
            DatoInvalidoError: Si la cantidad es menor o igual a cero.
        """
        # Validar que la cantidad a reintegrar sea un número entero positivo
        cantidad = self._validar_entero_positivo(
            cantidad, "Cantidad de equipos"
        )

        # Incrementar el stock disponible con los equipos retornados
        self.__existencias += cantidad

    def validar_parametros(
        self,
        duracion: float,
        cantidad: int = 1
    ) -> None:
        """
        Valida que la duración del alquiler y la cantidad de equipos sean válidas.

        Diseño polimórfico:
        Al no existir sobrecarga de métodos nativa en Python, se incluye `cantidad: int = 1`
        como parámetro por defecto para permitir su invocación mediante la interfaz
        polimórfica general `validar_parametros(duracion)` o de forma específica con cantidad.

        Args:
            duracion (float): Tiempo de alquiler expresado en días.
            cantidad (int, optional): Número de unidades requeridas. Por defecto 1.

        Raises:
            RecursoNoDisponibleError: Si el servicio está inhabilitado o no hay existencias.
            TypeError: Si los parámetros no cumplen los tipos esperados.
            DatoInvalidoError: Si la duración <= 0 o la cantidad <= 0.
        """
        # Paso 1: Comprobar el estado operativo general del servicio
        self._validar_disponibilidad()

        # Paso 2: Validar que los días de alquiler sean un número positivo
        self._validar_numero_positivo(
            duracion, "Duración"
        )

        # Paso 3: Validar que la cantidad de equipos solicitada sea un entero positivo
        cantidad = self._validar_entero_positivo(
            cantidad, "Cantidad de equipos"
        )

        # Paso 4: Validar disponibilidad de existencias sin modificarlas en esta etapa preliminar
        if cantidad > self.existencias:
            raise RecursoNoDisponibleError(
                f"No existen suficientes equipos disponibles. "
                f"Disponibles: {self.existencias}."
            )

    def calcular_costo(
        self,
        duracion: float,
        impuesto: float = 0,
        descuento: float = 0,
        cantidad: int = 1
    ) -> float:
        """
        Calcula el valor económico total para el alquiler de equipos.

        Simula sobrecarga mediante el parámetro opcional `cantidad: int = 1`,
        integrando tarifa por día, días de duración y número de unidades.

        Args:
            duracion (float): Duración del arriendo en días.
            impuesto (float, optional): Porcentaje tributario (0-100). Por defecto 0.
            descuento (float, optional): Porcentaje de rebaja comercial (0-100). Por defecto 0.
            cantidad (int, optional): Número de equipos a alquilar. Por defecto 1.

        Returns:
            float: Costo total final calculado y redondeado.

        Raises:
            RecursoNoDisponibleError: Si no hay disponibilidad o stock suficiente.
            TypeError: Si se suministran tipos incorrectos.
            DatoInvalidoError: Si los parámetros no cumplen las restricciones numéricas.
        """
        # Validar duración, disponibilidad y stock suficiente antes de proceder al cálculo
        self.validar_parametros(duracion, cantidad)

        # Invocar el cálculo general heredado con tarifa por día, días, impuesto, descuento y cantidad
        return self._calcular_total(
            self.precio_dia,
            duracion,
            impuesto,
            descuento,
            cantidad
        )

    def describir_servicio(self) -> str:
        """
        Genera una descripción textual estructurada con la información del equipo.

        Returns:
            str: Ficha técnica del equipo incluyendo tarifa diaria y existencias.
        """
        # Formatear la cadena representativa con identificador, nombre, tarifa diaria, stock y estado
        return (
            f"ALQUILER DE EQUIPOS | "
            f"ID: {self.identificador} | "
            f"Equipo: {self.nombre} | "
            f"Precio por día: ${self.precio_dia:,.2f} | "
            f"Existencias: {self.existencias} | "
            f"Disponible: {self.disponible}"
        )


# ==========================================================
# SERVICIO 3: ASESORIAS ESPECIALIZADAS
# ==========================================================

class ServicioAsesoria(Servicio):
    """
    Administra las asesorías y consultorías especializadas de Software FJ.

    Hereda de Servicio y especializa el cobro por hora de consultoría,
    asociando un área de conocimiento o especialidad profesional técnica.
    """

    def __init__(
        self,
        identificador: str,
        nombre: str,
        especialidad: str,
        precio_hora: float,
        disponible: bool = True
    ) -> None:
        """
        Inicializa un servicio de asesoría técnica especializada.

        Args:
            identificador (str): Código identificador único del servicio de asesoría.
            nombre (str): Nombre comercial de la asesoría (ej. 'Asesoría en programación').
            especialidad (str): Área o disciplina técnica abordada.
            precio_hora (float): Tarifa por hora de consultoría profesional.
            disponible (bool, optional): Estado de disponibilidad operativa. Por defecto True.

        Raises:
            TypeError: Si los parámetros no coinciden con los tipos de datos requeridos.
            DatoInvalidoError: Si los textos están vacíos o si el precio por hora no es positivo.
        """
        # Inicializar atributos de la clase abstracta padre Servicio con descripción específica
        super().__init__(
            identificador,
            nombre,
            "Servicio de asesoría especializada.",
            disponible
        )

        # Validar y almacenar la especialidad técnica como texto no vacío
        self.__especialidad = self._validar_texto(
            especialidad, "Especialidad"
        )

        # Validar y almacenar el precio por hora como valor numérico positivo
        self.__precio_hora = self._validar_numero_positivo(
            precio_hora, "Precio por hora"
        )

    @property
    def especialidad(self) -> str:
        """
        Obtiene el área técnica o temática de la asesoría.

        Returns:
            str: Nombre del área de especialidad.
        """
        # Retorna el atributo privado con la especialidad técnica
        return self.__especialidad

    @property
    def precio_hora(self) -> float:
        """
        Obtiene la tarifa por hora de la asesoría profesional.

        Returns:
            float: Costo fijado por cada hora de consultoría.
        """
        # Retorna el atributo privado con el precio fijado por hora
        return self.__precio_hora

    def validar_parametros(self, duracion: float) -> None:
        """
        Valida que la disponibilidad y la duración en horas sean válidas para la asesoría.

        Args:
            duracion (float): Duración de la sesión de asesoría en horas.

        Raises:
            RecursoNoDisponibleError: Si la asesoría está inhabilitada.
            TypeError: Si la duración no es un dato numérico.
            DatoInvalidoError: Si la duración es menor o igual a cero.
        """
        # Paso 1: Comprobar que el servicio de asesoría se encuentre habilitado operativamente
        self._validar_disponibilidad()

        # Paso 2: Validar que la duración en horas sea un valor numérico estrictamente positivo
        self._validar_numero_positivo(
            duracion, "Duración"
        )

    def calcular_costo(
        self,
        duracion: float,
        impuesto: float = 0,
        descuento: float = 0
    ) -> float:
        """
        Calcula el valor económico total para la sesión de asesoría especializada.

        Args:
            duracion (float): Tiempo de la asesoría expresado en horas.
            impuesto (float, optional): Porcentaje tributario (0-100). Por defecto 0.
            descuento (float, optional): Porcentaje comercial a restar (0-100). Por defecto 0.

        Returns:
            float: Costo total consolidado de la asesoría.

        Raises:
            RecursoNoDisponibleError: Si el servicio no está operativo.
            TypeError: Si los parámetros no son numéricos.
            DatoInvalidoError: Si la duración o porcentajes violan restricciones de negocio.
        """
        # Validar las condiciones previas de negocio: disponibilidad y duración horaria
        self.validar_parametros(duracion)

        # Invocar el cálculo general heredado con la tarifa horaria del asesor (cantidad 1)
        return self._calcular_total(
            self.precio_hora,
            duracion,
            impuesto,
            descuento
        )

    def describir_servicio(self) -> str:
        """
        Genera una descripción textual estructurada con la información de la asesoría.

        Returns:
            str: Ficha informativa de la asesoría incluyendo especialidad y tarifa por hora.
        """
        # Formatear la cadena representativa con identificador, nombre, especialidad, tarifa y estado
        return (
            f"ASESORIA ESPECIALIZADA | "
            f"ID: {self.identificador} | "
            f"Nombre: {self.nombre} | "
            f"Especialidad: {self.especialidad} | "
            f"Precio por hora: ${self.precio_hora:,.2f} | "
            f"Disponible: {self.disponible}"
        )
