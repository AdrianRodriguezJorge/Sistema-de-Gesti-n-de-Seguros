from data.class_entidadBase import EntidadBase

class Pago(EntidadBase):
    def __init__(self, idPoliza, fechaPago, montoPagado, idPago=None):
        super().__init__(id=idPago)
        self.idPoliza = self._validarId(idPoliza)
        self.fechaPago = fechaPago
        self.montoPagado = self._validarMontoPositivo(montoPagado, "monto pagado")

    def _validarMontoPositivo(self, valor, campo):
        monto = float(valor)
        if monto <= 0: 
            raise ValueError(f"El {campo} debe ser positivo.")
        return monto
