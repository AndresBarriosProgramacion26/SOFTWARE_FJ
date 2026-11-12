# SOFTWARE FJ
## Sistema Integral de Gestión de Clientes, Servicios y Reservas

- **Universidad:** Universidad Nacional Abierta y a Distancia (UNAD)
- **Escuela:** Ciencias Básicas, Tecnología e Ingeniería (ECBTI)
- **Curso:** Programación
- **Código:** 213023
- **Actividad:** Fase 4 - Prácticas simuladas

---

## 1. Descripción del proyecto

Software FJ es una aplicación desarrollada en Python que permite administrar clientes, servicios y reservas mediante programación orientada a objetos.

El sistema ofrece tres tipos de servicios:

- Reservas de salas.
- Alquiler de equipos.
- Asesorías especializadas.

El proyecto busca implementar una aplicación organizada, modular y robusta, capaz de controlar errores y continuar funcionando ante situaciones inesperadas.

## 2. Objetivo general

Desarrollar un sistema integral de gestión de clientes, servicios y reservas, aplicando los principios de programación orientada a objetos y mecanismos avanzados de manejo de excepciones.

## 3. Tecnologías utilizadas

- Python 3.11.9.
- Visual Studio Code.
- Git.
- GitHub.

No se utilizan bases de datos ni librerías externas. La información se administra mediante objetos y listas de Python.

Los archivos se utilizan exclusivamente para registrar eventos y errores.

## 4. Funcionalidades principales

### Gestión de clientes
- Registro de clientes.
- Validación de datos personales.
- Protección de atributos.
- Búsqueda por documento e identificador.
- Prevención de registros duplicados.

### Gestión de servicios
- Reservas de salas.
- Alquiler de equipos.
- Asesorías especializadas.
- Validación de disponibilidad.
- Cálculo de costos.

### Gestión de reservas
- Creación de reservas.
- Procesamiento de operaciones.
- Confirmación y cancelación.
- Control de horarios de salas.
- Control de existencias de equipos.
- Cálculo de impuestos y descuentos.

### Manejo de excepciones
- Excepciones personalizadas.
- Bloques try/except.
- Bloques try/except/else.
- Bloques try/except/finally.
- Encadenamiento de excepciones.
- Registro de errores en archivos LOG.

## 5. Estructura del proyecto

```text
SOFTWARE_FJ/
│
├── software_fj/
│   ├── __init__.py
│   ├── entidades.py
│   ├── servicios.py
│   ├── reservas.py
│   ├── sistema.py
│   ├── excepciones.py
│   └── registro.py
│
├── tests/
│   ├── __init__.py
│   ├── pruebas.py
│   └── operaciones_completas.py
│
├── logs/
│   └── .gitkeep
│
├── main.py
├── README.md
└── .gitignore
```

## 6. Instalación y ejecución

### Requisitos

- Python 3.11 o superior.
- Git.
- Visual Studio Code (recomendado).

### Preparar el entorno virtual

En la terminal de la carpeta principal del proyecto:

```powershell
py -3.11 -m venv .venv
```

Activar el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Ejecutar la aplicación

```powershell
python main.py
```

### Ejecutar las pruebas generales

```powershell
python -m tests.pruebas
```

### Ejecutar las pruebas de aceptación

```powershell
python -m tests.operaciones_completas
```

### Comprobar la sintaxis

```powershell
python -m py_compile main.py software_fj/*.py
```

## 7. Pruebas realizadas

Se desarrollaron pruebas para comprobar:

- Registro válido e inválido de clientes.
- Creación válida e inválida de servicios.
- Detección de registros duplicados.
- Procesamiento de reservas.
- Confirmación y cancelación.
- Control de horarios ocupados.
- Control de existencias de equipos.
- Manejo de excepciones.
- Registro de eventos y errores.

Las pruebas de aceptación implementadas contemplan 14 operaciones y, en la ejecución validada durante el desarrollo, las 14 finalizaron correctamente.

## 8. Almacenamiento de información

La aplicación administra clientes, servicios y reservas mediante objetos y listas en memoria.

No utiliza motores de bases de datos.

El archivo `logs/sistema.log` registra los acontecimientos y errores relevantes durante la ejecución.

Los registros del sistema se conservan en el archivo LOG. Los objetos y listas se mantienen únicamente mientras la aplicación está ejecutándose.

## 9. Responsabilidad del desarrollo

Responsable principal: Andres Felipe Barrios De La Vega.

Integrantes y aportes adicionales: El desarrollo fue realizado en su totalidad por el responsable principal. Los demás integrantes del grupo no se reportaron en el foro colaborativo durante el periodo de la actividad.

## 10. Repositorio

Enlace de GitHub: https://github.com/AndresBarriosProgramacion26/SOFTWARE_FJ

## 11. Referencias bibliográficas

Van Rossum, G., & Drake Jr., F. L. (2024). *El tutorial de Python*. Python Software Foundation. https://docs.python.org/es/3.12/tutorial/index.html

Cuevas Álvarez, A. (2016). *Python 3: curso práctico*. RA-MA Editorial.

Mishra, P. (2024). *Ultimate Git and GitHub for Modern Software Development*. Orange Education Pvt Ltd.

Silva, F. D. (2025). *Basics of using GitHub* [Objeto virtual de información]. Repositorio Institucional UNAD. https://repository.unad.edu.co/handle/10596/75882

Zambrano, J. P. (2025). *Introducción al uso de GitHub* [Objeto virtual de información]. Repositorio Institucional UNAD. https://repository.unad.edu.co/handle/10596/75876
