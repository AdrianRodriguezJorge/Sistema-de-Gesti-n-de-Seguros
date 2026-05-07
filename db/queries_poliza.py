<<<<<<< HEAD
from db.conexionDB import Database

def insertar_poliza(poliza):
    """Insertar una nueva póliza validando que existan las referencias"""

    with Database() as db:
        # Verificar que el cliente existe
        cliente = db.fetch_one("SELECT idcliente FROM cliente WHERE idcliente = %s;", (poliza.id_cliente,))
        if not cliente:
            raise ValueError(f"El cliente con ID {poliza.id_cliente} no existe")

        # Verificar que el tipo de seguro existe
        tipo_seguro = db.fetch_one("SELECT idtiposeguro FROM tipo_seguro WHERE idtiposeguro = %s;", (poliza.id_tipo_seguro,))
        if not tipo_seguro:
            raise ValueError(f"El tipo de seguro con ID {poliza.id_tipo_seguro} no existe")

        # Verificar que el estado de póliza existe
        estado = db.fetch_one("SELECT idestadopoliza FROM estado_poliza WHERE idestadopoliza = %s;", (poliza.id_estado_poliza,))
        if not estado:
            raise ValueError(f"El estado de póliza con ID {poliza.id_estado_poliza} no existe")

        # Insertar
        sql = """
            INSERT INTO poliza (idpoliza, idtiposeguro, fechainicio, fechafin,
                                primamensual, idestadopoliza, montoasegurado, idcliente)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING idpoliza;
        """
        params = (
            poliza.id_poliza,
            poliza.id_tipo_seguro,
            poliza.fecha_inicio,
            poliza.fecha_fin,
            poliza.prima_mensual,
            poliza.id_estado_poliza,
            poliza.monto_asegurado,
            poliza.id_cliente
        )
        result = db.fetch_one(sql, params)
        return result["idpoliza"] if result else None


def listar_polizas():
    sql = """
        SELECT p.idpoliza, p.fechainicio, p.fechafin, p.primamensual, p.montoasegurado, ts.nombre as tipo_seguro, ep.nombre as estado, c.nombre as cliente_nombre, c.apellidos
        FROM poliza p
        JOIN tipo_seguro ts ON p.idtiposeguro = ts.idtiposeguro
        JOIN estado_poliza ep ON p.idestadopoliza = ep.idestadopoliza
        JOIN cliente c ON p.idcliente = c.idcliente
        ORDER BY p.idpoliza;
    """
    with Database() as db:
        return db.fetch_all(sql)


def obtener_poliza_por_id(idpoliza):
    sql = """
        SELECT p.*, ts.nombre as tipo_seguro_nombre, ep.nombre as estado_nombre, c.nombre as cliente_nombre, c.apellidos
        FROM poliza p
        JOIN tipo_seguro ts ON p.idtiposeguro = ts.idtiposeguro
        JOIN estado_poliza ep ON p.idestadopoliza = ep.idestadopoliza
        JOIN cliente c ON p.idcliente = c.idcliente
        WHERE p.idpoliza = %s;
    """
    with Database() as db:
        return db.fetch_one(sql, (idpoliza,))


def actualizar_poliza(poliza):
    """Actualizar datos de una póliza existente"""

    with Database() as db:
        # Verificar que la póliza existe
        existente = db.fetch_one("SELECT idpoliza FROM poliza WHERE idpoliza = %s;", (poliza.id_poliza,))
        if not existente:
            raise ValueError(f"La póliza con ID {poliza.id_poliza} no existe")

        # Verificar referencias
        if not db.fetch_one("SELECT idcliente FROM cliente WHERE idcliente = %s;", (poliza.id_cliente,)):
            raise ValueError(f"El cliente con ID {poliza.id_cliente} no existe")
        if not db.fetch_one("SELECT idtiposeguro FROM tipo_seguro WHERE idtiposeguro = %s;", (poliza.id_tipo_seguro,)):
            raise ValueError(f"El tipo de seguro con ID {poliza.id_tipo_seguro} no existe")
        if not db.fetch_one("SELECT idestadopoliza FROM estado_poliza WHERE idestadopoliza = %s;", (poliza.id_estado_poliza,)):
            raise ValueError(f"El estado de póliza con ID {poliza.id_estado_poliza} no existe")

        sql = """
            UPDATE poliza
            SET idtiposeguro = %s,
                fechainicio = %s,
                fechafin = %s,
                primamensual = %s,
                idestadopoliza = %s,
                montoasegurado = %s,
                idcliente = %s
            WHERE idpoliza = %s;
        """
        params = (
            poliza.id_tipo_seguro,
            poliza.fecha_inicio,
            poliza.fecha_fin,
            poliza.prima_mensual,
            poliza.id_estado_poliza,
            poliza.monto_asegurado,
            poliza.id_cliente,
            poliza.id_poliza
        )
        db.execute(sql, params)


