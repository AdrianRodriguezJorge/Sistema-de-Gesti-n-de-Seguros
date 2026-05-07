from db.conexionDB import Database

class CrudGenerico:
    def __init__(self, tabla, columna_pk, columnas_atributos, clase_modelo, funcion_mapeo):
        self.tabla = tabla
        self.columna_pk = columna_pk
        self.columnas_atributos = columnas_atributos
        self.clase_modelo = clase_modelo
        self.funcion_mapeo = funcion_mapeo

    def crear(self, entidad):
        columnas_bd = list(self.columnas_atributos.keys())
        valores = [getattr(entidad, attr) for attr in self.columnas_atributos.values()]
        marcadores = ", ".join(["%s"] * len(valores))
        columnas_sql = ", ".join(columnas_bd)
        sql = f"INSERT INTO {self.tabla} ({columnas_sql}) VALUES ({marcadores}) RETURNING {self.columna_pk}"
        with Database() as db:
            return db.fetch_one(sql, tuple(valores))[self.columna_pk]

    def obtener(self, identificador):
        sql = f"SELECT * FROM {self.tabla} WHERE {self.columna_pk} = %s"
        with Database() as db:
            fila = db.fetch_one(sql, (identificador,))
            return self.funcion_mapeo(fila) if fila else None

    def obtener_todos(self, orden_por=None):
        clausula_orden = f" ORDER BY {orden_por}" if orden_por else ""
        sql = f"SELECT * FROM {self.tabla}{clausula_orden}"
        with Database() as db:
            return [self.funcion_mapeo(fila) for fila in db.fetch_all(sql)]

    def actualizar(self, entidad):
        asignaciones = ", ".join([f"{col} = %s" for col in self.columnas_atributos.keys()])
        valores = [getattr(entidad, attr) for attr in self.columnas_atributos.values()]
        valores.append(entidad.id)
        sql = f"UPDATE {self.tabla} SET {asignaciones} WHERE {self.columna_pk} = %s"
        with Database() as db:
            db.execute(sql, tuple(valores))

    def eliminar(self, identificador):
        sql = f"DELETE FROM {self.tabla} WHERE {self.columna_pk} = %s"
        with Database() as db:
            db.execute(sql, (identificador,))

    def contar(self, condiciones=None, parametros=None):
        condiciones = condiciones or []
        parametros = parametros or []
        sql = f"SELECT COUNT(*) AS total FROM {self.tabla} WHERE 1=1"
        for condicion in condiciones:
            sql += f" AND {condicion}"
        with Database() as db:
            return db.fetch_one(sql, tuple(parametros))["total"]

    def filtrar(self, condiciones, parametros):
        sql = f"SELECT * FROM {self.tabla} WHERE 1=1"
        for condicion in condiciones:
            sql += f" AND {condicion}"
        sql += f" ORDER BY {self.columna_pk}"
        with Database() as db:
            return [self.funcion_mapeo(fila) for fila in db.fetch_all(sql, tuple(parametros))]
