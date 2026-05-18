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
