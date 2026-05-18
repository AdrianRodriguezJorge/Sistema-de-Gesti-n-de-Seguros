from models.reaseguradora import Reaseguradora
from db.conexionDB import Database
from db.queries_base import BaseCrud
  
class CrudReaseguradora(BaseCrud):
    def __init__(self): 
        super().__init__("reaseguradora", "idreaseguradora")

    def _mapear(self, fila): 
        return Reaseguradora(idReaseguradora=fila["idreaseguradora"], nombre=fila["nombre"], idPais=fila["idpais"], idTipoReaseguro=fila["idtiporeaseguro"])
    
    def crear(self, reaseguradora):
        sql = "INSERT INTO reaseguradora (nombre, idpais, idtiporeaseguro) VALUES (%s, %s, %s) RETURNING idreaseguradora"
        params = (reaseguradora.nombre, reaseguradora.idPais, reaseguradora.idTipoReaseguro)
        with Database() as db: 
            return db.fetch_one(sql, params)["idreaseguradora"]
        
    def obtener(self, identificador_reaseguradora):
        sql = "SELECT * FROM reaseguradora WHERE idreaseguradora = %s"
        with Database() as db:
            fila = db.fetch_one(sql, (identificador_reaseguradora,))
            return self._mapear(fila) if fila else None
        
    def obtener_todos(self):
        sql = "SELECT * FROM reaseguradora ORDER BY nombre"
        with Database() as db: 
            return [self._mapear(fila) for fila in db.fetch_all(sql)]
    
    def eliminar(self, reaseguradora_seleccionada):
         with Database() as db:
                        db.execute("DELETE FROM participacion_reaseguro WHERE idreaseguradora = %s", (reaseguradora_seleccionada.id,))
                        db.execute("DELETE FROM reaseguradora WHERE idreaseguradora = %s", (reaseguradora_seleccionada.id,))

    def filtrar(self, idReaseguradora=None, nombre=None, idPais=None, idTipoReaseguro=None):
        sql = "SELECT * FROM reaseguradora WHERE 1=1"
        params = []
        if idReaseguradora:
             sql += " AND idreaseguradora = %s"
             params.append(idReaseguradora)
        if nombre: 
            sql += " AND nombre ILIKE %s"
            params.append(f"%{nombre}%")
        if idPais: 
            sql += " AND idpais = %s"
            params.append(idPais)
        if idTipoReaseguro: 
            sql += " AND idtiporeaseguro = %s"
            params.append(idTipoReaseguro)
        with Database() as db:
            return [self._mapear(fila) for fila in db.fetch_all(sql, tuple(params))]

    def actualizar(self, reaseguradora):
        sql = "UPDATE reaseguradora SET nombre=%s, idpais=%s, idtiporeaseguro=%s WHERE idreaseguradora=%s"
        params = (reaseguradora.nombre, reaseguradora.idPais, reaseguradora.idTipoReaseguro, reaseguradora.id)
        with Database() as db:
            db.execute(sql, params)


# Funciones de compatibilidad para la interfaz UI
def obtener_reaseguradora_por_id(id_reaseguradora):
    # Debería retornar una estructura con pais_nombre y tipo_reaseguro_nombre
    sql = """
        SELECT r.idreaseguradora, r.nombre, r.idpais, r.idtiporeaseguro,
               p.nombre as pais_nombre, tr.nombre as tipo_reaseguro_nombre,
               r.email
        FROM reaseguradora r
        JOIN pais p ON r.idpais = p.idpais
        JOIN tipo_reaseguro tr ON r.idtiporeaseguro = tr.idtiporeaseguro
        WHERE r.idreaseguradora = %s
    """
    with Database() as db:
        return db.fetch_one(sql, (id_reaseguradora,))

