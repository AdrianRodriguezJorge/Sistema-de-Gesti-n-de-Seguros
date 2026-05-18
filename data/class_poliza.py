from data.class_entidadBase import EntidadBase

class Poliza(EntidadBase):
    def __init__(self, idTipoSeguro, fechaInicio, fechaFin, primaMensual, idEstadoPoliza, montoAsegurado, idCliente, idPoliza=None):
        super().__init__(id=idPoliza)
        self.idTipoSeguro = self._validarId(idTipoSeguro)
        self.fechaInicio = self._validarFecha(fechaInicio, "fecha de inicio")
        self.fechaFin = self._validarFecha(fechaFin, "fecha de fin")
        self.primaMensual = self._validarMontoPositivo(primaMensual, "prima mensual")
        self.idEstadoPoliza = self._validarId(idEstadoPoliza)
        self.montoAsegurado = self._validarMontoPositivo(montoAsegurado, "monto asegurado")
        self.idCliente = self._validarId(idCliente)
        self._validarPeriodo(self.fechaInicio, self.fechaFin)

    def _validarMontoPositivo(self, valor, campo):
        try:
            monto = float(valor)
            if monto <= 0:
                raise ValueError(f"El {campo} debe ser mayor a cero.")
            return monto
        except (ValueError, TypeError):
            raise ValueError(f"El {campo} debe ser un valor numérico válido.")

    def _validarFecha(self, valor, campo):
        if not valor:
            raise ValueError(f"La {campo} es obligatoria.")
        return valor

    def _validarPeriodo(self, inicio, fin):
        if inicio >= fin:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin.")
