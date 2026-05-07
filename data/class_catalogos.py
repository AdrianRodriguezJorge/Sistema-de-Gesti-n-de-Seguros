from data.class_entidadConNombre import EntidadConNombre

class Pais(EntidadConNombre):
    _maxNombre = 100
    def __init__(self, nombre, idPais=None):
        super().__init__(id=idPais, nombre=nombre)

class TipoSeguro(EntidadConNombre):
    _maxNombre = 50
    def __init__(self, nombre, idTipoSeguro=None):
        super().__init__(id=idTipoSeguro, nombre=nombre)

class EstadoPoliza(EntidadConNombre):
    _maxNombre = 30
    def __init__(self, nombre, idEstadoPoliza=None):
        super().__init__(id=idEstadoPoliza, nombre=nombre)

class TipoSiniestro(EntidadConNombre):
    _maxNombre = 50
    def __init__(self, nombre, idTipoSiniestro=None):
        super().__init__(id=idTipoSiniestro, nombre=nombre)

class EstadoReclamacion(EntidadConNombre):
    _maxNombre = 30
    def __init__(self, nombre, idEstadoReclamacion=None):
        super().__init__(id=idEstadoReclamacion, nombre=nombre)

class TipoReaseguro(EntidadConNombre):
    _maxNombre = 50
    def __init__(self, nombre, idTipoReaseguro=None):
        super().__init__(id=idTipoReaseguro, nombre=nombre)
