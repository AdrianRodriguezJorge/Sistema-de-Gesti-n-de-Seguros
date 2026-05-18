from models.reclamacion_rechazada import ReclamacionRechazada
from db.crud_generico import CrudGenerico

def _mapear_reclamacion_rechazada(fila):
    return ReclamacionRechazada(idReclamacionRechazada=fila["idreclamacionrechazada"], motivo=fila["motivo"], idReclamacion=fila["idreclamacion"])

class CrudReclamacionRechazada(CrudGenerico):
    def __init__(self):
        super().__init__("reclamacion_rechazada", "idreclamacionrechazada", {"motivo": "motivo", "idreclamacion": "idReclamacion"}, ReclamacionRechazada, _mapear_reclamacion_rechazada)

    def filtrar(self, idReclamacionRechazada=None, idReclamacion=None):
        condiciones = []
        parametros = []
        if idReclamacionRechazada:
            condiciones.append("idreclamacionrechazada = %s")
            parametros.append(idReclamacionRechazada)
        if idReclamacion:
            condiciones.append("idreclamacion = %s")
            parametros.append(idReclamacion)
        return super().filtrar(condiciones, parametros)
