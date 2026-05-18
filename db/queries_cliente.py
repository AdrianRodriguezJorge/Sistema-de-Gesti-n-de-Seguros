from models.cliente import Cliente
from db.conexionDB import Database
from db.queries_base import BaseCrud

class CrudCliente(BaseCrud):
    def __init__(self):
        super().__init__("cliente", "idcliente")

    def _mapear(self, row):
        return Cliente(
            idCliente=row["idcliente"],
            nombre=row["nombre"],
            apellidos=row["apellidos"],
            noIdentificacion=row["no_identificacion"],
            edad=row["edad"],
            sexo=row["sexo"],
            dirPostal=row["dir_postal"],
            telefono=row["telefono"],
            correo=row["correo"],
            idPais=row["idpais"]
        )

    def crear(self, cliente: Cliente):
        sql = """
            INSERT INTO cliente (no_identificacion, nombre, apellidos, edad, sexo, dir_postal, telefono, correo, idpais)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING idcliente
        """
        params = (
            cliente.noIdentificacion,
            cliente.nombre,
            cliente.apellidos,
            cliente.edad,
            cliente.sexo,
            cliente.dirPostal,
            cliente.telefono,
            cliente.correo,
            cliente.idPais
        )
        with Database() as db:
            row = db.fetch_one(sql, params)
            return row["idcliente"]

    def obtener(self, idCliente: int):
        sql = "SELECT * FROM cliente WHERE idcliente = %s"
        with Database() as db:
            row = db.fetch_one(sql, (idCliente,))
            return self._mapear(row) if row else None

    def obtener_todos(self):
        sql = "SELECT * FROM cliente ORDER BY nombre"
        with Database() as db:
            rows = db.fetch_all(sql)
            return [self._mapear(r) for r in rows]

    def filtrar(self, idCliente=None, noIdentificacion=None, nombre=None, apellidos=None, idPais=None, limit=None, offset=None, busqueda_nombre=None):
        sql = "SELECT * FROM cliente WHERE 1=1"
        params = []
        if idCliente:
            sql += " AND idcliente = %s"
            params.append(idCliente)
        if noIdentificacion:
            sql += " AND no_identificacion ILIKE %s"
            params.append(f"%{noIdentificacion}%")
        if nombre:
            sql += " AND nombre ILIKE %s"
            params.append(f"%{nombre}%")
        if apellidos:
            sql += " AND apellidos ILIKE %s"
            params.append(f"%{apellidos}%")
        if busqueda_nombre:
            sql += " AND (nombre ILIKE %s OR apellidos ILIKE %s)"
            params.append(f"%{busqueda_nombre}%")
            params.append(f"%{busqueda_nombre}%")
        if idPais:
            sql += " AND idpais = %s"
            params.append(idPais)
        
        sql += " ORDER BY nombre"
        
        if limit is not None:
            sql += " LIMIT %s"
            params.append(limit)
        if offset is not None:
            sql += " OFFSET %s"
            params.append(offset)
            
        with Database() as db:
            rows = db.fetch_all(sql, tuple(params))
            return [self._mapear(r) for r in rows]

    def contar(self, idCliente=None, noIdentificacion=None, nombre=None, apellidos=None, idPais=None):
        sql = "SELECT COUNT(*) as total FROM cliente WHERE 1=1"
        params = []
        if idCliente:
            sql += " AND idcliente = %s"
            params.append(idCliente)
        if noIdentificacion:
            sql += " AND no_identificacion ILIKE %s"
            params.append(f"%{noIdentificacion}%")
        if nombre:
            sql += " AND nombre ILIKE %s"
            params.append(f"%{nombre}%")
        if apellidos:
            sql += " AND apellidos ILIKE %s"
            params.append(f"%{apellidos}%")
        if idPais:
            sql += " AND idpais = %s"
            params.append(idPais)
            
        with Database() as db:
            row = db.fetch_one(sql, tuple(params))
            return row["total"]

    def contar_filtrado(self, noIdentificacion=None, busqueda_nombre=None, idPais=None):
        sql = "SELECT COUNT(*) as total FROM cliente WHERE 1=1"
        params = []
        if noIdentificacion:
            sql += " AND no_identificacion ILIKE %s"
            params.append(f"%{noIdentificacion}%")
        if busqueda_nombre:
            sql += " AND (nombre ILIKE %s OR apellidos ILIKE %s)"
            params.append(f"%{busqueda_nombre}%")
            params.append(f"%{busqueda_nombre}%")
        if idPais:
            sql += " AND idpais = %s"
            params.append(idPais)
            
        with Database() as db:
            row = db.fetch_one(sql, tuple(params))
            return row["total"]


    def actualizar(self, cliente: Cliente):
        sql = """
            UPDATE cliente 
            SET no_identificacion=%s, nombre=%s, apellidos=%s, edad=%s, sexo=%s, dir_postal=%s, telefono=%s, correo=%s, idpais=%s 
            WHERE idcliente=%s
        """
        params = (
            cliente.noIdentificacion,
            cliente.nombre,
            cliente.apellidos,
            cliente.edad,
            cliente.sexo,
            cliente.dirPostal,
            cliente.telefono,
            cliente.correo,
            cliente.idPais,
            cliente.id
        )
        with Database() as db:
            db.execute(sql, params)

    def eliminar(self, cliente_id):
        """Eliminación física del cliente y todos sus registros dependientes en cascada"""
        with Database() as db:
            # 1. Obtener pólizas asociadas
            sql_polizas = "SELECT idpoliza FROM poliza WHERE idcliente = %s"
            polizas = db.fetch_all(sql_polizas, (cliente_id,))
            
            for p in polizas:
                pid = p["idpoliza"]
                # Borrar reclamaciones asociadas a la póliza
                db.execute("DELETE FROM reclamacion WHERE idpoliza = %s", (pid,))
                # Borrar pagos asociados a la póliza
                db.execute("DELETE FROM pago WHERE idpoliza = %s", (pid,))
                # Borrar coberturas asociadas a la póliza
                db.execute("DELETE FROM poliza_cobertura WHERE idpoliza = %s", (pid,))
                # Borrar cancelaciones asociadas a la póliza
                db.execute("DELETE FROM poliza_cancelada WHERE idpoliza = %s", (pid,))
                # Finalmente borrar la póliza
                db.execute("DELETE FROM poliza WHERE idpoliza = %s", (pid,))
            
            # 2. Eliminar el cliente
            sql_del_cliente = "DELETE FROM cliente WHERE idcliente = %s"
            db.execute(sql_del_cliente, (cliente_id,))


# Funciones de compatibilidad para la interfaz UI
def listar_clientes():
    registros = CrudCliente().obtener_todos()
    return [{
        "idcliente": r.id,
        "nombre": r.nombre,
        "apellidos": r.apellidos,
        "no_identificacion": r.noIdentificacion,
        "edad": r.edad,
        "sexo": r.sexo,
        "dir_postal": r.dirPostal,
        "telefono": r.telefono,
        "correo": r.correo,
        "idpais": r.idPais
    } for r in registros] if registros else []

def obtener_cliente_por_id(id_cliente):
    r = CrudCliente().obtener(id_cliente)
    if r:
        return {
            "idcliente": r.id,
            "nombre": r.nombre,
            "apellidos": r.apellidos,
            "no_identificacion": r.noIdentificacion,
            "edad": r.edad,
            "sexo": r.sexo,
            "dir_postal": r.dirPostal,
            "telefono": r.telefono,
            "correo": r.correo,
            "idpais": r.idPais
        }
    return None

