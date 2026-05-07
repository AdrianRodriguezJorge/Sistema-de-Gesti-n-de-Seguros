from datetime import date, timedelta
from db.queries_cliente import CrudCliente
from db.queries_poliza import CrudPoliza
from db.queries_catalogos import CrudTipoSeguro, CrudEstadoPoliza
from db.conexionDB import Database

def validar_existencia_cliente(identificador_cliente):
    cliente = CrudCliente().obtener(identificador_cliente)
    if not cliente:
        raise ValueError(f"El cliente con ID {identificador_cliente} no existe en el sistema.")
    return cliente

def validar_existencia_tipo_seguro(identificador_tipo_seguro):
    tipo_seguro = CrudTipoSeguro().obtener(identificador_tipo_seguro)
    if not tipo_seguro:
        raise ValueError(f"El tipo de seguro con ID {identificador_tipo_seguro} no existe en el sistema.")
    return tipo_seguro

def validar_existencia_estado_poliza(identificador_estado_poliza):
    estado_poliza = CrudEstadoPoliza().obtener(identificador_estado_poliza)
    if not estado_poliza:
        raise ValueError(f"El estado de poliza con ID {identificador_estado_poliza} no existe en el sistema.")
    return estado_poliza

def validar_claves_foraneas_poliza(identificador_cliente, identificador_tipo_seguro, identificador_estado_poliza):
    validar_existencia_cliente(identificador_cliente)
    validar_existencia_tipo_seguro(identificador_tipo_seguro)
    validar_existencia_estado_poliza(identificador_estado_poliza)

def validar_poliza_activa(identificador_poliza):
    poliza = CrudPoliza().obtener(identificador_poliza)
    if not poliza:
        raise ValueError(f"La poliza con ID {identificador_poliza} no existe en el sistema.")
    estado_poliza = CrudEstadoPoliza().obtener(poliza.idEstadoPoliza)
    if estado_poliza and estado_poliza.nombre != "Activa":
        raise ValueError(f"No se pueden crear reclamaciones sobre polizas con estado '{estado_poliza.nombre}'. La poliza debe estar activa.")
    if poliza.fechaFin < date.today():
        raise ValueError("No se pueden crear reclamaciones sobre polizas vencidas.")
    return poliza

def obtener_polizas_proximas_vencer(dias=30):
    fecha_limite = date.today() + timedelta(days=dias)
    sql = """
        SELECT p.*, 
               c.nombre as cli_nombre, c.apellidos as cli_apellidos,
               ep.nombre as estado_nombre
        FROM poliza p
        JOIN cliente c ON p.idcliente = c.idcliente
        JOIN estado_poliza ep ON p.idestadopoliza = ep.idestadopoliza
        WHERE p.fecha_fin BETWEEN CURRENT_DATE AND %s
        AND ep.nombre = 'Activa'
        ORDER BY p.fecha_fin
    """
    with Database() as db:
        return db.fetch_all(sql, (fecha_limite,))

def obtener_reclamaciones_pendientes():
    sql = """
        SELECT r.*, 
               p.idcliente,
               c.nombre as cli_nombre, c.apellidos as cli_apellidos,
               er.nombre as estado_nombre
        FROM reclamacion r
        JOIN poliza p ON r.idpoliza = p.idpoliza
        JOIN cliente c ON p.idcliente = c.idcliente
        JOIN estado_reclamacion er ON r.idestadoreclamacion = er.idestadoreclamacion
        WHERE er.nombre = 'En proceso'
        ORDER BY r.fecha_siniestro DESC
    """
    with Database() as db:
        return db.fetch_all(sql)

def obtener_resumen_alertas(dias=30):
    polizas_vencer = obtener_polizas_proximas_vencer(dias)
    reclamaciones_pendientes = obtener_reclamaciones_pendientes()
    return {
        "polizas_proximas_vencer": polizas_vencer,
        "reclamaciones_pendientes": reclamaciones_pendientes,
        "total_polizas_vencer": len(polizas_vencer),
        "total_reclamaciones_pendientes": len(reclamaciones_pendientes)
    }
