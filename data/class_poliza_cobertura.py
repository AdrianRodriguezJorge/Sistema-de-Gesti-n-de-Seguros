from data.class_entidadBase import EntidadBase

class PolizaCobertura(EntidadBase):
    def __init__(self, idPoliza, idCobertura, monto):
        super().__init__(id=None) 
        self.idPoliza = self._validarId(idPoliza)
        self.idCobertura = self._validarId(idCobertura)
        self.monto = self._validarMontoPositivo(monto, "monto de cobertura")

    def _validarMontoPositivo(self, valor, campo):
        monto = float(valor)
        if monto <= 0:
            raise ValueError(f"El {campo} debe ser mayor a cero.")
        return monto
