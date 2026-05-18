from data.class_entidadBase import EntidadBase

class Reclamacion(EntidadBase):
    def __init__(self, idTipoSiniestro, fechaSiniestro, montoReclamado, idEstadoReclamacion, idPoliza, montoIndemnizado=0, idReclamacion=None):
        super().__init__(id=idReclamacion)
        self.idTipoSiniestro = self._validarId(idTipoSiniestro)
        self.fechaSiniestro = fechaSiniestro
        self.montoReclamado = self._validarMontoPositivo(montoReclamado, "monto reclamado")
        self.idEstadoReclamacion = self._validarId(idEstadoReclamacion)
        self.idPoliza = self._validarId(idPoliza)
        self.montoIndemnizado = self._validarIndemnizacion(montoIndemnizado, self.montoReclamado)

    def _validarMontoPositivo(self, valor, campo):
        monto = float(valor)
        if monto <= 0:
            raise ValueError(f"El {campo} debe ser positivo.")
        return monto

    def _validarIndemnizacion(self, monto, reclamado):
        monto = float(monto)
        if monto < 0:
            raise ValueError("El monto indemnizado no puede ser negativo.")
        if monto > reclamado:
            raise ValueError("El monto indemnizado no puede ser mayor al reclamado.")
        return monto
