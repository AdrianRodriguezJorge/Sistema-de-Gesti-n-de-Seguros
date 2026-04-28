class Cobertura:
    """Catálogo de coberturas (sin relación directa con póliza)"""

    def __init__(self, descripcion, id_cobertura=None):
        self.id_cobertura = self._validar_id_cobertura(id_cobertura)
        self.descripcion = self._validar_descripcion(descripcion)

    def _validar_id_cobertura(self, valor):
        if valor is None:
            return None
        try:
            valor = int(valor)
        except:
            raise ValueError("El ID de cobertura debe ser un entero")
        if valor <= 0:
            raise ValueError("El ID de cobertura debe ser positivo")
        return valor

    def _validar_descripcion(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("La descripción no puede estar vacía")
        valor = str(valor).strip()
        if len(valor) > 200:
            raise ValueError("La descripción no puede tener más de 200 caracteres")
        return valor


class PolizaCobertura:
    """Relación N:M entre póliza y cobertura"""

    def __init__(self, id_poliza, id_cobertura, monto):
        self.id_poliza = self._validar_id_poliza(id_poliza)
        self.id_cobertura = self._validar_id_cobertura(id_cobertura)
        self.monto = self._validar_monto(monto)

    def _validar_id_poliza(self, valor):
        valor = str(valor).strip()
        if len(valor) > 20:
            raise ValueError("El ID de póliza no puede tener más de 20 caracteres")
        return valor

    def _validar_id_cobertura(self, valor):
        try:
            valor = int(valor)
        except:
            raise ValueError("id_cobertura debe ser un entero")
        if valor <= 0:
            raise ValueError("id_cobertura debe ser positivo")
        return valor

    def _validar_monto(self, valor):
        try:
            valor = float(valor)
        except:
            raise ValueError("El monto debe ser un número")
        if valor <= 0:
            raise ValueError("El monto debe ser mayor que 0")
        return valor