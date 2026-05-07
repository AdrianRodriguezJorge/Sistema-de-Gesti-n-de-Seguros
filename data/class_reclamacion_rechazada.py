from data.class_entidadBase import EntidadBase

class ReclamacionRechazada(EntidadBase):
    def __init__(self, motivo, idReclamacion, idReclamacionRechazada=None):
        super().__init__(id=idReclamacionRechazada)
        self.idReclamacion = self._validarId(idReclamacion)
        self.motivo = self._validarMotivo(motivo)

    def _validarMotivo(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("El motivo del rechazo es obligatorio.")
        if len(str(valor)) > 200:
            raise ValueError("El motivo excede los 200 caracteres.")
        return str(valor).strip()