def eliminar_poliza(idpoliza):
    """Eliminar una póliza (verificar que no tenga dependencias)"""

    with Database() as db:
        # Verificar dependencias
        reclamaciones = db.fetch_one("SELECT idreclamacion FROM reclamacion WHERE idpoliza = %s LIMIT 1;", (idpoliza,))
        if reclamaciones:
            raise ValueError(f"No se puede eliminar la póliza {idpoliza} porque tiene reclamaciones asociadas")

        pagos = db.fetch_one("SELECT idpago FROM pago WHERE idpoliza = %s LIMIT 1;", (idpoliza,))
        if pagos:
            raise ValueError(f"No se puede eliminar la póliza {idpoliza} porque tiene pagos asociados")

        coberturas = db.fetch_one("SELECT idpoliza FROM poliza_cobertura WHERE idpoliza = %s LIMIT 1;", (idpoliza,))
        if coberturas:
            raise ValueError(f"No se puede eliminar la póliza {idpoliza} porque tiene coberturas asociadas")

        cancelada = db.fetch_one("SELECT idpolizacancelada FROM poliza_cancelada WHERE idpoliza = %s LIMIT 1;", (idpoliza,))
        if cancelada:
            raise ValueError(f"No se puede eliminar la póliza {idpoliza} porque tiene registro de cancelación")

        db.execute("DELETE FROM poliza WHERE idpoliza = %s;", (idpoliza,))


def cambiar_estado_poliza(idpoliza, nuevo_estado_id, motivo=None):
    """
    Cambiar el estado de una póliza.
    Si el nuevo estado es 'Cancelada', se añade registro en poliza_cancelada.
    """
    with Database() as db:
        # 1. Verificar que la póliza existe
        poliza = db.fetch_one(
            "SELECT idpoliza, idestadopoliza FROM poliza WHERE idpoliza = %s;",
            (idpoliza,)
        )
        if not poliza:
            raise ValueError(f"La póliza con ID {idpoliza} no existe")

        # 2. Obtener el nombre del nuevo estado (para ver si es Cancelada)
        nuevo_estado = db.fetch_one(
            "SELECT idestadopoliza, nombre FROM estado_poliza WHERE idestadopoliza = %s;",
            (nuevo_estado_id,)
        )
        if not nuevo_estado:
            raise ValueError(f"El estado con ID {nuevo_estado_id} no existe")

        # 3. Si se está cancelando, verificar que tenga motivo
        es_cancelacion = nuevo_estado["nombre"].lower() == "cancelada"

        if es_cancelacion:
            if not motivo or not motivo.strip():
                raise ValueError("Debe proporcionar un motivo para cancelar la póliza")

            # Verificar si ya estaba cancelada
            if poliza["idestadopoliza"] == nuevo_estado_id:
                raise ValueError(f"La póliza {idpoliza} ya está cancelada")

            # Verificar si ya existe un registro de cancelación
            existe_cancelacion = db.fetch_one(
                "SELECT idpolizacancelada FROM poliza_cancelada WHERE idpoliza = %s;",
                (idpoliza,)
            )
            if existe_cancelacion:
                raise ValueError(f"La póliza {idpoliza} ya tiene un registro de cancelación")

        # 4. Actualizar el estado de la póliza
        db.execute(
            "UPDATE poliza SET idestadopoliza = %s WHERE idpoliza = %s;",
            (nuevo_estado_id, idpoliza)
        )

        # 5. Si es cancelación, insertar en poliza_cancelada
        if es_cancelacion:
            # Usar el mismo ID de la póliza para mantener consistencia agg 0C al principio
            id_cancelacion = f"0C{idpoliza}"

            db.execute(
                """
                INSERT INTO poliza_cancelada (idpolizacancelada, motivo, idpoliza)
                VALUES (%s, %s, %s);
                """,
                (id_cancelacion, motivo.strip(), idpoliza)
            )

        return True
=======
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
>>>>>>> 73161b5 (mis cambios)
