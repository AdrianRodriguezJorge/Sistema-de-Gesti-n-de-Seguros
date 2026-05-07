import re
from data.class_entidadConNombre import EntidadConNombre

<<<<<<< HEAD
class Cliente:
    def __init__(self, nombre, apellidos, noIdentificación, edad, sexo, telefono, correo, idpais, dirPostal=None, idcliente=None):
        self.idcliente = self._validar_idcliente(idcliente)
        self.noIdentificación = self._validar_noIdentificación(noIdentificación)
        self.nombre = self._validar_nombre(nombre)
        self.apellidos = self._validar_apellidos(apellidos)
        self.edad = self._validar_edad(edad)
        self.sexo = self._validar_sexo(sexo)
        self.telefono = self._validar_telefono(telefono)
        self.correo = self._validar_correo(correo)
        self.idpais = self._validar_idpais(idpais)
        self.dirPostal = self._validar_dirPostal(dirPostal)
=======
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
>>>>>>> 73161b5 (mis cambios)

    def _validarTexto(self, v, m):
        if not v: 
            raise ValueError("Campo obligatorio faltante")
        return str(v).strip()[:m]

<<<<<<< HEAD
    def _validar_noIdentificación(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("El número de identificación es obligatorio")
        valor = str(valor).strip()
        if len(valor) > 50:
            raise ValueError("El número de identificación no puede tener más de 50 caracteres")
        return valor
=======
    def _validarEdad(self, e):
        if not (0 <= int(e) <= 120): 
            raise ValueError("Edad fuera de rango (0-120)")
        return int(e)
>>>>>>> 73161b5 (mis cambios)

    def _validarSexo(self, s):
        s = str(s).upper()
        if s not in ('M', 'F'): 
            raise ValueError("Sexo debe ser M o F")
        return s

<<<<<<< HEAD
    def _validar_apellidos(self, valor):
        if not valor or not valor.strip():
            raise ValueError("Los apellidos no pueden estar vacíos")
        if len(valor) > 100:
            raise ValueError("Los apellidos no pueden tener más de 100 caracteres")
        return valor.strip()

    def _validar_edad(self, valor):
        try:
            edad = int(valor)
        except:
            raise ValueError("La edad debe ser un número entero")
        if edad < 0 or edad > 120:
            raise ValueError("La edad debe estar entre 0 y 120")
        return edad

    def _validar_sexo(self, valor):
        valor = str(valor).strip().upper()
        if valor not in ("M", "F"):
            raise ValueError("El sexo debe ser M o F")
        return valor

    def _validar_telefono(self, valor):
        if not valor or not valor.strip():
            return None
        valor = valor.strip()
        if len(valor) > 20:
            raise ValueError("El teléfono no puede tener más de 20 caracteres")
        if not re.match(r'^[0-9+\-\s]+$', valor):
            raise ValueError("El teléfono contiene caracteres inválidos")
        return valor

    def _validar_correo(self, valor):
        if not valor or not valor.strip():
            return None
        valor = valor.strip()
        if len(valor) > 100:
            raise ValueError("El correo no puede tener más de 100 caracteres")
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', valor):
            raise ValueError("El correo no tiene un formato válido")
        return valor

    def _validar_idpais(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("El país es obligatorio")
        valor = str(valor).strip().upper()
        if len(valor) != 3:
            raise ValueError("El código de país debe tener exactamente 3 caracteres (ej: CUB, USA, MEX)")
        return valor

    def _validar_dirPostal(self, valor):
        if valor is None or not str(valor).strip():
            return None
        valor = str(valor).strip()
        if len(valor) > 150:
            raise ValueError("La dirección postal no puede tener más de 150 caracteres")
        return valor
=======
    def _validarEmail(self, e):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", e): 
            raise ValueError("Email inválido")
        return e
>>>>>>> 73161b5 (mis cambios)
