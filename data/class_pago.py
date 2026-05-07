<<<<<<< HEAD
from datetime import date


class Pago:
    def __init__(self, id_poliza, fecha_pago, monto_pagado, id_pago=None):
        self.id_pago = self._validar_id_pago(id_pago)
        self.id_poliza = self._validar_id_poliza(id_poliza)
        self.fecha_pago = self._validar_fecha_pago(fecha_pago)
        self.monto_pagado = self._validar_monto_pagado(monto_pagado)

    def _validar_id_pago(self, valor):
        if valor is None:
            return None
        try:
            valor = int(valor)
        except:
            raise ValueError("id_pago debe ser un entero")
        if valor <= 0:
            raise ValueError("id_pago debe ser positivo")
        return valor

    def _validar_id_poliza(self, valor):
        valor = str(valor).strip()
        if len(valor) > 20:
            raise ValueError("El ID de póliza no puede tener más de 20 caracteres")
        return valor

    def _validar_fecha_pago(self, valor):
        if valor is None:
            raise ValueError("La fecha de pago es obligatoria")
        if isinstance(valor, str):
            valor = date.fromisoformat(valor)
        return valor

    def _validar_monto_pagado(self, valor):
        try:
            valor = float(valor)
        except:
            raise ValueError("El monto pagado debe ser un número")
        if valor <= 0:
            raise ValueError("El monto pagado debe ser mayor que 0")
        return valor
=======
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
>>>>>>> 73161b5 (mis cambios)
