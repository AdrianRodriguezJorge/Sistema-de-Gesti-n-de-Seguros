# -*- coding: utf-8 -*-
import sys
import psycopg2

# Reconfigurar la salida estándar a UTF-8 para evitar errores de codificación en terminales de Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def run_sql_script(script_path):
    print("=" * 60)
    print("       ⚙️ INICIALIZANDO Y VINCULANDO BASE DE DATOS POSTGRESQL")
    print("=" * 60)
    try:
        # Leer el archivo SQL
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Conectar a la base de datos con tus credenciales
        conn = psycopg2.connect(
            dbname="seguros_db",
            user="postgres",
            password="admin",
            host="localhost",
            port="5432"
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Ejecutar el contenido completo del script SQL (Tablas, Índices y Triggers)
        print(f"Executing: {script_path}...")
        cur.execute(sql_content)
        
        print("\n✅ ¡ÉXITO TOTAL! Base de datos recreada.")
        print("🟢 Índices de optimización de rendimiento establecidos.")
        print("🟢 Los 4 triggers de validación e integridad relacional están ACTIVOS.")
        print("=" * 60)
        
        cur.close()
        conn.close()
    except psycopg2.OperationalError as op_err:
        print("\n❌ Error de Conexión: Asegúrate de que PostgreSQL esté iniciado.")
        print(f"Detalle: {op_err}")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error al ejecutar el script: {e}")
        print("=" * 60)

if __name__ == "__main__":
    run_sql_script("db/SEGUROS_BD.sql")
