from db.conexionDB import Database


def obtener_agencia():
    """Obtener los datos de la agencia (solo una fila, id=1)"""
    sql = """
        SELECT idagencia, nombre, direccion, telefono, email, directorgeneral, jefeseguros, jefereclamaciones
        FROM agencia
        WHERE idagencia = 1;
    """
    with Database() as db:
        return db.fetch_one(sql)


def actualizar_agencia(agencia):
    """Actualizar los datos de la agencia (solo una fila)"""
    with Database() as db:
        # Verificar que existe
        existente = db.fetch_one("SELECT idagencia FROM agencia WHERE idagencia = 1;")
        if not existente:
            # Si no existe, insertar
            sql = """
                INSERT INTO agencia (idagencia, nombre, direccion, telefono, email, directorgeneral, jefeseguros, jefereclamaciones)
                VALUES (1, %s, %s, %s, %s, %s, %s, %s);
            """
            params = (
                agencia.nombre,
                agencia.direccion,
                agencia.telefono,
                agencia.email,
                agencia.director_general,
                agencia.jefe_seguros,
                agencia.jefe_reclamaciones
            )
            db.execute(sql, params)
        else:
            # Actualizar
            sql = """
                UPDATE agencia
                SET nombre = %s, direccion = %s, telefono = %s, email = %s,
                    directorgeneral = %s, jefeseguros = %s, jefereclamaciones = %s
                WHERE idagencia = 1;
            """
            params = (
                agencia.nombre,
                agencia.direccion,
                agencia.telefono,
                agencia.email,
                agencia.director_general,
                agencia.jefe_seguros,
                agencia.jefe_reclamaciones
            )
            db.execute(sql, params)