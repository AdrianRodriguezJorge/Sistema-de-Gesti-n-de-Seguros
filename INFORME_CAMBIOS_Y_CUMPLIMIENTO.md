# INFORME HISTÓRICO DE CAMBIOS Y CUMPLIMIENTO TÉCNICO
## Sistema de Gestión de Seguros — "La Confianza"

Este informe detalla minuciosamente todas las modificaciones, correcciones, optimizaciones e incorporaciones funcionales que se han realizado en el proyecto desde el fork inicial. 

---

## 1. Modificaciones en el Diseño Físico y Esquema de Base de Datos (PostgreSQL)

Se realizó una reestructuración de la base de datos para corregir inconsistencias entre los tipos de datos requeridos por la lógica de negocio y las columnas físicas reales.

### A. Corrección y Homogeneización de Nombres de Columnas
*   **Problema inicial**: Existían discrepancias de nomenclatura entre los scripts SQL y las llamadas en las clases CRUD (ej. consultas buscando `monto` cuando la columna era `monto_pagado`, o discrepancias con `fecha_inicio` y `fecha_fin`).
*   **Solución**: Se homogeneizó la base de datos y se re-mapeó el backend para usar columnas consistentes con la base de datos PostgreSQL:
    *   `monto_pagado` (en la tabla `pago`)
    *   `monto_asegurado` y `prima_mensual` (en la tabla `poliza`)
    *   `fecha_inicio` y `fecha_fin` (en la tabla `poliza`)
    *   `fecha_pago` (en la tabla `pago`)
*   **Respaldo en la Orientación (Líneas 10-14, 28-30 del TXT)**: El PDF exige vigencias claras, costos mensuales de primas, montos totales asegurados y registros históricos de primas cobradas mensualmente.

### B. Adición de Catálogos e ID de Seguro / Siniestros
*   **Modificación**: Se insertó en la base de datos el seguro de `'Salud'` (ID 4) y el tipo de siniestro `'Enfermedad'` (ID 5). Asimismo, se configuraron adecuadamente los estados de póliza (`'Activa'`, `'Vencida'`, `'Cancelada'`) y de reclamaciones (`'En proceso'`, `'Aprobada'`, `'Rechazada'`).
*   **Respaldo en la Orientación (Líneas 11-13, 24 del TXT)**: El PDF detalla que las pólizas pueden ser de *Vida, Hogar, Auto, Salud*, y los estados de reclamaciones deben contemplar *En proceso, Aprobada, Rechazada*.

### C. Implementación de Triggers del Servidor (Lógica SQL)
Se incorporaron 4 disparadores robustos en `db/SEGUROS_BD.sql` para automatizar la integridad del negocio a nivel servidor:
1.  **`trg_validar_fechas_poliza`**: Lanza una excepción si la `fecha_fin` de una póliza es menor o igual a la `fecha_inicio`.
2.  **`trg_validar_creacion_reclamacion` (Regla 1)**: Impide el registro de reclamaciones sobre pólizas que no estén en estado `'Activa'` (por ejemplo, canceladas o vencidas).
3.  **`trg_validar_creacion_reclamacion` (Regla 2)**: Impide que la `fecha_siniestro` esté fuera del rango de vigencia contratado en la póliza.
4.  **`trg_validar_porcentaje_participacion`**: Valida que la suma acumulada de participación (%) de todas las reaseguradoras para un tipo de seguro determinado no exceda el 100%.
*   **Respaldo en la Orientación (Líneas 47-51 del TXT)**: *"Integridad de los datos: el sistema no debe permitir inconsistencias... no registrar reclamaciones de pólizas inactivas/vencidas o fechas fuera del rango de vigencia... límite de reaseguro..."*

---

## 2. Optimizaciones en la Capa del Backend y Consultas (CRUD)

Se refactorizó completamente la capa de persistencia (`db/queries_*.py`) para asegurar compatibilidad absoluta con PostgreSQL y prevenir fallos de ejecución.

