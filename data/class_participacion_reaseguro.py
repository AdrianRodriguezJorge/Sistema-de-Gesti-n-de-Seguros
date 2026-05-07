from data.class_entidadBase import EntidadBase

class ParticipacionReaseguro(EntidadBase):
    def __init__(self, idReaseguradora, idTipoSeguro, porcentaje):
        super().__init__(id=None)
        self.idReaseguradora = self._validarId(idReaseguradora)
        self.idTipoSeguro = self._validarId(idTipoSeguro)
        self.porcentaje = self._validarPorcentaje(porcentaje)

    def _validarPorcentaje(self, valor):
        try:
            p = float(valor)
            if not (0 <= p <= 100):
                raise ValueError("El porcentaje debe estar entre 0 y 100.")
            return p
        except (ValueError, TypeError):
            raise ValueError("El porcentaje debe ser un número válido.")
