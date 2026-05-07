from db.conexionDB import Database

class BaseCrud:
    def __init__(self, table_name, id_column):
        self.table_name = table_name
        self.id_column = id_column

    def eliminar(self, id_entidad):
        sql = f"DELETE FROM {self.table_name} WHERE {self.id_column} = %s"
        with Database() as db:
            db.execute(sql, (id_entidad,))

    def contar(self, **kwargs):
        sql = f"SELECT COUNT(*) as total FROM {self.table_name} WHERE 1=1"
        params = []
        for key, value in kwargs.items():
            if value is not None:
                if isinstance(value, (list, tuple)):
                    placeholders = ','.join(['%s'] * len(value))
                    sql += f" AND {key} IN ({placeholders})"
                    params.extend(value)
                else:
                    sql += f" AND {key} = %s"
                    params.append(value)
        with Database() as db:
            result = db.fetch_one(sql, tuple(params))
            return result["total"] if result else 0