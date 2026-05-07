from data.class_cliente import Cliente
from db.conexionDB import Database
from db.queries_base import BaseCrud

<<<<<<< HEAD

def insertar_cliente(cliente):
    """Insertar un nuevo cliente validando que el país existe"""

    with Database() as db:
        # Verificar que el país existe
        pais = db.fetch_one("SELECT idpais FROM pais WHERE idpais = %s;", (cliente.idpais,))
        if not pais:
            raise ValueError(f"El país con ID {cliente.idpais} no existe. Verifica la tabla PAIS.")

        sql = """
            INSERT INTO cliente (noIdentificación, nombre, apellidos, edad, sexo, telefono, correo, idpais, dirPostal)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING idcliente;
        """

        params = (
            cliente.noIdentificación,
            cliente.nombre,
            cliente.apellidos,
            cliente.edad,
            cliente.sexo,
            cliente.telefono,
            cliente.correo,
            cliente.idpais,
            cliente.dirPostal
        )

        result = db.fetch_one(sql, params)
        return result["idcliente"] if result else None
=======
class CrudCliente(BaseCrud):
    def __init__(self): 
        super().__init__("cliente", "idcliente")

    def _mapear(self, fila): 
        return Cliente(idCliente=fila["idcliente"], noIdentificacion=fila["no_identificacion"], nombre=fila["nombre"], apellidos=fila["apellidos"], edad=fila["edad"], sexo=fila["sexo"], dirPostal=fila["dir_postal"], telefono=fila["telefono"], correo=fila["correo"], idPais=fila["idpais"])
    
    def crear(self, cliente):
        sql = "INSERT INTO cliente (no_identificacion, nombre, apellidos, edad, sexo, dir_postal, telefono, correo, idpais) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING idcliente"
        params = (cliente.noIdentificacion, cliente.nombre, cliente.apellidos, cliente.edad, cliente.sexo, cliente.dirPostal, cliente.telefono, cliente.correo, cliente.idPais)
        with Database() as db:
            return db.fetch_one(sql, params)["idcliente"]

    def obtener(self, identificador_cliente):
        sql = "SELECT * FROM cliente WHERE idcliente = %s"
        with Database() as db:
            fila = db.fetch_one(sql, (identificador_cliente,))
            return self._mapear(fila) if fila else None
        
    def obtener_todos(self):
        sql = "SELECT * FROM cliente ORDER BY apellidos, nombre"
        with Database() as db: 
            return [self._mapear(fila) for fila in db.fetch_all(sql)]
        
    def eliminar(self, identificador_cliente: int):
        with Database() as db:
            sql = '''DELETE FROM pago WHERE idpoliza IN (SELECT idpoliza FROM poliza WHERE idcliente = %s)'''
            db.execute(sql, (identificador_cliente,))
            sql = '''SELECT re.idreclamacion FROM reclamacion AS re
                    JOIN poliza AS p ON re.idpoliza = p.idpoliza
                    WHERE p.idcliente = %s'''
            filas_reclamaciones = db.fetch_all(sql, (identificador_cliente,))
            sql = '''DELETE FROM reclamacion_rechazada WHERE idreclamacion = %s'''
            for fila in filas_reclamaciones:
                db.execute(sql, (fila["idreclamacion"],))
            sql = '''DELETE FROM reclamacion WHERE idpoliza IN (
                        SELECT idpoliza FROM poliza WHERE idcliente = %s)'''
            db.execute(sql, (identificador_cliente,))
            sql = '''SELECT DISTINCT pc.idcobertura FROM poliza_cobertura AS pc
                    JOIN poliza AS p ON pc.idpoliza = p.idpoliza
                    WHERE p.idcliente = %s'''
            sql = '''DELETE FROM poliza_cobertura WHERE idpoliza IN (
                        SELECT idpoliza FROM poliza WHERE idcliente = %s)'''
            db.execute(sql, (identificador_cliente,))
            sql = '''DELETE FROM poliza_cancelada WHERE idpoliza IN (
                        SELECT idpoliza FROM poliza WHERE idcliente = %s)'''
            db.execute(sql, (identificador_cliente,))
            sql = '''DELETE FROM poliza WHERE idcliente = %s'''
            db.execute(sql, (identificador_cliente,))
            sql = '''DELETE FROM cliente WHERE idcliente = %s'''
            db.execute(sql, (identificador_cliente,))
