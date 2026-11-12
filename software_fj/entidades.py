# ==========================================================
# UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD
# ESCUELA DE CIENCIAS BÁSICAS, TECNOLOGÍA E INGENIERÍA - ECBTI
# SOFTWARE FJ - MÓDULO DE MODELOS Y ENTIDADES PRINCIPALES
# ==========================================================

"""
Módulo de entidades principales del sistema Software FJ.

Este módulo define la estructura de clases del modelo de dominio, aplicando
los cuatro pilares fundamentales de la Programación Orientada a Objetos (POO):
1. Abstracción: Mediante la clase base abstracta `Entidad` que establece el
   contrato y comportamiento esencial de cualquier objeto identificable.
2. Encapsulamiento: Ocultando los atributos internos mediante nombres privados
   (doble guion bajo `__`) y controlando el acceso a través de métodos de
   propiedad (@property y @setter) con validaciones rigurosas.
3. Herencia: Especializando la clase `Cliente` a partir de `Entidad`.
4. Polimorfismo: Definiendo el método abstracto `obtener_informacion`, cuya
   implementación concreta es provista por cada subclase.

Manejo de excepciones:
Todas las validaciones de datos en este módulo aseguran la integridad de las
entradas; las discrepancias de tipo lanzan `TypeError`, mientras que los valores
fuera de rango, con caracteres ilegales o formatos inválidos lanzan
`DatoInvalidoError`, una excepción propia del dominio Software FJ.
"""

from abc import ABC, abstractmethod
import re

# Se importa la excepción de dominio para datos que no cumplen las restricciones de negocio.
from software_fj.excepciones import DatoInvalidoError


# ==========================================================
# CLASE ABSTRACTA: ENTIDAD
# ==========================================================

class Entidad(ABC):
    """
    Clase base abstracta que representa una entidad general del sistema Software FJ.

    Esta clase define la estructura fundamental compartida por todos los
    elementos del dominio que requieren una identificación unívoca dentro del
    sistema (como clientes, servicios y reservas). Implementa la validación
    centralizada de cadenas de texto y exige que las clases derivadas
    proporcionen su propia representación de información mediante el método
    polimórfico `obtener_informacion`.

    Attributes:
        __identificador (str): Código o identificador único e inmutable de la entidad.
    """

    def __init__(self, identificador: str) -> None:
        """
        Inicializa una nueva instancia de la clase Entidad.

        Args:
            identificador (str): Cadena de texto que identifica unívocamente a la entidad.

        Raises:
            TypeError: Si el identificador no es una instancia de la clase str.
            DatoInvalidoError: Si el identificador está vacío o compuesto solo por espacios.
        """
        # Se valida que el identificador sea un texto válido y no vacío antes de almacenarlo.
        # Se guarda en un atributo privado con doble guion bajo para impedir modificaciones externas directas.
        self.__identificador = self._validar_texto(
            identificador, "Identificador"
        )

    # ------------------------------------------------------
    # MÉTODO ESTÁTICO DE VALIDACIÓN GENERAL
    # ------------------------------------------------------

    @staticmethod
    def _validar_texto(valor: str, campo: str) -> str:
        """
        Comprueba que un dato recibido sea de tipo texto (str) y contenga caracteres legibles.

        Este método utilitario es empleado por todas las entidades y servicios del
        sistema para asegurar la validez preliminar de cualquier parámetro de texto,
        eliminando espacios marginales innecesarios antes de realizar validaciones específicas.

        Args:
            valor (str): Valor recibido que se desea validar.
            campo (str): Nombre descriptivo del campo evaluado (utilizado para mensajes de error).

        Returns:
            str: La cadena de texto procesada sin espacios en blanco al inicio ni al final.

        Raises:
            TypeError: Si el valor suministrado no es una cadena de texto (str).
            DatoInvalidoError: Si la cadena tras eliminar espacios queda vacía.
        """
        # Se comprueba que el tipo de dato sea estrictamente una cadena de caracteres.
        # Si no lo es, se interrumpe la ejecución con TypeError respetando el estándar de Python.
        if not isinstance(valor, str):
            raise TypeError(f"{campo} debe ser un texto.")

        # Se eliminan los posibles espacios en blanco en los extremos del texto.
        valor = valor.strip()

        # Se verifica que la cadena no haya quedado completamente vacía tras la limpieza.
        # Si está vacía, se lanza la excepción de dominio DatoInvalidoError.
        if not valor:
            raise DatoInvalidoError(f"{campo} no puede estar vacío.")

        # Retorna el texto saneado para su posterior utilización o asignación.
        return valor

    # ------------------------------------------------------
    # PROPIEDADES (ENCAPSULAMIENTO)
    # ------------------------------------------------------

    @property
    def identificador(self) -> str:
        """
        Obtiene el identificador único de la entidad.

        Returns:
            str: El código de identificación inmutable de la entidad.
        """
        # Se retorna el valor del atributo privado.
        # Al no definir un método setter, el identificador funciona en modo de solo lectura (inmutable).
        return self.__identificador

    # ------------------------------------------------------
    # MÉTODO ABSTRACTO (CONTRATO POLIMÓRFICO)
    # ------------------------------------------------------

    @abstractmethod
    def obtener_informacion(self) -> str:
        """
        Genera una cadena de texto con la información detallada de la entidad.

        Este método define el contrato obligatorio que todas las subclases concretas
        deben sobreescribir, garantizando una representación textual homogénea y
        polimórfica en todo el sistema.

        Returns:
            str: Descripción completa de los atributos del objeto formateada para visualización.
        """
        pass