### A. Borrado y Gestión en Cascada
*   **Modificación**: Se actualizaron las funciones del CRUD (especialmente en `queries_poliza.py` y `queries_reclamacion.py`) para manejar la eliminación de registros dependientes en cascada.
*   **Acción Técnica**: Al eliminar una póliza, el sistema borra de forma consistente:
    1. Pagos asociados (`pago`).
    2. Coberturas vinculadas (`poliza_cobertura`).
    3. Registro de cancelaciones (`poliza_cancelada`).
    4. Reclamaciones y sus motivos de rechazo.
*   **Respaldo en la Orientación (Líneas 47-49 del TXT)**: Enfoque estricto en la integridad relacional de la base de datos para impedir registros huérfanos.

### B. Módulo de Persistencia Histórica de Reportes
*   **Modificación**: Se creó el módulo `queries_reporte_generado.py` que interactúa con la tabla `reporte_generado`. Este sistema guarda snapshots JSON del estado completo del reporte en el momento de su creación.
*   **Respaldo en la Orientación (Líneas 33-35 del TXT)**: Requiere el almacenamiento de informes detallados con la posibilidad de recuperarlos o consultarlos de manera histórica.

---

## 3. Rediseño y Mejoras en el Frontend (Streamlit UI)

Se transformó la interfaz del sistema para dotarla de una estética premium y adaptarla a todas las salidas documentales exigidas.

### A. Consola Consolidada de Reportes (`ui_reportes.py`)
*   **Modificación**: Se agrupó el visor de reportes en 5 pestañas lógicas de navegación:
    1.  **📋 Listados Generales**: Reportes L1 a L6.
    2.  **📊 Resúmenes y Estadísticas**: Reportes L7 a L11.
    3.  **👤 Fichas Especiales**: Fichas S1 a S3 (Agencia, Cliente específico, Reaseguradora).
    4.  **📅 Reportes Paramétricos**: Filtros temporales interactivos S4 a S6.
    5.  **💾 Historial Guardado**: Panel para recargar o purgar reportes guardados en JSON desde la base de datos.
*   **Respaldo en la Orientación (Líneas 61-96 del TXT)**: Cumple uno a uno con la lista de los 17 reportes obligatorios exigidos para el software de seguros.

### B. Exportación Estilizada a PDF con ReportLab
*   **Modificación**: Se integró un motor generador de PDF que renderiza cada uno de los 17 reportes en un documento formal de descarga directa, incorporando cabeceras institucionales, tablas autoajustables y firmas de control.
*   **Respaldo en la Orientación (Líneas 59-60 del TXT)**: *"Todos los listados e informes deben poder ser presentados en pantalla y exportados a formato PDF..."*

### C. Botones Inteligentes de Acción: Cancelación de Pólizas y Rechazo de Reclamaciones
*   **Modificación del Flujo de Trabajo**: Se abandonó la edición simple convencional por un sistema de retención de histórico accionado por botones de estado en los CRUDs.
    *   **Botón "Cancelar Póliza" (`ui_polizas.py`)**: Este botón despliega de forma reactiva un subformulario solicitando obligatoriamente el **motivo de cancelación**. Al confirmar, el sistema actualiza el estado de la póliza a `'Cancelada'` y escribe el histórico en `poliza_cancelada`.
    *   **Botón "Rechazar Reclamación" (`ui_reclamaciones.py`)**: Al procesar un siniestro y cambiar su estado a `'Rechazada'`, la interfaz bloquea el guardado hasta que el operador redacte la **justificación del rechazo**, la cual se graba herméticamente en la tabla relacional `reclamacion_rechazada`.
*   **Respaldo en la Orientación (Líneas 24-26, 31-33, 44 del TXT)**: Garantiza la trazabilidad legal e histórica de los estados excepcionales (Cancelación/Rechazo) exigidos por el negocio y listados en los reportes L6 y L11.

