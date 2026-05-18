from models.reclamacion import Reclamacion
from db.conexionDB import Database
from db.queries_base import BaseCrud
  
class CrudReclamacion(BaseCrud):
    def __init__(self): 
        super().__init__("reclamacion", "idreclamacion")

    def _mapear(self, r): 
        return Reclamacion(idReclamacion=r["idreclamacion"], idTipoSiniestro=r["idtiposiniestro"], fechaSiniestro=r["fecha_siniestro"], montoReclamado=r["monto_reclamado"], idEstadoReclamacion=r["idestadoreclamacion"], montoIndemnizado=r["monto_indemnizado"], idPoliza=r["idpoliza"])
    
    def crear(self, o):
        sql = "INSERT INTO reclamacion (idtiposiniestro, fecha_siniestro, monto_reclamado, idestadoreclamacion, monto_indemnizado, idpoliza) VALUES (%s, %s, %s, %s, %s, %s) RETURNING idreclamacion"
        params = (o.idTipoSiniestro, o.fechaSiniestro, o.montoReclamado, o.idEstadoReclamacion, o.montoIndemnizado, o.idPoliza)
        with Database() as db: 
            return db.fetch_one(sql, params)["idreclamacion"]
        
    def obtener(self, id):
        sql = "SELECT * FROM reclamacion WHERE idreclamacion = %s"
        with Database() as db:
            r = db.fetch_one(sql, (id,))
            return self._mapear(r) if r else None
        
    def obtener_todos(self):
        sql = "SELECT * FROM reclamacion ORDER BY fecha_siniestro DESC"
        with Database() as db: 
            return [self._mapear(r) for r in db.fetch_all(sql)]
        
    def filtrar(self, idReclamacion=None, idTipoSiniestro=None, idEstadoReclamacion=None, idPoliza=None, limit=None, offset=None):
        sql = "SELECT * FROM reclamacion WHERE 1=1"
        params = []
        if idReclamacion: 
            sql += " AND idreclamacion = %s"
            params.append(idReclamacion)
        if idTipoSiniestro:
             sql += " AND idtiposiniestro = %s" 
             params.append(idTipoSiniestro)
        if idEstadoReclamacion:
             sql += " AND idestadoreclamacion = %s"
             params.append(idEstadoReclamacion)
        if idPoliza: 
            sql += " AND idpoliza = %s" 
            params.append(idPoliza)
        sql += " ORDER BY fecha_siniestro DESC"
        if limit is not None:
            sql += " LIMIT %s"
            params.append(limit)
        if offset is not None:
            sql += " OFFSET %s"
            params.append(offset)
        with Database() as db: 
            return [self._mapear(r) for r in db.fetch_all(sql, tuple(params))]
    
    def contar(self, idReclamacion=None, idTipoSiniestro=None, idEstadoReclamacion=None, idPoliza=None):
        sql = "SELECT COUNT(*) as total FROM reclamacion WHERE 1=1"
        params = []
        if idReclamacion: 
            sql += " AND idreclamacion = %s"
            params.append(idReclamacion)
        if idTipoSiniestro:
             sql += " AND idtiposiniestro = %s" 
             params.append(idTipoSiniestro)
        if idEstadoReclamacion:
             sql += " AND idestadoreclamacion = %s"
             params.append(idEstadoReclamacion)
        if idPoliza: 
            sql += " AND idpoliza = %s" 
            params.append(idPoliza)
        with Database() as db: 
            return db.fetch_one(sql, tuple(params))["total"]
        
    def actualizar(self, o:Reclamacion):
        sql = "UPDATE reclamacion SET idtiposiniestro=%s, fecha_siniestro=%s, monto_reclamado=%s, idestadoreclamacion=%s, monto_indemnizado=%s, idpoliza=%s WHERE idreclamacion=%s"
        params = (o.idTipoSiniestro, o.fechaSiniestro, o.montoReclamado, o.idEstadoReclamacion, o.montoIndemnizado, o.idPoliza, o.id)
        with Database() as db: 
            db.execute(sql, params)

    def eliminar(self, id_reclamacion):
        with Database() as db:
            db.execute("DELETE FROM reclamacion_rechazada WHERE idreclamacion = %s", (id_reclamacion,))
            db.execute("DELETE FROM reclamacion WHERE idreclamacion = %s", (id_reclamacion,))


# Funciones de compatibilidad para la interfaz UI
def listar_reclamaciones():
    sql = """
        SELECT c.nombre || ' ' || c.apellidos as cliente,
               r.idpoliza, ts.nombre as tipo_seguro, r.idreclamacion,
               tsi.nombre as tipo_siniestro, r.fechasiniestro,
               r.montoreclamado, r.montoindemnizado, er.nombre as estado
        FROM reclamacion r
        JOIN poliza p ON r.idpoliza = p.idpoliza
        JOIN cliente c ON p.idcliente = c.idcliente
        JOIN tipo_seguro ts ON p.idtiposeguro = ts.idtiposeguro
        JOIN tipo_siniestro tsi ON r.idtiposiniestro = tsi.idtiposiniestro
        JOIN estado_reclamacion er ON r.idestadoreclamacion = er.idestadoreclamacion
        ORDER BY r.fechasiniestro DESC
    """
    with Database() as db:
        return db.fetch_all(sql)

