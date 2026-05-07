<<<<<<< HEAD
from datetime import date


class Reclamacion:
    def __init__(self, id_tipo_siniestro, fecha_siniestro, monto_reclamado, id_estado_reclamacion, monto_indemnizado, id_poliza, id_reclamacion=None):
        self.id_reclamacion = self._validar_id_reclamacion(id_reclamacion)
        self.id_tipo_siniestro = self._validar_id_tipo_siniestro(id_tipo_siniestro)
        self.fecha_siniestro = self._validar_fecha_siniestro(fecha_siniestro)
        self.monto_reclamado = self._validar_monto_reclamado(monto_reclamado)
        self.id_estado_reclamacion = self._validar_id_estado_reclamacion(id_estado_reclamacion)
        self.monto_indemnizado = self._validar_monto_indemnizado(monto_indemnizado)
        self.id_poliza = self._validar_id_poliza(id_poliza)

        # Validar que indemnizado no sea mayor que reclamado
        if self.monto_indemnizado > self.monto_reclamado:
            raise ValueError("El monto indemnizado no puede ser mayor que el monto reclamado")

    def _validar_id_reclamacion(self, valor):
        if valor is None:
            return None
        valor = str(valor).strip()
        if len(valor) > 20:
            raise ValueError("El ID de reclamación no puede tener más de 20 caracteres")
        return valor

    def _validar_id_tipo_siniestro(self, valor):
        try:
            valor = int(valor)
        except:
            raise ValueError("id_tipo_siniestro debe ser un entero")
        if valor <= 0:
            raise ValueError("id_tipo_siniestro debe ser positivo")
        return valor

    def _validar_fecha_siniestro(self, valor):
        if valor is None:
            raise ValueError("La fecha del siniestro es obligatoria")
        if isinstance(valor, str):
            valor = date.fromisoformat(valor)
        return valor

    def _validar_monto_reclamado(self, valor):
        try:
            valor = float(valor)
        except:
            raise ValueError("El monto reclamado debe ser un número")
        if valor <= 0:
            raise ValueError("El monto reclamado debe ser mayor que 0")
        return valor

    def _validar_id_estado_reclamacion(self, valor):
        try:
            valor = int(valor)
        except:
            raise ValueError("id_estado_reclamacion debe ser un entero")
        if valor <= 0:
            raise ValueError("id_estado_reclamacion debe ser positivo")
        return valor

    def _validar_monto_indemnizado(self, valor):
        try:
            valor = float(valor) if valor is not None else 0.0
        except:
            raise ValueError("El monto indemnizado debe ser un número")
        if valor < 0:
            raise ValueError("El monto indemnizado debe ser mayor o igual a 0")
        return valor

    def _validar_id_poliza(self, valor):
        valor = str(valor).strip()
        if len(valor) > 20:
            raise ValueError("El ID de póliza no puede tener más de 20 caracteres")
        return valor


class ReclamacionRechazada:
    def __init__(self, motivo, id_reclamacion, id_reclamacion_rechazada=None):
        self.id_reclamacion_rechazada = self._validar_id_reclamacion_rechazada(id_reclamacion_rechazada)
        self.motivo = self._validar_motivo(motivo)
        self.id_reclamacion = self._validar_id_reclamacion(id_reclamacion)

    def _validar_id_reclamacion_rechazada(self, valor):
        if valor is None:
            return None
        valor = str(valor).strip()
        return valor

    def _validar_motivo(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("El motivo no puede estar vacío")
        valor = str(valor).strip()
        if len(valor) > 200:
            raise ValueError("El motivo no puede tener más de 200 caracteres")
        return valor

    def _validar_id_reclamacion(self, valor):
        valor = str(valor).strip()
        if len(valor) > 20:
            raise ValueError("El ID de reclamación no puede tener más de 20 caracteres")
        return valor
=======
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
>>>>>>> 73161b5 (mis cambios)
