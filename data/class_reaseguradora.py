from data.class_entidadConNombre import EntidadConNombre

class Reaseguradora(EntidadConNombre):
    _maxNombre = 100
    def __init__(self, nombre, idPais, idTipoReaseguro, idReaseguradora=None):
        super().__init__(id=idReaseguradora, nombre=nombre)
        self.idPais = self._validarId(idPais)
        self.idTipoReaseguro = self._validarId(idTipoReaseguro)
