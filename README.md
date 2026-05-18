# 💼 Seguros La Confianza - Sistema de Gestión de Seguros

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16.0+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/Licencia-MIT-green?style=for-the-badge)

**Seguros La Confianza** es una aplicación web robusta diseñada para gestionar operaciones críticas de seguros. Desarrollada con **Streamlit** en el frontend y **PostgreSQL** como motor de base de datos, el sistema permite la administración integral de agencias, clientes, pólizas, coberturas, pagos y reclamaciones. Además, cuenta con un motor de reportes, alertas en tiempo real e integridad de datos garantizada a nivel de base de datos.

---

## ✨ Características Principales (Features)

- **Gestión Integral**: Administración completa del ciclo de vida de Clientes, Pólizas, Coberturas, Pagos y Reclamaciones.
- **Motor de Reaseguro**: Asignación y control avanzado de la participación de reaseguradoras, categorizado por tipo de seguro.
- **Alertas Dinámicas en Tiempo Real**: Notificaciones automáticas sobre pólizas próximas a vencer y reclamaciones en estado pendiente.
- **Generación de Reportes**: Persistencia de datos históricos y analíticos en formato `JSONB`, con capacidad de exportación a PDF profesional.
- **Seguridad e Integridad Transaccional**: Consistencia de datos estrictamente controlada mediante *Triggers*, funciones PL/pgSQL e índices optimizados en PostgreSQL.

---

## 🛠️ Arquitectura y Estructura del Código

El proyecto sigue un diseño modular para separar responsabilidades (interfaz, lógica de negocio y base de datos).

```text
Sistema-de-Gestion-de-Seguros/
├── app.py                # Punto de entrada de la aplicación Streamlit
├── db/                   # Capa de acceso a datos y scripts SQL
│   ├── conexionDB.py     # Gestor de conexión a PostgreSQL
│   └── SEGUROS_BD.sql    # Script principal de DDL y DML
├── ui/                   # Componentes modulares de la interfaz de usuario
│   ├── ui_principal.py   # Controlador principal de la UI
│   └── ...               # Formularios, grids y vistas específicas
├── utils/                # Utilidades compartidas del sistema
│   └── generador_pdf.py  # Lógica para generación y exportación de reportes PDF
├── tests/                # Suite de pruebas automatizadas
│   └── ...               # Pruebas unitarias y de integración
├── update_db.py          # Script de inicialización y migración de base de datos
├── requirements.txt      # Dependencias del proyecto Python
└── README.md             # Documentación del proyecto
```

> [!NOTE]
> La modularidad del código permite que nuevos desarrolladores extiendan funcionalidades en la carpeta `ui/` sin impactar la capa de base de datos en `db/`.

---

## 🗄️ Modelo de Base de Datos y Reglas de Negocio (Triggers)

El núcleo del sistema reside en un esquema relacional normalizado compuesto por **12 tablas principales**, que aseguran la consistencia mediante restricciones de llave foránea.

### Triggers Clave (PL/pgSQL)

La integridad de las reglas de negocio críticas se delega a la base de datos mediante disparadores (Triggers):

- **`trg_validar_fechas_poliza`**: Se activa en inserciones/actualizaciones de pólizas para garantizar matemáticamente que la fecha de terminación sea estrictamente posterior a la fecha de inicio.
- **`trg_validar_creacion_reclamacion`**: Bloquea el registro de reclamaciones si la póliza asociada se encuentra inactiva o si la fecha del siniestro está fuera del período de vigencia contratado.
- **`trg_validar_porcentaje_participacion`**: Valida a nivel transaccional que la suma de las participaciones porcentuales de múltiples reaseguradoras para un mismo riesgo no exceda el 100%.

> [!IMPORTANT]
> Estas validaciones en la base de datos previenen inconsistencias sin depender exclusivamente del código del frontend, asegurando la robustez de los datos en cualquier escenario de concurrencia.

---

## 🚀 Requisitos Previos e Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/Sistema-de-Gestion-de-Seguros.git
cd Sistema-de-Gestion-de-Seguros
```

### 2. Crear y activar un entorno virtual
Se recomienda el uso de un entorno virtual para aislar las dependencias.

**En Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**En Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
Instala los paquetes requeridos utilizando el archivo `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuración de la Base de Datos

El sistema requiere una instancia funcional de PostgreSQL.

1. **Crear la base de datos**: En tu gestor favorito (pgAdmin, DBeaver o CLI), crea una base de datos vacía llamada `seguros_db`.
2. **Configurar Credenciales**: Edita el archivo `db/conexionDB.py` con tu usuario y contraseña local de PostgreSQL.
3. **Inicializar y Sembrar Datos**:
   Ejecuta el script automatizado que recreará la estructura de tablas, aplicará los triggers, construirá índices de búsqueda y sembrará la base con datos de prueba (10 clientes, pólizas, pagos y reclamaciones).

```bash
python update_db.py
```

> [!CAUTION]
> Ejecutar `update_db.py` con la base de datos en producción puede sobrescribir o eliminar datos existentes. Utilízalo principalmente para despliegues iniciales o entornos de desarrollo.

---

## 🖥️ Ejecución del Proyecto

Una vez que la base de datos esté inicializada y las dependencias instaladas, puedes iniciar la aplicación con Streamlit:

```bash
python -m streamlit run app.py
```

El servidor local se iniciará y la aplicación web estará disponible por defecto en tu navegador web en:
**[http://localhost:8501](http://localhost:8501)**

---

## 🧪 Pruebas Automatizadas

Para garantizar la estabilidad del sistema a medida que crece, se ha incluido una suite de pruebas en el directorio `tests/`.

Puedes ejecutar todas las pruebas automatizadas (unitarias y de integración) utilizando `pytest` o el módulo nativo `unittest`:

```bash
# Si usas pytest (recomendado):
pytest tests/

# O usando el módulo nativo:
python -m unittest discover -s tests
```

---

<div align="center">
  Hecho con ❤️ y código limpio. Para dudas o soporte, por favor abre un <i>Issue</i> en este repositorio.
</div>