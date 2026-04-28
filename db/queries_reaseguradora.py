from db.conexionDB import Database


def insertar_reaseguradora(reaseguradora):
    sql = """
        INSERT INTO reaseguradora (idreaseguradora, nombre, idpais, idtiporeaseguro)
        VALUES (%s, %s, %s, %s)
        RETURNING idreaseguradora;
    """
    with Database() as db:
        # Verificar que el país existe
        pais = db.fetch_one("SELECT idpais FROM pais WHERE idpais = %s;", (reaseguradora.id_pais,))
        if not pais:
            raise ValueError(f"El país con ID {reaseguradora.id_pais} no existe")

        # Verificar que el tipo de reaseguro existe
        tipo = db.fetch_one(
            "SELECT idtiporeaseguro FROM tipo_reaseguro WHERE idtiporeaseguro = %s;",
            (reaseguradora.id_tipo_reaseguro,)
        )
        if not tipo:
            raise ValueError(f"El tipo de reaseguro con ID {reaseguradora.id_tipo_reaseguro} no existe")

        params = (
            reaseguradora.id_reaseguradora,
            reaseguradora.nombre,
            reaseguradora.id_pais,
            reaseguradora.id_tipo_reaseguro
        )
        result = db.fetch_one(sql, params)
        return result["idreaseguradora"] if result else None


def listar_reaseguradoras():
    sql = """
        SELECT r.idreaseguradora, r.nombre, p.nombre as pais, tr.nombre as tipo_reaseguro
        FROM reaseguradora r
        JOIN pais p ON r.idpais = p.idpais
        JOIN tipo_reaseguro tr ON r.idtiporeaseguro = tr.idtiporeaseguro
        ORDER BY r.idreaseguradora;
    """
    with Database() as db:
        return db.fetch_all(sql)


def obtener_reaseguradora_por_id(idreaseguradora):
    sql = """
        SELECT r.idreaseguradora, r.nombre, r.idpais, r.idtiporeaseguro, p.nombre as pais_nombre, tr.nombre as tipo_reaseguro_nombre
        FROM reaseguradora r
        JOIN pais p ON r.idpais = p.idpais
        JOIN tipo_reaseguro tr ON r.idtiporeaseguro = tr.idtiporeaseguro
        WHERE r.idreaseguradora = %s;
    """
    with Database() as db:
        return db.fetch_one(sql, (idreaseguradora,))


def actualizar_reaseguradora(reaseguradora):
    sql = """
        UPDATE reaseguradora
        SET nombre = %s, idpais = %s, idtiporeaseguro = %s
        WHERE idreaseguradora = %s;
    """
    with Database() as db:
        db.execute(sql, (
            reaseguradora.nombre,
            reaseguradora.id_pais,
            reaseguradora.id_tipo_reaseguro,
            reaseguradora.id_reaseguradora
        ))


def eliminar_reaseguradora(idreaseguradora):
    with Database() as db:
        # Verificar dependencias
        participaciones = db.fetch_one(
            "SELECT idreaseguradora FROM participacion_reaseguro WHERE idreaseguradora = %s LIMIT 1;",
            (idreaseguradora,)
        )
        if participaciones:
            raise ValueError(f"No se puede eliminar la reaseguradora porque tiene participaciones asociadas")

        db.execute("DELETE FROM reaseguradora WHERE idreaseguradora = %s;", (idreaseguradora,))


def agregar_participacion(idreaseguradora, id_tipo_seguro, porcentaje):
    """Agregar participación de una reaseguradora en un tipo de seguro"""
    with Database() as db:
        # Verificar que la reaseguradora existe
        reaseg = db.fetch_one("SELECT idreaseguradora FROM reaseguradora WHERE idreaseguradora = %s;", (idreaseguradora,))
        if not reaseg:
            raise ValueError(f"La reaseguradora con ID {idreaseguradora} no existe")

        # Verificar que el tipo de seguro existe
        tipo = db.fetch_one("SELECT idtiposeguro FROM tipo_seguro WHERE idtiposeguro = %s;", (id_tipo_seguro,))
        if not tipo:
            raise ValueError(f"El tipo de seguro con ID {id_tipo_seguro} no existe")

        sql = """
            INSERT INTO participacion_reaseguro (idreaseguradora, idtiposeguro, porcentaje)
            VALUES (%s, %s, %s)
            ON CONFLICT (idreaseguradora, idtiposeguro) DO UPDATE SET porcentaje = %s;
        """
        db.execute(sql, (idreaseguradora, id_tipo_seguro, porcentaje, porcentaje))


def listar_participaciones(idreaseguradora):
    sql = """
        SELECT ts.idtiposeguro, ts.nombre as tipo_seguro, pr.porcentaje
        FROM participacion_reaseguro pr
        JOIN tipo_seguro ts ON pr.idtiposeguro = ts.idtiposeguro
        WHERE pr.idreaseguradora = %s;
    """
    with Database() as db:
        return db.fetch_all(sql, (idreaseguradora,))