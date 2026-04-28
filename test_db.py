# test_db.py
import psycopg2

try:
    conn = psycopg2.connect(
        dbname="seguros_db",
        user="postgres",
        password="123",
        host="localhost",
        port="5432",
        client_encoding='UTF8'
    )
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print("✅ Conexión exitosa")
    print(cur.fetchone())
    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Tipo de error: {type(e).__name__}")