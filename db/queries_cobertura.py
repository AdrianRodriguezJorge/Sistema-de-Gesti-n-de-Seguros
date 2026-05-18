from data.class_cobertura import Cobertura
from db.crud_generico import CrudGenerico

def _mapear_cobertura(fila):
    return Cobertura(idCobertura=fila["idcobertura"], descripcion=fila["descripcion"])

class CrudCobertura(CrudGenerico):
    def __init__(self):
        super().__init__("cobertura", "idcobertura", {"descripcion": "descripcion"}, Cobertura, _mapear_cobertura)

    def filtrar(self, idCobertura=None, descripcion=None):
        condiciones = []
        parametros = []
        if idCobertura:
            condiciones.append("idcobertura = %s")
            parametros.append(idCobertura)
        if descripcion:
            condiciones.append("descripcion ILIKE %s")
            parametros.append(f"%{descripcion}%")
        return super().filtrar(condiciones, parametros)
