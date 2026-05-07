<<<<<<< HEAD
from db.conexionDB import Database


def insertar_pago(pago):
    """Insertar un nuevo pago validando que no haya pagos recientes (mínimo 30 días entre pagos)"""

    with Database() as db:
        # 1. Verificar que la póliza existe
        poliza = db.fetch_one("SELECT idpoliza FROM poliza WHERE idpoliza = %s;", (pago.id_poliza,))
        if not poliza:
            raise ValueError(f"La póliza con ID {pago.id_poliza} no existe")

        # 2. Validar que no haya un pago en los últimos 30 días (evualar si es mejor hacerlo por mes)
        pago_reciente = db.fetch_one(
            """
            SELECT idpago, fechapago
            FROM pago
            WHERE idpoliza = %s
                AND fechapago >= %s - INTERVAL '30 days'
            ORDER BY fechapago DESC
            LIMIT 1;
            """,
            (pago.id_poliza, pago.fecha_pago)
        )

        if pago_reciente:
            dias_diferencia = (pago.fecha_pago - pago_reciente["fechapago"]).days
            raise ValueError(
                f"Ya existe un pago para esta póliza el {pago_reciente['fechapago']}. "
                f"Deben pasar al menos 30 días entre pagos. "
                f"Han pasado solo {dias_diferencia} días."
            )

        # 3. Tiene q pagar lo q cuesta la poliza al mes
        prima = db.fetch_one(
            "SELECT primamensual FROM poliza WHERE idpoliza = %s;",
            (pago.id_poliza,)
        )
        if prima and pago.monto_pagado != prima["primamensual"]:
            raise ValueError(
                f"El monto pagado ({pago.monto_pagado}) tiene que ser igual a la prima mensual ({prima['primamensual']})"
            )

        # 4. Validar que no se pague una póliza vencida o cancelada
        estado_poliza = db.fetch_one(
            """
            SELECT ep.nombre as estado_nombre
            FROM poliza p
            JOIN estado_poliza ep ON p.idestadopoliza = ep.idestadopoliza
            WHERE p.idpoliza = %s;
            """,
            (pago.id_poliza,)
        )
        if estado_poliza and estado_poliza["estado_nombre"].lower() in ["vencida", "cancelada"]:
            raise ValueError(f"No se puede pagar una póliza que está {estado_poliza['estado_nombre']}")

        # 5. Insertar el pago
        sql = """
            INSERT INTO pago (idpago, idpoliza, fechapago, montopagado)
            VALUES (%s, %s, %s, %s)
            RETURNING idpago;
        """
        params = (
            pago.id_pago,
            pago.id_poliza,
            pago.fecha_pago,
            pago.monto_pagado
        )
        result = db.fetch_one(sql, params)
        return result["idpago"] if result else None


def listar_pagos():
    sql = """
        SELECT p.idpago, p.idpoliza, p.fechapago, p.montopagado, c.nombre || ' ' || c.apellidos as cliente
        FROM pago p
        JOIN poliza po ON p.idpoliza = po.idpoliza
        JOIN cliente c ON po.idcliente = c.idcliente
        ORDER BY p.fechapago DESC;
    """
    with Database() as db:
        return db.fetch_all(sql)


def listar_pagos_por_poliza(idpoliza):
    sql = """
        SELECT idpago, fechapago, montopagado
        FROM pago
        WHERE idpoliza = %s
        ORDER BY fechapago DESC;
    """
    with Database() as db:
        return db.fetch_all(sql, (idpoliza,))


def obtener_pago_por_id(idpago):
    sql = """
        SELECT p.*, po.idcliente
        FROM pago p
        JOIN poliza po ON p.idpoliza = po.idpoliza
        WHERE p.idpago = %s;
    """
    with Database() as db:
        return db.fetch_one(sql, (idpago,))


def actualizar_pago(pago):
    """Actualizar un pago existente"""

    with Database() as db:
        # Verificar que existe
        existente = db.fetch_one("SELECT idpago FROM pago WHERE idpago = %s;", (pago.id_pago,))
        if not existente:
            raise ValueError(f"El pago con ID {pago.id_pago} no existe")

        sql = """
            UPDATE pago
            SET idpoliza = %s, fechapago = %s, montopagado = %s
            WHERE idpago = %s;
        """
        params = (
            pago.id_poliza,
            pago.fecha_pago,
            pago.monto_pagado,
            pago.id_pago
        )
        db.execute(sql, params)


def eliminar_pago(idpago):
    """Eliminar un pago"""
    with Database() as db:
        db.execute("DELETE FROM pago WHERE idpago = %s;", (idpago,))


def total_pagado_por_poliza(idpoliza):
    """Calcular el total pagado de una póliza"""
    sql = "SELECT COALESCE(SUM(montopagado), 0) as total FROM pago WHERE idpoliza = %s;"
    with Database() as db:
        result = db.fetch_one(sql, (idpoliza,))
        return result["total"] if result else 0


def total_pagado_por_cliente(idcliente):
    """Calcular el total pagado por un cliente"""
    sql = """
        SELECT COALESCE(SUM(p.montopagado), 0) as total
        FROM pago p
        JOIN poliza po ON p.idpoliza = po.idpoliza
        WHERE po.idcliente = %s;
    """
    with Database() as db:
        result = db.fetch_one(sql, (idcliente,))
        return result["total"] if result else 0
=======
from data.class_pago import Pago
from db.crud_generico import CrudGenerico
from db.conexionDB import Database

def _mapear_pago(fila):
    return Pago(idPago=fila["idpago"], idPoliza=fila["idpoliza"], fechaPago=fila["fecha_pago"], montoPagado=fila["monto_pagado"])

class CrudPago(CrudGenerico):
    def __init__(self):
        super().__init__("pago", "idpago", {"idpoliza": "idPoliza", "fecha_pago": "fechaPago", "monto_pagado": "montoPagado"}, Pago, _mapear_pago)

    def filtrar(self, idPago=None, idPoliza=None, fechaPago=None, montoPagado=None):
        condiciones = []
        parametros = []
        if idPago:
            condiciones.append("idpago = %s")
            parametros.append(idPago)
        if idPoliza:
            condiciones.append("idpoliza = %s")
            parametros.append(idPoliza)
        if fechaPago:
            condiciones.append("fecha_pago = %s")
            parametros.append(fechaPago)
        if montoPagado:
            condiciones.append("monto_pagado = %s")
            parametros.append(montoPagado)
        return super().filtrar(condiciones, parametros)
    
    def obtener_ingresos_mensuales(self, año=None):
        sql = """
            SELECT 
                EXTRACT(MONTH FROM fecha_pago) as mes,
                TO_CHAR(fecha_pago, 'Month') as nombre_mes,
                SUM(monto_pagado) as ingreso_mensual
            FROM pago 
            WHERE 1=1
        """
        params = []
        if año:
            sql += " AND EXTRACT(YEAR FROM fecha_pago) = %s"
            params.append(año)
        sql += " GROUP BY mes, nombre_mes ORDER BY mes"
        with Database() as db:
            return db.fetch_all(sql, tuple(params))
    
    def obtener_total_anual(self, año=None):
        sql = "SELECT COALESCE(SUM(monto_pagado), 0) as total_anual FROM pago WHERE 1=1"
        params = []
        if año:
            sql += " AND EXTRACT(YEAR FROM fecha_pago) = %s"
            params.append(año)
        with Database() as db:
            return db.fetch_one(sql, tuple(params))["total_anual"]
>>>>>>> 73161b5 (mis cambios)