### D. Dashboard Principal Analítico y Accesos Rápidos (`app.py` / `ui_principal.py`)
*   **Modificación**: El módulo principal de la aplicación se transformó en un **Dashboard de Comando** de alto rendimiento.
    *   **Métricas y KPIs en Vivo**: Utilizando componentes interactivos (`st.metric`), el Dashboard presenta indicadores financieros y estadísticos globales de la agencia en la página de inicio (ej. total de primas recaudadas, cantidad de clientes activos, recuento de siniestros).
    *   **Sistema de Alertas Dinámicas**: Se integró un motor inteligente que analiza la base de datos al inicio de sesión y proyecta advertencias (`st.warning` / `st.info`) en la barra lateral para pólizas con expiración temprana (menos de 30 días) y reclamaciones atascadas `'En proceso'`.
    *   **Flujo de Navegación Acelerada**: Inclusión de botones de acción rápida en la cuadrícula principal para acceder instantáneamente a los módulos de Clientes, Pólizas, Reclamaciones o Reportes.
*   **Respaldo en la Orientación (Líneas 53-56 del TXT)**: *"El sistema debe emitir alertas automáticas en la pantalla principal para avisar sobre pólizas próximas a vencerse... y reclamaciones pendientes..."* proporcionando además visibilidad abierta de la información (RF1).

### E. Control Estricto de Estado y Botones de "Cancelar Edición"
*   **Modificación**: Se incorporó un mecanismo robusto de control de estado (`st.session_state`) en absolutamente todos los formularios CRUD de la aplicación.
    *   Anteriormente, al entrar en modo de edición de un registro, el sistema retenía los estados en memoria. Esto permitía cambiar de página arrastrando variables de sesión huérfanas, lo que generaba inconsistencias visuales y colisiones al intentar guardar otros registros.
    *   Se implementaron botones explícitos de **"Cancelar Edición"** en los formularios de cada módulo. Estos botones actúan como un interruptor de seguridad que limpia inmediatamente las variables `editando` y `id_editar`, devolviendo la interfaz a su estado original de lectura/creación y bloqueando fallos de navegación cruzada.
*   **Respaldo en la Orientación (Líneas 47, 51 del TXT)**: Garantiza la "gestión limpia y robusta" de las interfaces, impidiendo colisiones de datos durante la manipulación concurrente de registros.

### F. Estilizado Global de Componentes y Alertas Nativas (Monkey-Patching)
*   **Modificación**: En lugar de depender del aspecto plano de los componentes predeterminados de Streamlit, el archivo raíz `app.py` fue modificado para sobrescribir (monkey-patch) el renderizado core:
    *   **DataFrames Dinámicos HTML**: Todas las llamadas a `st.dataframe` se interceptan y redirigen para renderizar tablas HTML estáticas (`pd.DataFrame.to_html`) enriquecidas con la paleta de colores corporativa (bordes `#D2DCB6`, hover effects `#E6EAD0`).
    *   **Alertas Estilizadas Globales**: Las notificaciones (`st.info`, `st.warning`, `st.error`, `st.success`) han sido redefinidas a nivel core para pintar contenedores HTML customizados, mejorando drásticamente el impacto visual y la armonía estética de toda la plataforma.
    *   **Scroll-to-Top Inteligente**: Se añadió un trigger oculto en JavaScript que fuerza a la interfaz a auto-desplazarse hacia arriba (Top) de manera limpia y automática cada vez que se detecta un cambio en las opciones del menú lateral.
*   **Respaldo en la Orientación (Requerimiento Transversal)**: Satisface la directriz integral de entregar una aplicación estética, moderna y con un flujo de interacción sin fricciones.

---

## 4. Matriz de Trazabilidad y Cumplimiento de Reportes (PDF vs Sistema)

