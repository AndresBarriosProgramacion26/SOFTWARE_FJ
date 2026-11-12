
# ==========================================================
# SOFTWARE FJ
# MODULO DE SERVICIOS
# ==========================================================

from abc import ABC, abstractmethod
from software_fj.entidades import Entidad
from software_fj.excepciones import RecursoNoDisponibleError

# ==========================================================
# CLASE ABSTRACTA SERVICIO
# ==========================================================

class Servicio(Entidad, ABC):
    """
    Clase abstracta que representa un servicio general
    ofrecido por Software FJ.
    """

    def __init__(
        self,
        identificador: str,
        nombre: str,
        descripcion: str,
        disponible: bool = True
    ) -> None:

        super().__init__(identificador)

        self.__nombre = self._validar_texto(nombre, "Nombre")
        self.__descripcion = self._validar_texto(
            descripcion, "Descripción"
        )

        if not isinstance(disponible, bool):
            raise TypeError(
                "La disponibilidad debe ser verdadera o falsa."
            )

        self.__disponible = disponible

    # ------------------------------------------------------
    # PROPIEDADES
    # ------------------------------------------------------

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def descripcion(self) -> str:
        return self.__descripcion

    @property
    def disponible(self) -> bool:
        return self.__disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:

        if not isinstance(valor, bool):
            raise TypeError(
                "La disponibilidad debe ser un valor booleano."
            )

        self.__disponible = valor

    # ------------------------------------------------------
    # VALIDACIONES GENERALES
    # ------------------------------------------------------

    @staticmethod
    def _validar_numero_positivo(
        valor: int | float,
        campo: str
    ) -> float:

        if isinstance(valor, bool) or not isinstance(
            valor, (int, float)
        ):
            raise TypeError(
                f"{campo} debe ser un número."
            )

        if valor <= 0:
            raise ValueError(
                f"{campo} debe ser mayor que cero."
            )

        return float(valor)

    @staticmethod
    def _validar_entero_positivo(
        valor: int,
        campo: str
    ) -> int:

        if isinstance(valor, bool) or not isinstance(valor, int):
            raise TypeError(
                f"{campo} debe ser un número entero."
            )

        if valor <= 0:
            raise ValueError(
                f"{campo} debe ser mayor que cero."
            )

        return valor

    @staticmethod
    def _validar_porcentaje(
        valor: int | float,
        campo: str
    ) -> float:

        if isinstance(valor, bool) or not isinstance(
            valor, (int, float)
        ):
            raise TypeError(
                f"{campo} debe ser un número."
            )

        if not 0 <= valor <= 100:
            raise ValueError(
                f"{campo} debe estar entre 0 y 100."
            )

        return float(valor)

    def _validar_disponibilidad(self) -> None:

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
        Calcula el costo con impuestos y descuentos opcionales.
        """

        impuesto = self._validar_porcentaje(
            impuesto, "Impuesto"
        )

        descuento = self._validar_porcentaje(
            descuento, "Descuento"
        )

        cantidad = self._validar_entero_positivo(
            cantidad, "Cantidad"
        )

        subtotal = tarifa * duracion * cantidad

        valor_descuento = subtotal * descuento / 100

        subtotal -= valor_descuento

        valor_impuesto = subtotal * impuesto / 100

        total = subtotal + valor_impuesto

        return round(total, 2)

    # ------------------------------------------------------
    # METODOS ABSTRACTOS
    # ------------------------------------------------------

    @abstractmethod
    def validar_parametros(self, duracion: float) -> None:
        pass

    @abstractmethod
    def calcular_costo(
        self,
        duracion: float,
        impuesto: float = 0,
        descuento: float = 0
    ) -> float:
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        pass

    # ------------------------------------------------------
    # IMPLEMENTACION DEL METODO HEREDADO
    # ------------------------------------------------------

    def obtener_informacion(self) -> str:

        return self.describir_servicio()


# ==========================================================
# SERVICIO 1: RESERVA DE SALAS
# ==========================================================

class ServicioSala(Servicio):
    """
    Administra las reservas de salas de Software FJ.
    El cobro se realiza por hora.
    """

    def __init__(
        self,
        identificador: str,
        nombre: str,
        capacidad: int,
        precio_hora: float,
        disponible: bool = True
    ) -> None:

        super().__init__(
            identificador,
            nombre,
            "Servicio de reserva de salas."
            ,
            disponible
        )

        self.__capacidad = self._validar_entero_positivo(
            capacidad, "Capacidad"
        )

        self.__precio_hora = self._validar_numero_positivo(
            precio_hora, "Precio por hora"
        )

    @property
    def capacidad(self) -> int:
        return self.__capacidad

    @property
    def precio_hora(self) -> float:
        return self.__precio_hora

    def validar_parametros(
        self,
        duracion: float,
        personas: int = 1
    ) -> None:

        self._validar_disponibilidad()

        self._validar_numero_positivo(
            duracion, "Duración"
        )

        personas = self._validar_entero_positivo(
            personas, "Número de personas"
        )

        if personas > self.capacidad:
            raise ValueError(
                "La cantidad de personas supera la capacidad de la sala."
            )

    def calcular_costo(
        self,
        duracion: float,
        impuesto: float = 0,
        descuento: float = 0,
        personas: int = 1
    ) -> float:

        self.validar_parametros(duracion, personas)

        return self._calcular_total(
            self.precio_hora,
            duracion,
            impuesto,
            descuento
        )

    def describir_servicio(self) -> str:

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
    Administra el alquiler de equipos.
    El cobro se realiza por día.
    """

    def __init__(
        self,
        identificador: str,
        nombre: str,
        precio_dia: float,
        existencias: int,
        disponible: bool = True
    ) -> None:

        super().__init__(
            identificador,
            nombre,
            "Servicio de alquiler de equipos."
            ,
            disponible
        )

        self.__precio_dia = self._validar_numero_positivo(
            precio_dia, "Precio por día"
        )

        self.__existencias = self._validar_entero_positivo(
            existencias, "Existencias"
        )

    @property
    def precio_dia(self) -> float:
        return self.__precio_dia

    @property
    def existencias(self) -> int:
        return self.__existencias


    # ------------------------------------------------------
    # CONTROL DE INVENTARIO
    # ------------------------------------------------------

    def reservar_existencias(self, cantidad: int) -> None:
        """Descuenta los equipos cuando se confirma un alquiler."""

        cantidad = self._validar_entero_positivo(
            cantidad, "Cantidad de equipos"
        )

        self._validar_disponibilidad()

        if cantidad > self.__existencias:
            raise RecursoNoDisponibleError(
                f"Existencias insuficientes para '{self.nombre}'. "
                f"Disponibles: {self.__existencias}."
            )

        self.__existencias -= cantidad

    def liberar_existencias(self, cantidad: int) -> None:
        """Devuelve los equipos cuando se cancela un alquiler."""

        cantidad = self._validar_entero_positivo(
            cantidad, "Cantidad de equipos"
        )

        self.__existencias += cantidad

    def validar_parametros(
        self,
        duracion: float,
        cantidad: int = 1
    ) -> None:

        self._validar_disponibilidad()

        self._validar_numero_positivo(
            duracion, "Duración"
        )

        cantidad = self._validar_entero_positivo(
            cantidad, "Cantidad de equipos"
        )

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

        self.validar_parametros(duracion, cantidad)

        return self._calcular_total(
            self.precio_dia,
            duracion,
            impuesto,
            descuento,
            cantidad
        )

    def describir_servicio(self) -> str:

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
    Administra las asesorías especializadas.
    El cobro se realiza por hora.
    """

    def __init__(
        self,
        identificador: str,
        nombre: str,
        especialidad: str,
        precio_hora: float,
        disponible: bool = True
    ) -> None:

        super().__init__(
            identificador,
            nombre,
            "Servicio de asesoría especializada."
            ,
            disponible
        )

        self.__especialidad = self._validar_texto(
            especialidad, "Especialidad"
        )

        self.__precio_hora = self._validar_numero_positivo(
            precio_hora, "Precio por hora"
        )

    @property
    def especialidad(self) -> str:
        return self.__especialidad

    @property
    def precio_hora(self) -> float:
        return self.__precio_hora

    def validar_parametros(self, duracion: float) -> None:

        self._validar_disponibilidad()

        self._validar_numero_positivo(
            duracion, "Duración"
        )

    def calcular_costo(
        self,
        duracion: float,
        impuesto: float = 0,
        descuento: float = 0
    ) -> float:

        self.validar_parametros(duracion)

        return self._calcular_total(
            self.precio_hora,
            duracion,
            impuesto,
            descuento
        )

    def describir_servicio(self) -> str:

        return (
            f"ASESORIA ESPECIALIZADA | "
            f"ID: {self.identificador} | "
            f"Nombre: {self.nombre} | "
            f"Especialidad: {self.especialidad} | "
            f"Precio por hora: ${self.precio_hora:,.2f} | "
            f"Disponible: {self.disponible}"
        )