>>>>>>> 73161b5 (mis cambios)

    def filtrar(self, idCliente=None, noIdentificacion=None, nombre=None, apellidos=None, edad=None, sexo=None, idPais=None, correo=None, limit=None, offset=None, busqueda_nombre=None):
        sql = "SELECT * FROM cliente WHERE 1=1"
        params = []
        if idCliente: 
            sql += " AND idcliente = %s"
            params.append(idCliente)
        if noIdentificacion: 
            sql += " AND no_identificacion = %s"
            params.append(noIdentificacion)
        if busqueda_nombre:
            sql += " AND (nombre ILIKE %s OR apellidos ILIKE %s)"
            params.append(f"%{busqueda_nombre}%")
            params.append(f"%{busqueda_nombre}%")
        else:
            if nombre: 
                sql += " AND nombre ILIKE %s"
                params.append(f"%{nombre}%")
            if apellidos: 
                sql += " AND apellidos ILIKE %s" 
                params.append(f"%{apellidos}%")
        if edad: 
            sql += " AND edad = %s"
            params.append(edad)
        if sexo:
             sql += " AND sexo = %s"
             params.append(sexo)
        if idPais: 
            sql += " AND idpais = %s" 
            params.append(idPais)
        if correo: 
            sql += " AND correo ILIKE %s"
            params.append(f"%{correo}%")
        sql += " ORDER BY apellidos, nombre"
        if limit is not None:
            sql += " LIMIT %s"
            params.append(limit)
        if offset is not None:
            sql += " OFFSET %s"
            params.append(offset)
        with Database() as db: 
            return [self._mapear(fila) for fila in db.fetch_all(sql, tuple(params))]
        
    def actualizar(self, cliente):
        sql = "UPDATE cliente SET no_identificacion=%s, nombre=%s, apellidos=%s, edad=%s, sexo=%s, dir_postal=%s, telefono=%s, correo=%s, idpais=%s WHERE idcliente=%s"
        params = (cliente.noIdentificacion, cliente.nombre, cliente.apellidos, cliente.edad, cliente.sexo, cliente.dirPostal, cliente.telefono, cliente.correo, cliente.idPais, cliente.id)
        with Database() as db: 
            db.execute(sql, params)

<<<<<<< HEAD
def actualizar_cliente(cliente):
    """Actualizar cliente validando que el país existe"""

    with Database() as db:
        # Verificar que el país existe
        pais = db.fetch_one("SELECT idpais FROM pais WHERE idpais = %s;", (cliente.idpais,))
        if not pais:
            raise ValueError(f"El país con ID {cliente.idpais} no existe. Verifica la tabla PAIS.")

        # Verificar que el cliente existe
        existente = db.fetch_one("SELECT idcliente FROM cliente WHERE idcliente = %s;", (cliente.idcliente,))
        if not existente:
            raise ValueError(f"El cliente con ID {cliente.idcliente} no existe")

        sql = """
            UPDATE cliente
            SET noIdentificación = %s,
                nombre = %s,
                apellidos = %s,
                edad = %s,
                sexo = %s,
                telefono = %s,
                correo = %s,
                idpais = %s,
                dirPostal = %s
            WHERE idcliente = %s;
        """

        params = (
            cliente.noIdentificación,
            cliente.nombre,
            cliente.apellidos,
            cliente.edad,
            cliente.sexo,
            cliente.telefono,
            cliente.correo,
            cliente.idpais,
            cliente.dirPostal,
            cliente.idcliente
        )

        db.execute(sql, params)


def listar_clientes():
    sql = """
        SELECT idcliente, noIdentificación, nombre, apellidos, edad, sexo, idpais, dirPostal, telefono, correo
        FROM cliente
        ORDER BY idcliente;
    """
    with Database() as db:
        return db.fetch_all(sql)


def obtener_cliente_por_id(idcliente):
    sql = """
        SELECT idcliente, noIdentificación, nombre, apellidos, edad, sexo, idpais, dirPostal, telefono, correo
        FROM cliente
        WHERE idcliente = %s;
    """
    with Database() as db:
        return db.fetch_one(sql, (idcliente,))


def eliminar_cliente(idcliente):
    """Eliminar cliente (verificar que no tenga pólizas asociadas)"""
    with Database() as db:
        # Verificar si tiene pólizas
        polizas = db.fetch_one("SELECT idpoliza FROM poliza WHERE idcliente = %s LIMIT 1;", (idcliente,))
        if polizas:
            raise ValueError(f"No se puede eliminar el cliente {idcliente} porque tiene pólizas asociadas")

        db.execute("DELETE FROM cliente WHERE idcliente = %s;", (idcliente,))
=======
    def contar_filtrado(self, noIdentificacion=None, nombre=None, apellidos=None, idPais=None, busqueda_nombre=None):
        sql = "SELECT COUNT(*) as total FROM cliente WHERE 1=1"
        params = []
        if noIdentificacion: 
            sql += " AND no_identificacion = %s"
            params.append(noIdentificacion)
        if busqueda_nombre:
            sql += " AND (nombre ILIKE %s OR apellidos ILIKE %s)"
            params.append(f"%{busqueda_nombre}%")
            params.append(f"%{busqueda_nombre}%")
        else:
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
            result = db.fetch_one(sql, tuple(params))
            return result["total"] if result else 0
>>>>>>> 73161b5 (mis cambios)
