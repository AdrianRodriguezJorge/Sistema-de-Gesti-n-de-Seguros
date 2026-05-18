from models.poliza_cobertura import PolizaCobertura
from db.conexionDB import Database
from db.queries_base import BaseCrud

class CrudPolizaCobertura(BaseCrud):
    def __init__(self): 
        super().__init__("poliza_cobertura", "idpoliza")

    def _mapear(self, r): 
        return PolizaCobertura(idPoliza=r["idpoliza"], idCobertura=r["idcobertura"], monto=r["monto"])
    
    def crear(self, o):
        sql = "INSERT INTO poliza_cobertura (idpoliza, idcobertura, monto) VALUES (%s, %s, %s)"
        params = (o.idPoliza, o.idCobertura, o.monto)
        with Database() as db: 
            db.execute(sql, params)

    def obtener(self, idPoliza, idCobertura):
        sql = "SELECT * FROM poliza_cobertura WHERE idpoliza = %s AND idcobertura = %s"
        with Database() as db:
            r = db.fetch_one(sql, (idPoliza, idCobertura))
            return self._mapear(r) if r else None
        
    def obtener_todos(self):
        sql = "SELECT * FROM poliza_cobertura ORDER BY idpoliza"
        with Database() as db: 
            return [self._mapear(r) for r in db.fetch_all(sql)]
        
    def filtrar(self, idPoliza=None, idCobertura=None):
        sql = "SELECT * FROM poliza_cobertura WHERE 1=1"
        params = []
        if idPoliza: 
            sql += " AND idpoliza = %s"
            params.append(idPoliza)
        if idCobertura: 
            sql += " AND idcobertura = %s"
            params.append(idCobertura)
        with Database() as db: 
            return [self._mapear(r) for r in db.fetch_all(sql, tuple(params))]
        
    def actualizar(self, o):
        sql = "UPDATE poliza_cobertura SET monto=%s WHERE idpoliza=%s AND idcobertura=%s"
        params = (o.monto, o.idPoliza, o.idCobertura)
        with Database() as db:
            db.execute(sql, params)
