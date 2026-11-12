# ==========================================================
# UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD
# ESCUELA DE CIENCIAS BÁSICAS, TECNOLOGÍA E INGENIERÍA - ECBTI
# SOFTWARE FJ - PAQUETE DE PRUEBAS DEL SISTEMA
# ==========================================================

"""
Paquete de pruebas para el sistema de gestión Software FJ.

Este paquete agrupa los módulos de prueba unitaria, pruebas de integración
y escenarios de aceptación integral diseñados para verificar la calidad,
robustez y fiabilidad de todos los componentes del sistema.

Módulos incluidos en este paquete:
- pruebas: Contiene pruebas unitarias enfocadas en validar la creación
  de entidades (clientes, servicios, reservas), la consistencia de
  encapsulamiento de atributos, los límites de validación de campos
  (nombres, documentos, correos, teléfonos), la correcta activación
  de excepciones del dominio y la persistencia en archivos de bitácora.
- operaciones_completas: Pruebas de integración de extremo a extremo (E2E)
  que ejecutan flujos de trabajo completos del negocio, simulando el
  registro secuencial de clientes, el aprovisionamiento de servicios,
  la programación de reservas, transiciones de estado, cálculo de costos
  totales, y cancelaciones según políticas empresariales.
"""
