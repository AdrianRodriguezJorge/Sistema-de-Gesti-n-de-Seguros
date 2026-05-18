import re
from models.entidad_con_nombre import EntidadConNombre

class Cliente(EntidadConNombre):
    _maxNombre = 50 
    def __init__(self, nombre, apellidos, noIdentificacion, edad, sexo, idPais, dirPostal=None, telefono=None, correo=None, idCliente=None):
        super().__init__(id=idCliente, nombre=nombre)
        self.apellidos = self._validarTexto(apellidos, 100)
        self.noIdentificacion = self._validarTexto(noIdentificacion, 50)
        self.edad = self._validarEdad(edad)
        self.sexo = self._validarSexo(sexo)
        self.idPais = self._validarId(idPais)
        self.dirPostal = str(dirPostal)[:150] if dirPostal else None
        self.telefono = str(telefono)[:20] if telefono else None
        self.correo = self._validarEmail(correo) if correo else None

    def _validarTexto(self, v, m):
        if not v: 
            raise ValueError("Campo obligatorio faltante")
        return str(v).strip()[:m]

    def _validarEdad(self, e):
        if not (0 <= int(e) <= 120): 
            raise ValueError("Edad fuera de rango (0-120)")
        return int(e)

    def _validarSexo(self, s):
        s = str(s).upper()
        if s not in ('M', 'F'): 
            raise ValueError("Sexo debe ser M o F")
        return s

    def _validarEmail(self, e):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", e): 
            raise ValueError("Email inválido")
        return e
