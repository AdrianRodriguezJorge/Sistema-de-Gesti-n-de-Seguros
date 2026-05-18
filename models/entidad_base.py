class EntidadBase:
    def __init__(self, id=None):
        self.id = self._validarId(id)

    def _validarId(self, valor):
        if valor is None: 
            return None 
        try:
            valor = int(valor)
            if valor <= 0: 
                raise ValueError()  
            return valor
        except (ValueError, TypeError):
            raise ValueError("El ID debe ser un número entero positivo.")
