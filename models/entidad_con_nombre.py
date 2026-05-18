from models.entidad_base import EntidadBase
class EntidadConNombre(EntidadBase):
    _maxNombre = 100

    def __init__(self, id=None, nombre=None):
        super().__init__(id=id)
        self.nombre = self._validarNombre(nombre)

    def _validarNombre(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("El nombre no puede estar vacío.")
        valor = str(valor).strip()
        if len(valor) > self._maxNombre:
            raise ValueError(f"El nombre no puede superar los {self._maxNombre} caracteres.")
        return valor
