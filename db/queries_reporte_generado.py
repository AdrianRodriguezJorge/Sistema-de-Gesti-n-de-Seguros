from db.conexionDB import Database
from db.queries_base import BaseCrud
import json

class CrudReporteGenerado(BaseCrud):
    def __init__(self):
        super().__init__('reporte_generado', 'id_reporte')

    def crear(self, nombre_reporte, datos_reporte):
        sql = "INSERT INTO reporte_generado (nombre_reporte, datos_reporte) VALUES (%s, %s) RETURNING id_reporte"
        with Database() as db:
            result = db.fetch_one(sql, (nombre_reporte, json.dumps(datos_reporte)))
            return result['id_reporte'] if result else None

    def obtener(self, id_reporte):
        sql = "SELECT * FROM reporte_generado WHERE id_reporte = %s"
        with Database() as db:
            row = db.fetch_one(sql, (id_reporte,))
            if row and row['datos_reporte']:
                if isinstance(row['datos_reporte'], str):
                    row['datos_reporte'] = json.loads(row['datos_reporte'])
            return row

    def obtener_todos(self):
        sql = "SELECT * FROM reporte_generado ORDER BY fecha_creacion DESC, id_reporte DESC"
        with Database() as db:
            rows = db.fetch_all(sql)
            for row in rows:
                if row and row['datos_reporte'] and isinstance(row['datos_reporte'], str):
                    row['datos_reporte'] = json.loads(row['datos_reporte'])
            return rows

    def eliminar(self, id_reporte):
        sql = "DELETE FROM reporte_generado WHERE id_reporte = %s"
        with Database() as db:
            db.execute(sql, (id_reporte,))
