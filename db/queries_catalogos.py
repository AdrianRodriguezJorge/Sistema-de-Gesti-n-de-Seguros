from models.catalogos import Pais, TipoSeguro, EstadoPoliza, TipoSiniestro, EstadoReclamacion, TipoReaseguro
from db.crud_generico import CrudGenerico

def _mapear_pais(fila):
    return Pais(idPais=fila["idpais"], nombre=fila["nombre"])

def _mapear_tipo_seguro(fila):
    return TipoSeguro(idTipoSeguro=fila["idtiposeguro"], nombre=fila["nombre"])

def _mapear_estado_poliza(fila):
    return EstadoPoliza(idEstadoPoliza=fila["idestadopoliza"], nombre=fila["nombre"])

def _mapear_tipo_siniestro(fila):
    return TipoSiniestro(idTipoSiniestro=fila["idtiposiniestro"], nombre=fila["nombre"])

def _mapear_estado_reclamacion(fila):
    return EstadoReclamacion(idEstadoReclamacion=fila["idestadoreclamacion"], nombre=fila["nombre"])

def _mapear_tipo_reaseguro(fila):
    return TipoReaseguro(idTipoReaseguro=fila["idtiporeaseguro"], nombre=fila["nombre"])


class CrudPais(CrudGenerico):
    def __init__(self):
        super().__init__("pais", "idpais", {"nombre": "nombre"}, Pais, _mapear_pais)

    def filtrar(self, idPais=None, nombre=None):
        condiciones = []
        parametros = []
        if idPais:
            condiciones.append("idpais = %s")
            parametros.append(idPais)
        if nombre:
            condiciones.append("nombre ILIKE %s")
            parametros.append(f"%{nombre}%")
        return super().filtrar(condiciones, parametros)


class CrudTipoSeguro(CrudGenerico):
    def __init__(self):
        super().__init__("tipo_seguro", "idtiposeguro", {"nombre": "nombre"}, TipoSeguro, _mapear_tipo_seguro)

    def filtrar(self, idTipoSeguro=None, nombre=None):
        condiciones = []
        parametros = []
        if idTipoSeguro:
            condiciones.append("idtiposeguro = %s")
            parametros.append(idTipoSeguro)
        if nombre:
            condiciones.append("nombre ILIKE %s")
            parametros.append(f"%{nombre}%")
        return super().filtrar(condiciones, parametros)


class CrudEstadoPoliza(CrudGenerico):
    def __init__(self):
        super().__init__("estado_poliza", "idestadopoliza", {"nombre": "nombre"}, EstadoPoliza, _mapear_estado_poliza)

    def filtrar(self, idEstadoPoliza=None, nombre=None):
        condiciones = []
        parametros = []
        if idEstadoPoliza:
            condiciones.append("idestadopoliza = %s")
            parametros.append(idEstadoPoliza)
        if nombre:
            condiciones.append("nombre ILIKE %s")
            parametros.append(f"%{nombre}%")
        return super().filtrar(condiciones, parametros)


class CrudTipoSiniestro(CrudGenerico):
    def __init__(self):
        super().__init__("tipo_siniestro", "idtiposiniestro", {"nombre": "nombre"}, TipoSiniestro, _mapear_tipo_siniestro)

    def filtrar(self, idTipoSiniestro=None, nombre=None):
        condiciones = []
        parametros = []
        if idTipoSiniestro:
            condiciones.append("idtiposiniestro = %s")
            parametros.append(idTipoSiniestro)
        if nombre:
            condiciones.append("nombre ILIKE %s")
            parametros.append(f"%{nombre}%")
        return super().filtrar(condiciones, parametros)


class CrudEstadoReclamacion(CrudGenerico):
    def __init__(self):
        super().__init__("estado_reclamacion", "idestadoreclamacion", {"nombre": "nombre"}, EstadoReclamacion, _mapear_estado_reclamacion)

    def filtrar(self, idEstadoReclamacion=None, nombre=None):
        condiciones = []
        parametros = []
        if idEstadoReclamacion:
            condiciones.append("idestadoreclamacion = %s")
            parametros.append(idEstadoReclamacion)
        if nombre:
            condiciones.append("nombre ILIKE %s")
            parametros.append(f"%{nombre}%")
        return super().filtrar(condiciones, parametros)


class CrudTipoReaseguro(CrudGenerico):
    def __init__(self):
        super().__init__("tipo_reaseguro", "idtiporeaseguro", {"nombre": "nombre"}, TipoReaseguro, _mapear_tipo_reaseguro)

    def filtrar(self, idTipoReaseguro=None, nombre=None):
        condiciones = []
        parametros = []
        if idTipoReaseguro:
            condiciones.append("idtiporeaseguro = %s")
            parametros.append(idTipoReaseguro)
        if nombre:
            condiciones.append("nombre ILIKE %s")
            parametros.append(f"%{nombre}%")
        return super().filtrar(condiciones, parametros)


# Funciones de utilidad compatibles con listado de diccionarios para la interfaz UI
def listar_paises():
    registros = CrudPais().obtener_todos()
    return [{"idpais": r.id, "nombre": r.nombre} for r in registros] if registros else []

def listar_tipos_seguro():
    registros = CrudTipoSeguro().obtener_todos()
    return [{"idtiposeguro": r.id, "nombre": r.nombre} for r in registros] if registros else []

def listar_estados_reclamacion():
    registros = CrudEstadoReclamacion().obtener_todos()
    return [{"idestadoreclamacion": r.id, "nombre": r.nombre} for r in registros] if registros else []

def listar_tipos_reaseguro():
    registros = CrudTipoReaseguro().obtener_todos()
    return [{"idtiporeaseguro": r.id, "nombre": r.nombre} for r in registros] if registros else []

