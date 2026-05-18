# Comparativa y Auditoría del Sistema vs. PDF de Requerimientos

Este documento presenta una comparación detallada entre el **estado actual del sistema** y los requerimientos especificados en el documento **"Sistema de Gestión de seguros (3 estudiantes).pdf"**. El objetivo es identificar qué elementos están completamente implementados, cuáles están incompletos o ausentes, y cómo podemos optimizar el sistema para cumplir al 100% con la entrega académica.

---

## 📊 Resumen Ejecutivo de la Auditoría

| Componente | Requerimiento del PDF | Estado Actual | Diagnóstico y Acción Requerida |
| :--- | :--- | :--- | :--- |
| **Diseño Físico (DB)** | Llaves PK/FK, Índices, Restricciones y Triggers. | Parcialmente Completo | Faltan índices de búsqueda y **triggers automáticos** para integridad y reglas de negocio. |
| **Catálogos Semilla** | Tipos de seguro (vida, hogar, auto, salud), reaseguro (proporcional, no proporcional), estados, etc. | Incompleto | Faltan tipos como "Salud", y "Vencida" en estados de póliza. El catálogo de reaseguros no refleja "proporcional/no proporcional" sino subtipos específicos. |
| **Gestión (CRUD)** | Pólizas, reclamaciones, reaseguradoras, clientes de forma abierta y relacional. | Completo | Flujos CRUD en Streamlit funcionales con validaciones en Python. |
| **Alertas (Req. 8)** | Alertas para pólizas próximas a vencer y reclamaciones pendientes. | Completo | Implementado dinámicamente en la interfaz de Streamlit (`app.py` y `validaciones.py`). |
| **Salidas y Reportes** | 11 Listados Generales + 6 Reportes Específicos (Total 17). | **Crucial Hallazgo** | El archivo activo (`ui_reportes.py`) solo muestra **6 reportes**. Sin embargo, existe un archivo inactivo (`reportes.py`) que tiene los **17 reportes** pero sin el sistema de guardado histórico. |

---

## 🔍 Análisis Detallado por Componente

### 1. Base de Datos Física (SQL & Triggers)

El diseño físico está bien estructurado en `db/SEGUROS_BD.sql` con llaves primarias y foráneas adecuadas, pero adolece de la falta de elementos de rendimiento y automatización requeridos en la página 4 del PDF:

> [!WARNING]
> **Elementos Faltantes en el Diseño Físico:**
> * **Índices de Búsqueda:** El PDF exige *"utilizar índices de búsqueda para optimizar el rendimiento del sistema"*. Actualmente no hay índices explícitos creados para campos muy consultados (como `cliente.no_identificacion`, `cliente.nombre`, `poliza.idcliente`, `reclamacion.idpoliza`, etc.).
> * **Disparadores (Triggers):** El PDF exige *"implementar restricciones y disparadores para mantener la integridad de los datos"*. Actualmente, no existe ningún trigger (`CREATE TRIGGER`) en la base de datos PostgreSQL.

#### Propuesta de Triggers e Índices a Implementar:
1. **Trigger de Validación de Fechas:** Evitar que una póliza se registre con `fecha_fin < fecha_inicio`.
2. **Trigger de Validación de Reclamaciones:** Evitar que se cree una reclamación para una póliza que no esté en estado 'Activa' o donde la `fecha_siniestro` esté fuera del rango de vigencia de la póliza.
3. **Trigger de Control de Indemnizaciones:** Asegurar que el total indemnizado no supere la prima o el monto total asegurado de la póliza.
4. **Índices clave:**
   ```sql
   CREATE INDEX idx_cliente_identificacion ON cliente(no_identificacion);
   CREATE INDEX idx_poliza_cliente ON poliza(idcliente);
   CREATE INDEX idx_reclamacion_poliza ON reclamacion(idpoliza);
   ```

---

### 2. Consistencia en Catálogos Semilla

Existen discrepancias menores pero notables entre los nombres de los estados y catálogos en el script SQL y lo especificado textualmente por el PDF:

* **Tipos de Seguro:** El PDF lista *"seguro de vida, seguro de hogar, seguro de auto y seguro de salud"*. El catálogo SQL actual (`tipo_seguro`) solo contiene *Vida, Automóvil y Hogar*. Falta **Salud**.
* **Estados de Póliza:** El PDF define los estados *"activa, vencida, cancelada"*. La tabla actual (`estado_poliza`) inserta *Activa, Inactiva y Cancelada*. Falta explícitamente el término **Vencida** (en su lugar se usa "Inactiva" o se valida por fecha, pero académicamente debería llamarse "Vencida" según el documento).
* **Tipos de Reaseguro:** El PDF requiere *"tipo de reaseguro ofrecido (proporcional, no proporcional)"*. La tabla actual (`tipo_reaseguro`) inserta *Cuota Parte, Excedente y Stop Loss*. Debería ajustarse para incluir o categorizar por Proporcional / No Proporcional.
* **Tipos de Siniestro:** El PDF menciona *"accidente, enfermedad, desastre natural, etc."*. En SQL se tiene *Accidente de tráfico, Robo, Incendio e Inundación*. Falta **Enfermedad** para soportar el seguro de Salud.
* **Estados de Reclamación:** El PDF pide *"en proceso, aprobada, rechazada"*. La base de datos tiene *Presentada, Aprobada y Rechazada*. Esto genera un conflicto en el código: la función `obtener_reclamaciones_pendientes` busca `'En proceso'`, pero en la DB solo existe `'Presentada'`.

