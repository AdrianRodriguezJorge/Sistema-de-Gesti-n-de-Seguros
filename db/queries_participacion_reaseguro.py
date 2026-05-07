from data.class_participacion_reaseguro import ParticipacionReaseguro
from db.conexionDB import Database
from db.queries_base import BaseCrud 

class CrudParticipacionReaseguro(BaseCrud):
    def __init__(self):
        super().__init__("participacion_reaseguro", "idreaseguradora")

    def _mapear(self, r): 
        return ParticipacionReaseguro(idReaseguradora=r["idreaseguradora"], idTipoSeguro=r["idtiposeguro"], porcentaje=r["porcentaje"])
    
    def crear(self, o):
        sql = "INSERT INTO participacion_reaseguro (idreaseguradora, idtiposeguro, porcentaje) VALUES (%s, %s, %s)"
        params = (o.idReaseguradora, o.idTipoSeguro, o.porcentaje)
        with Database() as db:
            db.execute(sql, params)

    def obtener(self, idReaseguradora, idTipoSeguro):
        sql = "SELECT * FROM participacion_reaseguro WHERE idreaseguradora = %s AND idtiposeguro = %s"
        with Database() as db:
            r = db.fetch_one(sql, (idReaseguradora, idTipoSeguro))
            return self._mapear(r) if r else None
    def obtener_todos(self):
        sql = "SELECT * FROM participacion_reaseguro ORDER BY idreaseguradora"
        with Database() as db:
            return [self._mapear(r) for r in db.fetch_all(sql)]
        
    def filtrar(self, idReaseguradora=None, idTipoSeguro=None):
        sql = "SELECT * FROM participacion_reaseguro WHERE 1=1"
        params = []
        if idReaseguradora: 
            sql += " AND idreaseguradora = %s" 
            params.append(idReaseguradora)
        if idTipoSeguro:
             sql += " AND idtiposeguro = %s"
             params.append(idTipoSeguro)
        with Database() as db:
            return [self._mapear(r) for r in db.fetch_all(sql, tuple(params))]
        
    def actualizar(self, o):
        sql = "UPDATE participacion_reaseguro SET porcentaje=%s WHERE idreaseguradora=%s AND idtiposeguro=%s"
        params = (o.porcentaje, o.idReaseguradora, o.idTipoSeguro)
        with Database() as db:
            db.execute(sql, params)
