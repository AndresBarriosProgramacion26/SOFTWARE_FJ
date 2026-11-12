
from abc import ABC, abstractmethod
import re


# ==================================================
# CLASE ABSTRACTA: ENTIDAD
# ==================================================

class Entidad(ABC):
    """
    Representa una entidad general del sistema.
    Es una clase abstracta que sirve como base
    para otras clases.
    """

    def __init__(self, identificador: str) -> None:
        self.__identificador = self._validar_texto(
            identificador, "Identificador"
        )

    @staticmethod
    def _validar_texto(valor: str, campo: str) -> str:
        """Comprueba que un dato sea texto y no esté vacío."""

        if not isinstance(valor, str):
            raise TypeError(f"{campo} debe ser un texto.")

        valor = valor.strip()

        if not valor:
            raise ValueError(f"{campo} no puede estar vacío.")

        return valor

    @property
    def identificador(self) -> str:
        """Permite consultar el identificador."""
        return self.__identificador

    @abstractmethod
    def obtener_informacion(self) -> str:
        """Obliga a las clases hijas a implementar este método."""
        pass


# ==================================================
# CLASE CLIENTE
# ==================================================

class Cliente(Entidad):
    """
    Representa un cliente de Software FJ.
    Hereda de Entidad y valida sus datos personales.
    """

    def __init__(
        self,
        identificador: str,
        nombre: str,
        documento: str,
        correo: str,
        telefono: str
    ) -> None:

        super().__init__(identificador)

        self.__nombre = self._validar_nombre(nombre)
        self.__documento = self._validar_documento(documento)
        self.__correo = self._validar_correo(correo)
        self.__telefono = self._validar_telefono(telefono)

    # ----------------------------------------------
    # VALIDACIONES
    # ----------------------------------------------

    @staticmethod
    def _validar_nombre(nombre: str) -> str:

        nombre = Entidad._validar_texto(nombre, "Nombre")
        nombre = " ".join(nombre.split())

        if not 2 <= len(nombre) <= 80:
            raise ValueError(
                "El nombre debe tener entre 2 y 80 caracteres."
            )

        if not all(
            caracter.isalpha() or caracter in " -'’"
            for caracter in nombre
        ):
            raise ValueError(
                "El nombre solo puede contener letras, "
                "espacios y guiones o apóstrofes."
            )

        return nombre

    @staticmethod
    def _validar_documento(documento: str) -> str:

        documento = Entidad._validar_texto(
            documento, "Documento"
        )

        documento = documento.replace(" ", "")

        if not 5 <= len(documento) <= 20:
            raise ValueError(
                "El documento debe tener entre 5 y 20 caracteres."
            )

        if (
            not documento[0].isalnum()
            or not documento[-1].isalnum()
            or not all(
                caracter.isalnum() or caracter == "-"
                for caracter in documento
            )
        ):
            raise ValueError(
                "El documento contiene caracteres no permitidos."
            )

        return documento

    @staticmethod
    def _validar_correo(correo: str) -> str:

        correo = Entidad._validar_texto(correo, "Correo")

        patron = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

        if not re.fullmatch(patron, correo):
            raise ValueError(
                "El formato del correo electrónico no es válido."
            )

        return correo.lower()

    @staticmethod
    def _validar_telefono(telefono: str) -> str:

        telefono = Entidad._validar_texto(
            telefono, "Teléfono"
        )

        telefono_limpio = re.sub(r"[\s().-]", "", telefono)

        if telefono_limpio.startswith("+"):
            digitos = telefono_limpio[1:]
        else:
            digitos = telefono_limpio

        if not digitos.isdigit() or not 7 <= len(digitos) <= 15:
            raise ValueError(
                "El teléfono debe contener entre 7 y 15 dígitos."
            )

        return telefono_limpio

    # ----------------------------------------------
    # PROPIEDADES: ENCAPSULACIÓN
    # ----------------------------------------------

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self.__nombre = self._validar_nombre(valor)

    @property
    def documento(self) -> str:
        return self.__documento

    @documento.setter
    def documento(self, valor: str) -> None:
        self.__documento = self._validar_documento(valor)

    @property
    def correo(self) -> str:
        return self.__correo

    @correo.setter
    def correo(self, valor: str) -> None:
        self.__correo = self._validar_correo(valor)

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        self.__telefono = self._validar_telefono(valor)

    # ----------------------------------------------
    # MÉTODO HEREDADO DE ENTIDAD
    # ----------------------------------------------

    def obtener_informacion(self) -> str:

        return (
            f"ID: {self.identificador} | "
            f"Cliente: {self.nombre} | "
            f"Documento: {self.documento} | "
            f"Correo: {self.correo} | "
            f"Teléfono: {self.telefono}"
        )
