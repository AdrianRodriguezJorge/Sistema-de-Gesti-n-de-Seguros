import re

class Cliente:
    def __init__(self, nombre, apellidos, no_identificacion, edad, sexo, telefono, correo, idpais, dir_postal=None, idcliente=None):
        self.idcliente = self._validar_idcliente(idcliente)
        self.no_identificacion = self._validar_no_identificacion(no_identificacion)
        self.nombre = self._validar_nombre(nombre)
        self.apellidos = self._validar_apellidos(apellidos)
        self.edad = self._validar_edad(edad)
        self.sexo = self._validar_sexo(sexo)
        self.telefono = self._validar_telefono(telefono)
        self.correo = self._validar_correo(correo)
        self.idpais = self._validar_idpais(idpais)
        self.dir_postal = self._validar_dir_postal(dir_postal)

    def _validar_idcliente(self, valor):
        if valor is None:
            return None
        try:
            valor = int(valor)
        except:
            raise ValueError("idCliente debe ser un entero")
        if valor <= 0:
            raise ValueError("idCliente debe ser positivo")
        return valor

    def _validar_no_identificacion(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("El número de identificación es obligatorio")
        valor = str(valor).strip()
        if len(valor) > 50:
            raise ValueError("El número de identificación no puede tener más de 50 caracteres")
        return valor

    def _validar_nombre(self, valor):
        if not valor or not valor.strip():
            raise ValueError("El nombre no puede estar vacío")
        if len(valor) > 50:
            raise ValueError("El nombre no puede tener más de 50 caracteres")
        return valor.strip()

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
        try:
            valor = int(valor)
        except:
            raise ValueError("idPais debe ser un entero")
        if valor <= 0:
            raise ValueError("idPais debe ser positivo")
        return valor

    def _validar_dir_postal(self, valor):
        if valor is None or not str(valor).strip():
            return None
        valor = str(valor).strip()
        if len(valor) > 150:
            raise ValueError("La dirección postal no puede tener más de 150 caracteres")
        return valor
