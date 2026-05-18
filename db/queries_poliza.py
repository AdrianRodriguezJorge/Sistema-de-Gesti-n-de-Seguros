from data.class_poliza import Poliza
from db.conexionDB import Database
from db.queries_base import BaseCrud 
  
class CrudPoliza(BaseCrud):
    def __init__(self): 
        super().__init__("poliza", "idpoliza")

    def _mapear(self, r): 
        return Poliza(idPoliza=r["idpoliza"], idTipoSeguro=r["idtiposeguro"], fechaInicio=r["fecha_inicio"], fechaFin=r["fecha_fin"], primaMensual=r["prima_mensual"], idEstadoPoliza=r["idestadopoliza"], montoAsegurado=r["monto_asegurado"], idCliente=r["idcliente"])
    
    def crear(self, o):
        sql = "INSERT INTO poliza (idtiposeguro, fecha_inicio, fecha_fin, prima_mensual, idestadopoliza, monto_asegurado, idcliente) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING idpoliza"
        params = (o.idTipoSeguro, o.fechaInicio, o.fechaFin, o.primaMensual, o.idEstadoPoliza, o.montoAsegurado, o.idCliente)
        with Database() as db: 
            return db.fetch_one(sql, params)["idpoliza"]
        
    def obtener(self, id):
        sql = "SELECT * FROM poliza WHERE idpoliza = %s"
        with Database() as db:
            r = db.fetch_one(sql, (id,))
            return self._mapear(r) if r else None
        
    def obtener_todos(self):
        sql = "SELECT * FROM poliza ORDER BY idpoliza"
        with Database() as db: 
            return [self._mapear(r) for r in db.fetch_all(sql)]
        
    def filtrar(self, idPoliza=None, idTipoSeguro=None, idEstadoPoliza=None, idCliente=None, limit=None, offset=None):
        sql = "SELECT * FROM poliza WHERE 1=1"
        params = []
        if idPoliza: 
            sql += " AND idpoliza = %s"
            params.append(idPoliza)
        if idTipoSeguro:
             sql += " AND idtiposeguro = %s"
             params.append(idTipoSeguro)
        if idEstadoPoliza:
             sql += " AND idestadopoliza = %s"
             params.append(idEstadoPoliza)
        if idCliente:
             sql += " AND idcliente = %s"
             params.append(idCliente)
        sql += " ORDER BY idpoliza"
        if limit is not None:
            sql += " LIMIT %s"
            params.append(limit)
        if offset is not None:
            sql += " OFFSET %s"
            params.append(offset)
        with Database() as db:
            return [self._mapear(r) for r in db.fetch_all(sql, tuple(params))]
    
    def contar(self, idPoliza=None, idTipoSeguro=None, idEstadoPoliza=None, idCliente=None):
        sql = "SELECT COUNT(*) as total FROM poliza WHERE 1=1"
        params = []
        if idPoliza: 
            sql += " AND idpoliza = %s"
            params.append(idPoliza)
        if idTipoSeguro:
             sql += " AND idtiposeguro = %s"
             params.append(idTipoSeguro)
        if idEstadoPoliza:
             sql += " AND idestadopoliza = %s"
             params.append(idEstadoPoliza)
        if idCliente:
             sql += " AND idcliente = %s"
             params.append(idCliente)
        with Database() as db:
            return db.fetch_one(sql, tuple(params))["total"]
        
    def actualizar(self, o: Poliza):
        sql = "UPDATE poliza SET idtiposeguro=%s, fecha_inicio=%s, fecha_fin=%s, prima_mensual=%s, idestadopoliza=%s, monto_asegurado=%s, idcliente=%s WHERE idpoliza=%s"
        params = (o.idTipoSeguro, o.fechaInicio, o.fechaFin, o.primaMensual, o.idEstadoPoliza, o.montoAsegurado, o.idCliente, o.id)
        with Database() as db: 
            db.execute(sql, params)
