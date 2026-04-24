class CatalogoBase:
    """Clase base para catálogos simples (id + nombre)."""

    _max_nombre = 100  # sobreescribir en subclases si el VARCHAR es distinto

    def __init__(self, nombre, id_=None):
        self.id_ = self._validar_id(id_)
        self.nombre = self._validar_nombre(nombre)

    def _validar_id(self, valor):
        if valor is None:
            return None
        try:
            valor = int(valor)
        except:
            raise ValueError("El ID debe ser un entero")
        if valor <= 0:
            raise ValueError("El ID debe ser positivo")
        return valor

    def _validar_nombre(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("El nombre no puede estar vacío")
        valor = str(valor).strip()
        if len(valor) > self._max_nombre:
            raise ValueError(f"El nombre no puede tener más de {self._max_nombre} caracteres")
        return valor


class Pais(CatalogoBase):
    _max_nombre = 100

class TipoSeguro(CatalogoBase):
    _max_nombre = 50

class EstadoPoliza(CatalogoBase):
    _max_nombre = 30

class TipoSiniestro(CatalogoBase):
    _max_nombre = 50

class EstadoReclamacion(CatalogoBase):
    _max_nombre = 30

class TipoReaseguro(CatalogoBase):
    _max_nombre = 50