---

### 3. La Situación de los Reportes (El Crucial Hallazgo 💡)

En tu carpeta `ui/` hay dos archivos para reportes:
1. `ui/ui_reportes.py` (Activo en `app.py`):
   * **Ventajas:** Tiene una interfaz hermosa con tabs, gráficos interactivos con Streamlit, y persiste/guarda los reportes generados como JSON en la tabla `reporte_generado` de la DB (permitiendo un histórico de reportes).
   * **Desventajas:** Solo implementa **6 reportes** (Ingresos Mensuales, Ficha Agencia, Ficha Cliente, Ficha Reaseguradora, Pólizas por Período, Estado Reclamaciones).
2. `ui/reportes.py` (Inactivo):
   * **Ventajas:** ¡Tiene implementados los **17 reportes requeridos por el PDF** de forma estructurada!
   * **Desventajas:** No usa tabs, no guarda los reportes en el histórico de la DB, y las llamadas a SQL se hacen directamente con consultas CRUD básicas sin la persistencia JSON.

#### Comparativa de Cobertura de Reportes:

| Reporte / Salida en PDF | ¿Está en `ui_reportes.py` (Activo)? | ¿Está en `reportes.py` (Inactivo)? | Estado de Cumplimiento |
| :--- | :---: | :---: | :---: |
| **1. Listado de Clientes** (Agrupado por país, pólizas activas, total primas) | ❌ |  (Fila 48) | **Inactivo** |
| **2. Listado de Pólizas** (Agrupado por tipo de seguro) | ❌ |  (Fila 89) | **Inactivo** |
| **3. Listado de Reclamaciones** (Detallado con estados e indemnizaciones) | ❌ |  (Fila 130) | **Inactivo** |
| **4. Listado de Reaseguradoras** (Con participaciones) | ❌ |  (Fila 158) | **Inactivo** |
| **5. Listado de Pólizas Vencidas** | ❌ |  (Fila 206) | **Inactivo** |
| **6. Listado de Clientes con Pólizas Canceladas** | ❌ |  (Fila 241) | **Inactivo** |
| **7. Resumen de Pólizas por Tipo de Seguro** | ❌ |  (Fila 275) | **Inactivo** |
| **8. Resumen de Reclamaciones por Estado** | ❌ |  (Fila 307) | **Inactivo** |
| **9. Listado de Ingresos Mensuales** |  |  (Fila 339) | Activo |
| **10. Clientes con Reclamaciones Aprobadas** | ❌ |  (Fila 375) | **Inactivo** |
| **11. Clientes con Reclamaciones Rechazadas** | ❌ |  (Fila 410) | **Inactivo** |
| **12. Ficha de la Agencia de Seguros** |  |  (Fila 445) | Activo |
| **13. Ficha de un Cliente Determinado** |  |  (Fila 467) | Activo |
| **14. Ficha de una Reaseguradora Asociada** |  |  (Fila 548) | Activo |
| **15. Pólizas Emitidas en un Período** |  |  (Fila 601) | Activo |
| **16. Reporte de Estado de las Reclamaciones** |  |  (Fila 646) | Activo |
| **17. Ingresos Mensuales por Primas** (Con gráfico de barras) |  |  (Fila 674) | Activo |

---

## 🛠️ Plan de Acción Recomendado

Para que el sistema quede **100% fiel al PDF** y sea una entrega académica sobresaliente, te propongo realizar las siguientes mejoras consecutivas:

### Fase A: Base de Datos y Catálogos (SQL)
1. **Corregir las semillas en `db/SEGUROS_BD.sql`:**
   * Agregar el tipo de seguro *"Salud"*.
   * Ajustar el estado de póliza `'Inactiva'` por `'Vencida'`.
   * Agregar el tipo de siniestro *"Enfermedad"*.
   * Cambiar el estado de reclamación `'Presentada'` por `'En proceso'` (o asegurar que ambos se soporten sin provocar errores en `validaciones.py`).
2. **Crear Índices de búsqueda** en PostgreSQL para optimizar consultas de reportes.
3. **Desarrollar Triggers en PL/pgSQL** en `db/SEGUROS_BD.sql` para validaciones de pólizas inactivas/vencidas en reclamaciones y control de fechas.

### Fase B: Unificación del Módulo de Reportes
1. **Activar los 17 reportes:** En lugar de limitar la vista de reportes en Streamlit, unificar lo mejor de ambos mundos. 
2. Rediseñar `pagina_reportes()` para que use un control de selección premium (un dropdown elegante o agrupado por tabs: *"Listados Generales"*, *"Resúmenes y Gráficos"*, *"Fichas Específicas"* y *"Historial Guardado"*).
3. Asegurar que **los 17 reportes** cuenten con la opción de **"Generar Reporte" (guardar en DB como JSON)** e imprimirse/visualizarse de forma premium.

---

¿Qué te parece este diagnóstico? ¿Por cuál de estas fases o mejoras te gustaría que comencemos a trabajar en el sistema?