# ==========================================================
# CLASE CONCRETA: CLIENTE
# ==========================================================

class Cliente(Entidad):
    """
    Representa a un cliente registrado en la plataforma Software FJ.

    Esta clase hereda de `Entidad` y encapsula la información de contacto y
    datos personales de los usuarios del sistema. Cada uno de sus atributos
    cuenta con validaciones rigurosas aplicadas tanto en el constructor como
    en los métodos modificadores (setters), asegurando que el estado interno
    siempre cumpla con los estándares del negocio.

    Attributes:
        identificador (str): Código único heredado que identifica al cliente (ej: CLI-001).
        nombre (str): Nombre completo del cliente, normalizado y sin caracteres ilegales.
        documento (str): Documento de identidad nacional o pasaporte alfanumérico.
        correo (str): Dirección de correo electrónico normalizada a minúsculas con formato RFC válido.
        telefono (str): Número telefónico normalizado con dígitos entre 7 y 15 cifras.
    """

    def __init__(
        self,
        identificador: str,
        nombre: str,
        documento: str,
        correo: str,
        telefono: str
    ) -> None:
        """
        Inicializa una nueva instancia de la clase Cliente con sus datos personales.

        Args:
            identificador (str): Identificador único para el cliente en el sistema.
            nombre (str): Nombre completo del cliente (entre 2 y 80 caracteres).
            documento (str): Número de documento de identificación (entre 5 y 20 caracteres).
            correo (str): Dirección de correo electrónico válida (formato usuario@dominio.ext).
            telefono (str): Número de teléfono nacional o internacional (entre 7 y 15 dígitos).

        Raises:
            TypeError: Si alguno de los argumentos no corresponde a una cadena de texto (str).
            DatoInvalidoError: Si alguno de los datos incumple las reglas de formato, rango o caracteres.
        """
        # Se invoca el constructor de la clase padre Entidad para inicializar y validar el identificador.
        super().__init__(identificador)

        # Se validan y asignan cada uno de los atributos personales mediante métodos especializados.
        # Al almacenarse en atributos con doble guion bajo (__), se protege el encapsulamiento.
        self.__nombre = self._validar_nombre(nombre)
        self.__documento = self._validar_documento(documento)
        self.__correo = self._validar_correo(correo)
        self.__telefono = self._validar_telefono(telefono)

    # ------------------------------------------------------
    # MÉTODOS ESTÁTICOS DE VALIDACIÓN ESPECÍFICA
    # ------------------------------------------------------

    @staticmethod
    def _validar_nombre(nombre: str) -> str:
        """
        Valida y normaliza el nombre de una persona.

        Comprueba que el nombre sea un texto válido, colapsa espacios en blanco
        múltiples entre palabras, verifica que su longitud se encuentre entre 2 y 80
        caracteres, y restringe los caracteres permitidos a letras del alfabeto,
        espacios simples, guiones y apóstrofes (útiles para nombres compuestos o extranjeros).

        Args:
            nombre (str): Nombre de la persona a validar.

        Returns:
            str: Nombre normalizado y con espacios interiores individuales.

        Raises:
            TypeError: Si el nombre no es una cadena de texto.
            DatoInvalidoError: Si la longitud no está en el rango [2, 80] o contiene caracteres ilegales.
        """
        # Se comprueba que sea un texto no vacío empleando la validación base de Entidad.
        nombre = Entidad._validar_texto(nombre, "Nombre")

        # Se eliminan los espacios redundantes internos dividiendo la cadena por palabras y reuniéndolas.
        # Esto transforma "Juan   Carlos" en "Juan Carlos".
        nombre = " ".join(nombre.split())

        # Se verifica que la longitud del nombre cumpla con los límites mínimos y máximos de negocio.
        if not 2 <= len(nombre) <= 80:
            raise DatoInvalidoError(
                "El nombre debe tener entre 2 y 80 caracteres."
            )

        # Se comprueba que cada carácter sea una letra (alfabético) o un carácter de separación permitido.
        # Se admiten espacios, guiones normales y apóstrofes ortográficos o tipográficos (ej: D'Angelo, O’Connor).
        if not all(
            caracter.isalpha() or caracter in " -'’"
            for caracter in nombre
        ):
            raise DatoInvalidoError(
                "El nombre solo puede contener letras, "
                "espacios y guiones o apóstrofes."
            )

        # Se retorna el nombre completamente validado y normalizado.
        return nombre

    @staticmethod
    def _validar_documento(documento: str) -> str:
        """
        Valida y normaliza el documento de identificación de un cliente.

        Elimina cualquier espacio en blanco intermedio, verifica que la longitud
        resultante esté comprendida entre 5 y 20 caracteres, y comprueba que
        esté compuesto únicamente por caracteres alfanuméricos y guiones, exigiendo
        que tanto el primer como el último carácter sean necesariamente alfanuméricos.

        Args:
            documento (str): Cadena que contiene el documento a evaluar.

        Returns:
            str: Documento de identidad limpio y sin espacios en blanco.

        Raises:
            TypeError: Si el documento no es una cadena de texto.
            DatoInvalidoError: Si la longitud está fuera del rango [5, 20] o contiene símbolos no permitidos.
        """
        # Se valida que el documento sea texto no vacío a través del validador de Entidad.
        documento = Entidad._validar_texto(
            documento, "Documento"
        )

        # Se eliminan todos los espacios en blanco que el usuario haya podido introducir entre los números.
        documento = documento.replace(" ", "")

        # Se valida que la cantidad de caracteres esté dentro del rango legal para documentos (cédula, pasaporte, etc.).
        if not 5 <= len(documento) <= 20:
            raise DatoInvalidoError(
                "El documento debe tener entre 5 y 20 caracteres."
            )

        # Se valida la estructura del documento:
        # 1. documento[0].isalnum(): El primer carácter debe ser una letra o un número (no puede iniciar con guion).
        # 2. documento[-1].isalnum(): El último carácter debe ser letra o número (no puede finalizar con guion).
        # 3. all(caracter.isalnum() or caracter == '-' ...): Solo permite letras, números o guiones en el cuerpo.
        if (
            not documento[0].isalnum()
            or not documento[-1].isalnum()
            or not all(
                caracter.isalnum() or caracter == "-"
                for caracter in documento
            )
        ):
            raise DatoInvalidoError(
                "El documento contiene caracteres no permitidos."
            )

        # Retorna el documento debidamente depurado.
        return documento

    @staticmethod
    def _validar_correo(correo: str) -> str:
        """
        Valida que una dirección de correo electrónico cumpla con el estándar RFC aplicable.

        Utiliza una expresión regular (regex) para evaluar la estructura completa del
        correo electrónico: nombre de usuario, arroba (@), dominio principal y extensión
        de dominio de nivel superior (TLD). Finalmente, normaliza la cadena resultante
        a minúsculas para garantizar comparaciones consistentes en la base de datos.

        Args:
            correo (str): Dirección de correo electrónico que se someterá a validación.

        Returns:
            str: Dirección de correo electrónico validada y convertida a minúsculas.

        Raises:
            TypeError: Si el correo no es una cadena de texto.
            DatoInvalidoError: Si la estructura del correo no coincide con la expresión regular.
        """
        # Se comprueba que el correo sea una cadena de texto no vacía.
        correo = Entidad._validar_texto(correo, "Correo")

        # Expresión regular para validar el formato de correo electrónico:
        # ^                 : Inicio estricto de la cadena.
        # [A-Za-z0-9._%+-]+ : Uno o más caracteres alfanuméricos o símbolos estándar para la parte local (usuario).
        # @                 : Carácter arroba obligatorio que delimita el usuario del nombre de dominio.
        # [A-Za-z0-9.-]+    : Uno o más caracteres alfanuméricos, puntos o guiones para el nombre del servidor o dominio.
        # \.                : Punto literal obligatorio que separa el nombre del dominio de su extensión.
        # [A-Za-z]{2,}      : Dominio de nivel superior (TLD) compuesto por al menos 2 caracteres alfabéticos (ej: com, co, edu, org).
        # $                 : Fin estricto de la cadena, asegurando que no existan caracteres residuales al final.
        patron = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

        # Se evalúa la coincidencia total de la cadena frente a la expresión regular mediante fullmatch.
        if not re.fullmatch(patron, correo):
            raise DatoInvalidoError(
                "El formato del correo electrónico no es válido."
            )

        # Se normaliza la dirección a minúsculas para prevenir problemas de duplicados por mayúsculas/minúsculas.
        return correo.lower()

    @staticmethod
    def _validar_telefono(telefono: str) -> str:
        """
        Valida y normaliza el número de teléfono del cliente.

        Remueve caracteres decorativos habituales en la notación telefónica (espacios,
        paréntesis, puntos y guiones), verifica el uso correcto del prefijo internacional
        opcional (+), y corrobora que la cantidad de dígitos numéricos se encuentre
        en el estándar internacional de telecomunicaciones (entre 7 y 15 cifras).

        Args:
            telefono (str): Número telefónico original ingresado por el usuario.

        Returns:
            str: Número de teléfono normalizado (dígitos continuos precedidos por + si aplica).

        Raises:
            TypeError: Si el teléfono no es una cadena de texto.
            DatoInvalidoError: Si contiene caracteres no autorizados o la cantidad de dígitos
                se encuentra fuera del rango internacional [7, 15].
        """
        # Se valida que el teléfono sea una cadena de texto no vacía.
        telefono = Entidad._validar_texto(
            telefono, "Teléfono"
        )

        # Expresión regular para limpiar símbolos de formato habituales en números telefónicos:
        # [\s().-] es una clase de caracteres que coincide con:
        # \s : Cualquier espacio en blanco (espacios, tabulaciones).
        # () : Paréntesis comúnmente usados para encerrar códigos de área o ciudad.
        # .  : Puntos usados en formatos europeos o modernos como separadores.
        # -  : Guiones comúnmente usados para dividir bloques de dígitos.
        # Se reemplazan todos estos caracteres por la cadena vacía "", conservando solo dígitos y el prefijo '+'.
        telefono_limpio = re.sub(r"[\s().-]", "", telefono)

        # Se gestiona el prefijo internacional '+' en caso de que esté presente al inicio del número.
        if telefono_limpio.startswith("+"):
            # Se extraen únicamente los caracteres posteriores al símbolo '+' para validar los dígitos numéricos.
            digitos = telefono_limpio[1:]
        else:
            # Si no hay prefijo '+', todos los caracteres del texto limpio deben corresponder a dígitos numéricos.
            digitos = telefono_limpio

        # Se corrobora que la totalidad de los caracteres restantes sean estrictamente numéricos (0-9)
        # y que la longitud total de dígitos se encuentre entre 7 y 15 (conforme a la recomendación ITU-T E.164).
        if not digitos.isdigit() or not 7 <= len(digitos) <= 15:
            raise DatoInvalidoError(
                "El teléfono debe contener entre 7 y 15 dígitos."
            )

        # Retorna el teléfono depurado listo para almacenamiento.
        return telefono_limpio

    # ------------------------------------------------------
    # PROPIEDADES Y MODIFICADORES (ENCAPSULAMIENTO POO)
    # ------------------------------------------------------

    @property
    def nombre(self) -> str:
        """
        Obtiene el nombre completo del cliente.

        Returns:
            str: El nombre del cliente.
        """
        # Lectura controlada del atributo privado __nombre.
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """
        Actualiza el nombre completo del cliente tras aplicar las validaciones correspondientes.

        Args:
            valor (str): Nuevo nombre que se asignará al cliente.

        Raises:
            TypeError: Si el valor no es una cadena de texto.
            DatoInvalidoError: Si el valor no cumple con las restricciones de longitud o caracteres.
        """
        # Se revalida el nuevo valor antes de mutar el estado interno del objeto.
        self.__nombre = self._validar_nombre(valor)

    @property
    def documento(self) -> str:
        """
        Obtiene el documento de identificación del cliente.

        Returns:
            str: El documento del cliente.
        """
        # Lectura controlada del atributo privado __documento.
        return self.__documento

    @documento.setter
    def documento(self, valor: str) -> None:
        """
        Actualiza el documento de identificación del cliente previa validación de formato.

        Args:
            valor (str): Nuevo documento que se asignará al cliente.

        Raises:
            TypeError: Si el valor no es una cadena de texto.
            DatoInvalidoError: Si el nuevo documento no cumple las restricciones de formato.
        """
        # Se ejecuta la validación del documento antes de modificar el atributo encapsulado.
        self.__documento = self._validar_documento(valor)

    @property
    def correo(self) -> str:
        """
        Obtiene la dirección de correo electrónico del cliente.

        Returns:
            str: El correo electrónico en minúsculas del cliente.
        """
        # Lectura controlada del atributo privado __correo.
        return self.__correo

    @correo.setter
    def correo(self, valor: str) -> None:
        """
        Actualiza el correo electrónico del cliente previa comprobación de formato de correo.

        Args:
            valor (str): Nueva dirección de correo que se desea registrar.

        Raises:
            TypeError: Si el valor no es una cadena de texto.
            DatoInvalidoError: Si la dirección no cumple con el patrón regex de correo válido.
        """
        # Se valida la estructura del correo electrónico antes de almacenarlo normalizado.
        self.__correo = self._validar_correo(valor)

    @property
    def telefono(self) -> str:
        """
        Obtiene el número de teléfono del cliente.

        Returns:
            str: El número telefónico depurado del cliente.
        """
        # Lectura controlada del atributo privado __telefono.
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        """
        Actualiza el número de teléfono del cliente tras su debida depuración y comprobación.

        Args:
            valor (str): Nuevo número de teléfono que se asignará al cliente.

        Raises:
            TypeError: Si el valor no es una cadena de texto.
            DatoInvalidoError: Si la cantidad de dígitos o composición numérica es inválida.
        """
        # Se limpia y valida el número de teléfono antes de sobreescribir el atributo privado.
        self.__telefono = self._validar_telefono(valor)

    # ------------------------------------------------------
    # IMPLEMENTACIÓN DEL MÉTODO POLIMÓRFICO HEREDADO
    # ------------------------------------------------------

    def obtener_informacion(self) -> str:
        """
        Genera una cadena de texto estructurada con los datos completos del cliente.

        Sobreescribe la definición abstracta de `Entidad.obtener_informacion`
        para presentar un resumen conciso y legible con el identificador,
        nombre completo, documento de identidad, correo electrónico y teléfono.

        Returns:
            str: Representación formateada con todos los datos personales del cliente.
        """
        # Se construye la representación textual formateada uniendo los atributos con separadores visuales (|).
        return (
            f"ID: {self.identificador} | "
            f"Cliente: {self.nombre} | "
            f"Documento: {self.documento} | "
            f"Correo: {self.correo} | "
            f"Teléfono: {self.telefono}"
        )
