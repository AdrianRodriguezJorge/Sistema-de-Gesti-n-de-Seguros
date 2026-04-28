from db.conexionDB import Database


def insertar_cliente(cliente):
    """Insertar un nuevo cliente validando que el país existe"""

    with Database() as db:
        # Verificar que el país existe
        pais = db.fetch_one("SELECT idpais FROM pais WHERE idpais = %s;", (cliente.idpais,))
        if not pais:
            raise ValueError(f"El país con ID {cliente.idpais} no existe. Verifica la tabla PAIS.")

        sql = """
            INSERT INTO cliente (noIdentificación, nombre, apellidos, edad, sexo, telefono, correo, idpais, dirPostal)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING idcliente;
        """

        params = (
            cliente.noIdentificación,
            cliente.nombre,
            cliente.apellidos,
            cliente.edad,
            cliente.sexo,
            cliente.telefono,
            cliente.correo,
            cliente.idpais,
            cliente.dirPostal
        )

        result = db.fetch_one(sql, params)
        return result["idcliente"] if result else None


def actualizar_cliente(cliente):
    """Actualizar cliente validando que el país existe"""

    with Database() as db:
        # Verificar que el país existe
        pais = db.fetch_one("SELECT idpais FROM pais WHERE idpais = %s;", (cliente.idpais,))
        if not pais:
            raise ValueError(f"El país con ID {cliente.idpais} no existe. Verifica la tabla PAIS.")

        # Verificar que el cliente existe
        existente = db.fetch_one("SELECT idcliente FROM cliente WHERE idcliente = %s;", (cliente.idcliente,))
        if not existente:
            raise ValueError(f"El cliente con ID {cliente.idcliente} no existe")

        sql = """
            UPDATE cliente
            SET noIdentificación = %s,
                nombre = %s,
                apellidos = %s,
                edad = %s,
                sexo = %s,
                telefono = %s,
                correo = %s,
                idpais = %s,
                dirPostal = %s
            WHERE idcliente = %s;
        """

        params = (
            cliente.noIdentificación,
            cliente.nombre,
            cliente.apellidos,
            cliente.edad,
            cliente.sexo,
            cliente.telefono,
            cliente.correo,
            cliente.idpais,
            cliente.dirPostal,
            cliente.idcliente
        )

        db.execute(sql, params)


def listar_clientes():
    sql = """
        SELECT idcliente, noIdentificación, nombre, apellidos, edad, sexo, idpais, dirPostal, telefono, correo
        FROM cliente
        ORDER BY idcliente;
    """
    with Database() as db:
        return db.fetch_all(sql)


def obtener_cliente_por_id(idcliente):
    sql = """
        SELECT idcliente, noIdentificación, nombre, apellidos, edad, sexo, idpais, dirPostal, telefono, correo
        FROM cliente
        WHERE idcliente = %s;
    """
    with Database() as db:
        return db.fetch_one(sql, (idcliente,))


def eliminar_cliente(idcliente):
    """Eliminar cliente (verificar que no tenga pólizas asociadas)"""
    with Database() as db:
        # Verificar si tiene pólizas
        polizas = db.fetch_one("SELECT idpoliza FROM poliza WHERE idcliente = %s LIMIT 1;", (idcliente,))
        if polizas:
            raise ValueError(f"No se puede eliminar el cliente {idcliente} porque tiene pólizas asociadas")

        db.execute("DELETE FROM cliente WHERE idcliente = %s;", (idcliente,))