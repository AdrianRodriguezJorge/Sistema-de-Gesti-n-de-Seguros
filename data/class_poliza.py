from datetime import date


class Poliza:
    def __init__(self, id_tipo_seguro, fecha_inicio, fecha_fin, prima_mensual, id_estado_poliza, monto_asegurado, id_cliente, id_poliza=None):
        self.id_poliza = self._validar_id_poliza(id_poliza)
        self.id_tipo_seguro = self._validar_id_tipo_seguro(id_tipo_seguro)
        self.fecha_inicio = self._validar_fecha_inicio(fecha_inicio)
        self.fecha_fin = self._validar_fecha_fin(fecha_fin)
        self.prima_mensual = self._validar_prima_mensual(prima_mensual)
        self.id_estado_poliza = self._validar_id_estado_poliza(id_estado_poliza)
        self.monto_asegurado = self._validar_monto_asegurado(monto_asegurado)
        self.id_cliente = self._validar_id_cliente(id_cliente)

    def _validar_id_poliza(self, valor):
        if valor is None:
            return None
        valor = str(valor).strip()
        if len(valor) > 20:
            raise ValueError("El ID de póliza no puede tener más de 20 caracteres")
        return valor

    def _validar_id_tipo_seguro(self, valor):
        try:
            valor = int(valor)
        except:
            raise ValueError("id_tipo_seguro debe ser un entero")
        if valor <= 0:
            raise ValueError("id_tipo_seguro debe ser positivo")
        return valor

    def _validar_fecha_inicio(self, valor):
        if valor is None:
            raise ValueError("La fecha de inicio es obligatoria")
        if isinstance(valor, str):
            valor = date.fromisoformat(valor)
        return valor

    def _validar_fecha_fin(self, valor):
        if valor is None:
            raise ValueError("La fecha de fin es obligatoria")
        if isinstance(valor, str):
            valor = date.fromisoformat(valor)
        return valor

    def _validar_prima_mensual(self, valor):
        try:
            valor = float(valor)
        except:
            raise ValueError("La prima mensual debe ser un número")
        if valor <= 0:
            raise ValueError("La prima mensual debe ser mayor que 0")
        return valor

    def _validar_id_estado_poliza(self, valor):
        try:
            valor = int(valor)
        except:
            raise ValueError("id_estado_poliza debe ser un entero")
        if valor <= 0:
            raise ValueError("id_estado_poliza debe ser positivo")
        return valor

    def _validar_monto_asegurado(self, valor):
        try:
            valor = float(valor)
        except:
            raise ValueError("El monto asegurado debe ser un número")
        if valor <= 0:
            raise ValueError("El monto asegurado debe ser mayor que 0")
        return valor

    def _validar_id_cliente(self, valor):
        try:
            valor = int(valor)
        except:
            raise ValueError("id_cliente debe ser un entero")
        if valor <= 0:
            raise ValueError("id_cliente debe ser positivo")
        return valor