from models.poliza_cancelada import PolizaCancelada
from db.crud_generico import CrudGenerico

def _mapear_poliza_cancelada(fila):
    return PolizaCancelada(idPolizaCancelada=fila["idpolizacancelada"], motivo=fila["motivo"], idPoliza=fila["idpoliza"])

class CrudPolizaCancelada(CrudGenerico):
    def __init__(self):
        super().__init__("poliza_cancelada", "idpolizacancelada", {"motivo": "motivo", "idpoliza": "idPoliza"}, PolizaCancelada, _mapear_poliza_cancelada)

    def filtrar(self, idPolizaCancelada=None, idPoliza=None):
        condiciones = []
        parametros = []
        if idPolizaCancelada:
            condiciones.append("idpolizacancelada = %s")
            parametros.append(idPolizaCancelada)
        if idPoliza:
            condiciones.append("idpoliza = %s")
            parametros.append(idPoliza)
        return super().filtrar(condiciones, parametros)
