from db.conexionDB import Database

def insertar_cliente(cliente):
    sql = """
        INSERT INTO cliente (no_identificacion, nombre, apellidos, edad, sexo, telefono, correo, idpais, dir_postal)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING idcliente;
    """

    params = (
        cliente.no_identificacion,
        cliente.nombre,
        cliente.apellidos,
        cliente.edad,
        cliente.sexo,
        cliente.telefono,
        cliente.correo,
        cliente.idpais,
        cliente.dir_postal
    )

    with Database() as db:
        result = db.fetch_one(sql, params)
        return result["idcliente"] if result else None


def listar_clientes():
    sql = """
        SELECT idcliente, no_identificacion, nombre, apellidos, edad, sexo, idpais, dir_postal, telefono, correo
        FROM cliente
        ORDER BY idcliente;
    """

    with Database() as db:
        return db.fetch_all(sql)


def obtener_cliente_por_id(idcliente):
    sql = """
        SELECT idcliente, no_identificacion, nombre, apellidos, edad, sexo, idpais, dir_postal, telefono, correo
        FROM cliente
        WHERE idcliente = %s;
    """

    with Database() as db:
        return db.fetch_one(sql, (idcliente,))


def actualizar_cliente(cliente):
    sql = """
        UPDATE cliente
        SET no_identificacion = %s,
            nombre = %s,
            apellidos = %s,
            edad = %s,
            sexo = %s,
            telefono = %s,
            correo = %s,
            idpais = %s,
            dir_postal = %s
        WHERE idcliente = %s;
    """

    params = (
        cliente.no_identificacion,
        cliente.nombre,
        cliente.apellidos,
        cliente.edad,
        cliente.sexo,
        cliente.telefono,
        cliente.correo,
        cliente.idpais,
        cliente.dir_postal,
        cliente.idcliente
    )

    with Database() as db:
        db.execute(sql, params)


def eliminar_cliente(idcliente):
    sql = "DELETE FROM cliente WHERE idcliente = %s;"

    with Database() as db:
        db.execute(sql, (idcliente,))
