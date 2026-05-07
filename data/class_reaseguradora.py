<<<<<<< HEAD
class Reaseguradora:
    def __init__(self, nombre, id_pais, id_tipo_reaseguro, email=None, id_reaseguradora=None):
        self.id_reaseguradora = self._validar_id_reaseguradora(id_reaseguradora)
        self.nombre = self._validar_nombre(nombre)
        self.email = self._validar_email(email)
        self.id_pais = self._validar_id_pais(id_pais)
        self.id_tipo_reaseguro = self._validar_id_tipo_reaseguro(id_tipo_reaseguro)

    def _validar_id_reaseguradora(self, valor):
        if valor is None:
            return None
        valor = str(valor).strip()
        if len(valor) > 15:
            raise ValueError("El ID de reaseguradora no puede tener más de 15 caracteres")
        return valor

    def _validar_nombre(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("El nombre no puede estar vacío")
        valor = str(valor).strip()
        if len(valor) > 100:
            raise ValueError("El nombre no puede tener más de 100 caracteres")
        return valor

    def _validar_email(self, valor):
        if valor is None or not str(valor).strip():
            return None
        valor = str(valor).strip()
        if len(valor) > 100:
            raise ValueError("El email no puede tener más de 100 caracteres")
        if '@' not in valor:
            raise ValueError("El email debe tener un formato válido")
        return valor

    def _validar_id_pais(self, valor):
        try:
            valor = int(valor)
        except:
            raise ValueError("id_pais debe ser un entero")
        if valor <= 0:
            raise ValueError("id_pais debe ser positivo")
        return valor

    def _validar_id_tipo_reaseguro(self, valor):
        try:
            valor = int(valor)
        except:
            raise ValueError("id_tipo_reaseguro debe ser un entero")
        if valor <= 0:
            raise ValueError("id_tipo_reaseguro debe ser positivo")
        return valor


class ParticipacionReaseguro:
    def __init__(self, id_reaseguradora, id_tipo_seguro, porcentaje):
        self.id_reaseguradora = self._validar_id_reaseguradora(id_reaseguradora)
        self.id_tipo_seguro = self._validar_id_tipo_seguro(id_tipo_seguro)
        self.porcentaje = self._validar_porcentaje(porcentaje)

    def _validar_id_reaseguradora(self, valor):
        valor = str(valor).strip()
        if len(valor) > 15:
            raise ValueError("El ID de reaseguradora no puede tener más de 15 caracteres")
        return valor

    def _validar_id_tipo_seguro(self, valor):
        try:
            valor = int(valor)
        except:
            raise ValueError("id_tipo_seguro debe ser un entero")
        if valor <= 0:
            raise ValueError("id_tipo_seguro debe ser positivo")
        return valor

    def _validar_porcentaje(self, valor):
        try:
            valor = float(valor)
        except:
            raise ValueError("El porcentaje debe ser un número")
        if valor < 0 or valor > 100:
            raise ValueError("El porcentaje debe estar entre 0 y 100")
        return valor
=======
from data.class_entidadConNombre import EntidadConNombre

class Reaseguradora(EntidadConNombre):
    _maxNombre = 100
    def __init__(self, nombre, idPais, idTipoReaseguro, idReaseguradora=None):
        super().__init__(id=idReaseguradora, nombre=nombre)
        self.idPais = self._validarId(idPais)
        self.idTipoReaseguro = self._validarId(idTipoReaseguro)
>>>>>>> 73161b5 (mis cambios)
