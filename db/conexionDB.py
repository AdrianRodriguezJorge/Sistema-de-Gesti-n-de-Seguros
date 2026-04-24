import psycopg2
import psycopg2.extras

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="seguros_db",
            user="postgres",
            password="123",
            host="localhost",
            port="5432"
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.conn.close()

    def fetch_one(self, sql, params=None):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        self.conn.commit()  # ← añadir
        row = cur.fetchone()
        cur.close()
        return row

    def fetch_all(self, sql, params=None):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        self.conn.commit()  # ← añadir (por si fetch_all se usa con INSERT ... RETURNING alguna vez)
        rows = cur.fetchall()
        cur.close()
        return rows

    def execute(self, sql, params=None):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        cur.close()
