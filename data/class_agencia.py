from data.class_entidadConNombre import EntidadConNombre

class Agencia(EntidadConNombre):
    _maxNombre = 100
    def __init__(self, nombre, direccion, telefono, email, directorGeneral, jefeSeguros, jefeReclamaciones, idAgencia=None):
        super().__init__(id=idAgencia, nombre=nombre)
        self.direccion = self._validarTexto(direccion, 200, "dirección")
        self.telefono = self._validarTexto(telefono, 20, "teléfono")
        self.email = self._validarTexto(email, 100, "email")
        self.directorGeneral = self._validarTexto(directorGeneral, 100, "director general")
        self.jefeSeguros = self._validarTexto(jefeSeguros, 100, "jefe de seguros")
        self.jefeReclamaciones = self._validarTexto(jefeReclamaciones, 100, "jefe de reclamaciones")

    def _validarTexto(self, valor, maxLen, campo):
        if not valor: 
            raise ValueError(f"El campo {campo} es obligatorio.")
        if len(str(valor)) > maxLen:
            raise ValueError(f"{campo} excede los {maxLen} caracteres.")  
        return str(valor).strip()