| Código Reporte | Especificación del PDF (TXT) | Implementación Técnica en Código | Estado |
| :--- | :--- | :--- | :--- |
| **L1** | Listado de Clientes agrupado por país, pólizas activas y primas pagadas. | Filtro agregado PostgreSQL en `queries_reporte.py` (`L1`). | **Cumplido** 🟢 |
| **L2** | Listado de Pólizas agrupado por ramo, cliente, vigencia, prima y estado. | Consulta cruzada con unión de `tipo_seguro` y `cliente` (`L2`). | **Cumplido** 🟢 |
| **L3** | Listado de Reclamaciones con montos, siniestro, cliente y estado. | Query unificada de reclamos con `reclamacion` y `poliza` (`L3`). | **Cumplido** 🟢 |
| **L4** | Listado de Reaseguradoras y participaciones de seguros asociadas. | Mapeo de `participacion_reaseguro` agrupada por firma (`L4`). | **Cumplido** 🟢 |
| **L5** | Listado de Pólizas Vencidas con cliente, ramo y valor asegurado. | Filtro dinámico comparando `fecha_fin < CURRENT_DATE` (`L5`). | **Cumplido** 🟢 |
| **L6** | Clientes con pólizas canceladas indicando el motivo detallado. | Cruce con `poliza_cancelada` y conteo de cancelaciones (`L6`). | **Cumplido** 🟢 |
| **L7** | Resumen de pólizas por ramo con primas mensuales y monto asegurado. | Funciones SQL de agregación (`SUM`, `COUNT`) por ramo (`L7`). | **Cumplido** 🟢 |
| **L8** | Resumen de reclamaciones por estado con montos totales y cantidad. | Agrupación por `idestadoreclamacion` (`L8`). | **Cumplido** 🟢 |
| **L9** | Listado de ingresos mensuales por primas cobradas en el año fiscal. | Desglose mensual agregando la fecha de cobro (`L9`). | **Cumplido** 🟢 |
| **L10** | Clientes con reclamaciones aprobadas e indemnizaciones recibidas. | Filtro por reclamaciones con estado `'Aprobada'` (`L10`). | **Cumplido** 🟢 |
| **L11** | Clientes con reclamaciones rechazadas y justificación del rechazo. | Cruce relacional con `reclamacion_rechazada` (`L11`). | **Cumplido** 🟢 |
| **S1** | Ficha de la Agencia de Seguros con información de contacto y directivos.| Carga interactiva desde la tabla `agencia` (`S1`). | **Cumplido** 🟢 |
| **S2** | Ficha de un Cliente Determinado con pólizas activas e historial. | Selector de cliente con desglose relacional completo (`S2`). | **Cumplido** 🟢 |
| **S3** | Ficha de una Reaseguradora Asociada con su porcentaje por ramo. | Selector dinámico con gráfico de distribución por ramo (`S3`). | **Cumplido** 🟢 |
| **S4** | Reporte de pólizas emitidas en un período determinado. | Filtro paramétrico dinámico usando `BETWEEN` en `fecha_inicio` (`S4`).| **Cumplido** 🟢 |
| **S5** | Reporte de reclamaciones y sus estados en un período determinado. | Filtro temporal dinámico en `fecha_siniestro` (`S5`). | **Cumplido** 🟢 |
| **S6** | Reporte de ingresos mensuales por primas con desglose temporal. | Consulta filtrada por año fiscal con gráfico de barras (`S6`). | **Cumplido** 🟢 |

---

## 5. Pruebas y Aseguramiento de Calidad (QA)

Para validar quirúrgicamente cada cambio, se diseñó e implementó la suite de pruebas automatizadas **`test_surgical_compliance.py`** en la raíz del proyecto. 

### Resultados de Ejecución de la Suite:
1.  **Triggers de Base de Datos**: **`APROBADO`** 🟢
    *   Excepciones de PostgreSQL interceptadas correctamente al forzar vigencias negativas, pólizas inactivas, siniestros fuera de fecha o porcentajes de participación mayores al 100%.
2.  **Integridad por Eliminación en Cascada**: **`APROBADO`** 🟢
    *   Comprobación física de que eliminar registros padre limpia automáticamente los históricos en cascada sin dejar registros huérfanos.
3.  **Motor de Alertas Dinámicas**: **`APROBADO`** 🟢
    *   Validación de que las alertas de vencimiento e historial en proceso son detectadas de forma exacta en la base de datos.
4.  **Persistencia JSON de Reportes**: **`APROBADO`** 🟢
    *   Inserción y lectura del formato JSONB histórica completada exitosamente sin pérdida de precisión decimal ni sintáctica.