# -*- coding: utf-8 -*-
import sys
import psycopg2

# Reconfigurar la salida estándar a UTF-8 para evitar errores de codificación con Emojis en la terminal de Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass  # Python antiguo

def test_database_connection():
    print("=" * 60)
    print("       🔍 DIAGNÓSTICO DE CONEXIÓN Y SALUD DE LA BASE DE DATOS")
    print("=" * 60)
    
    try:
        # Conectando con las credenciales actualizadas del usuario (password='admin')
        conn = psycopg2.connect(
            dbname="seguros_db",
            user="postgres",
            password="admin",
            host="localhost",
            port="5432",
            client_encoding='UTF8'
        )
        cur = conn.cursor()
        
        # 1. Obtener versión de PostgreSQL
        cur.execute("SELECT version();")
        pg_version = cur.fetchone()[0]
        print(f"✅ Conexión establecida con éxito a 'seguros_db'.")
        print(f"🖥️  Servidor: {pg_version.split(',')[0]}")
        print("-" * 60)
        
        # Lista de tablas a auditar
        tablas = [
            ("agencia", "Agencia Registrada"),
            ("pais", "Países"),
            ("tipo_seguro", "Tipos de Seguro"),
            ("estado_poliza", "Estados de Póliza"),
            ("tipo_siniestro", "Tipos de Siniestro"),
            ("estado_reclamacion", "Estados de Reclamación"),
            ("tipo_reaseguro", "Tipos de Reaseguro"),
            ("cliente", "Clientes registrados"),
            ("poliza", "Pólizas emitidas"),
            ("cobertura", "Coberturas de catálogo"),
            ("poliza_cobertura", "Coberturas asignadas"),
            ("pago", "Pagos registrados"),
            ("reclamacion", "Reclamaciones procesadas"),
            ("reaseguradora", "Reaseguradoras"),
            ("participacion_reaseguro", "Participaciones Reaseguro")
        ]
        
        print("📊 Conteo y verificación de tablas:")
        error_count = 0
        
        for tabla, descripcion in tablas:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {tabla};")
                count = cur.fetchone()[0]
                emoji = "🟢" if count > 0 else "🟡"
                print(f"  {emoji} {descripcion:<25} ({tabla:<22}) -> {count} registros")
            except Exception as table_err:
                print(f"  ❌ Error al consultar tabla '{tabla}': {table_err}")
                error_count += 1
                # Limpiar el estado de transacción fallido en la conexión
                conn.rollback()
                
        print("-" * 60)
        if error_count == 0:
            print("🎉 ¡TODO PERFECTO! Todas las tablas están creadas y con datos de prueba.")
        else:
            print("⚠️  Atención: Algunas tablas no existen o fallaron. Ejecuta SEGUROS_BD.sql primero.")
            
        cur.close()
        conn.close()
        
    except psycopg2.OperationalError as op_err:
        print("❌ Error de Conexión (psycopg2.OperationalError)")
        print(f"   Detalle: {op_err}")
        print("\n💡 Recomendación:")
        print("   1. Asegúrate de que el servicio de PostgreSQL esté iniciado en tu máquina.")
        print("   2. Verifica en pgAdmin 4 que creaste la base de datos llamada 'seguros_db'.")
        print("   3. Confirma que tu contraseña sea efectivamente 'admin'.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        print(f"   Tipo de error: {type(e).__name__}")
        
    print("=" * 60)

if __name__ == "__main__":
    test_database_connection()