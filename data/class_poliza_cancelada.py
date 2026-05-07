from data.class_entidadBase import EntidadBase

class PolizaCancelada(EntidadBase):
    def __init__(self, motivo, idPoliza, idPolizaCancelada=None):
        super().__init__(id=idPolizaCancelada)
        self.idPoliza = self._validarId(idPoliza)
        self.motivo = self._validarMotivo(motivo)

    def _validarMotivo(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("El motivo de cancelación es obligatorio.")
        valor = str(valor).strip()
        if len(valor) > 200:
            raise ValueError("El motivo no puede superar los 200 caracteres.")
        return valor
