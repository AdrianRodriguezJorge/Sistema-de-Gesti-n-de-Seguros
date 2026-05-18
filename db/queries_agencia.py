from data.class_agencia import Agencia
from db.conexionDB import Database
from db.queries_base import BaseCrud

class CrudAgencia(BaseCrud):
    def __init__(self):
        super().__init__("agencia", "idagencia")

    def _mapear(self, row):
        return Agencia(idAgencia=row["idagencia"], nombre=row["nombre"], direccion=row["direccion"], telefono=row["telefono"], email=row["email"], directorGeneral=row["director_general"], jefeSeguros=row["jefe_seguros"], jefeReclamaciones=row["jefe_reclamaciones"])

    def crear(self, agencia: Agencia):
        sql = "INSERT INTO agencia (nombre, direccion, telefono, email, director_general, jefe_seguros, jefe_reclamaciones) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING idagencia"
        params = (agencia.nombre, agencia.direccion, agencia.telefono, agencia.email, agencia.directorGeneral, agencia.jefeSeguros, agencia.jefeReclamaciones)
        with Database() as db:
            row = db.fetch_one(sql, params)
            return row["idagencia"]

    def obtener(self, idAgencia: int):
        sql = "SELECT * FROM agencia WHERE idagencia = %s"
        with Database() as db:
            row = db.fetch_one(sql, (idAgencia,))
            return self._mapear(row) if row else None

    def obtener_todos(self):
        sql = "SELECT * FROM agencia ORDER BY nombre"
        with Database() as db:
            rows = db.fetch_all(sql)
            return [self._mapear(r) for r in rows]

    def filtrar(self, idAgencia=None, nombre=None, direccion=None, telefono=None, email=None, directorGeneral=None, jefeSeguros=None, jefeReclamaciones=None):
        sql = "SELECT * FROM agencia WHERE 1=1"
        params = []
        if idAgencia: 
            sql += " AND idagencia = %s"
            params.append(idAgencia)
        if nombre: 
            sql += " AND nombre ILIKE %s"
            params.append(f"%{nombre}%")
        if direccion: 
            sql += " AND direccion ILIKE %s"
            params.append(f"%{direccion}%")
        if telefono: 
            sql += " AND telefono ILIKE %s"
            params.append(f"%{telefono}%")
        if email: 
            sql += " AND email ILIKE %s" 
            params.append(f"%{email}%")
        if directorGeneral: 
            sql += " AND director_general ILIKE %s"
            params.append(f"%{directorGeneral}%")
        if jefeSeguros: 
            sql += " AND jefe_seguros ILIKE %s"
            params.append(f"%{jefeSeguros}%")
        if jefeReclamaciones: 
            sql += " AND jefe_reclamaciones ILIKE %s"
            params.append(f"%{jefeReclamaciones}%")
        sql += " ORDER BY nombre"
        with Database() as db:
            rows = db.fetch_all(sql, tuple(params))
            return [self._mapear(r) for r in rows]

    def actualizar(self, agencia: Agencia):
        sql = "UPDATE agencia SET nombre=%s, direccion=%s, telefono=%s, email=%s, director_general=%s, jefe_seguros=%s, jefe_reclamaciones=%s WHERE idagencia=%s"
        params = (agencia.nombre, agencia.direccion, agencia.telefono, agencia.email, agencia.directorGeneral, agencia.jefeSeguros, agencia.jefeReclamaciones, agencia.id)
        with Database() as db:
            db.execute(sql, params)