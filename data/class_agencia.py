class Agencia:
    """Solo una fila (id_agencia = 1)"""

    def __init__(self, nombre, direccion, telefono, email, director_general, jefe_seguros, jefe_reclamaciones, id_agencia=1):
        self.id_agencia = self._validar_id_agencia(id_agencia)
        self.nombre = self._validar_nombre(nombre)
        self.direccion = self._validar_direccion(direccion)
        self.telefono = self._validar_telefono(telefono)
        self.email = self._validar_email(email)
        self.director_general = self._validar_director_general(director_general)
        self.jefe_seguros = self._validar_jefe_seguros(jefe_seguros)
        self.jefe_reclamaciones = self._validar_jefe_reclamaciones(jefe_reclamaciones)

    def _validar_id_agencia(self, valor):
        if valor != 1:
            raise ValueError("id_agencia debe ser 1 (solo existe una agencia)")
        return valor

    def _validar_nombre(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("El nombre no puede estar vacío")
        return str(valor).strip()

    def _validar_direccion(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("La dirección no puede estar vacía")
        return str(valor).strip()

    def _validar_telefono(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("El teléfono no puede estar vacío")
        return str(valor).strip()

    def _validar_email(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("El email no puede estar vacío")
        return str(valor).strip()

    def _validar_director_general(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("El director general no puede estar vacío")
        return str(valor).strip()

    def _validar_jefe_seguros(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("El jefe de seguros no puede estar vacío")
        return str(valor).strip()

    def _validar_jefe_reclamaciones(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("El jefe de reclamaciones no puede estar vacío")
        return str(valor).strip()