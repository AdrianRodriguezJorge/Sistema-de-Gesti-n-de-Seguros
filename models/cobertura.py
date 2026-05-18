from models.entidad_base import EntidadBase

class Cobertura(EntidadBase):
    def __init__(self, descripcion, idCobertura=None):
        super().__init__(id=idCobertura)
        self.descripcion = self._validarDescripcion(descripcion)

    def _validarDescripcion(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("La descripción de la cobertura no puede estar vacía.")
        valor = str(valor).strip()
        if len(valor) > 200:
            raise ValueError("La descripción no puede superar los 200 caracteres.")
        return valor
