from db.conexionDB import Database


def insertar_cobertura(cobertura):
    """Insertar una nueva cobertura en el catálogo"""
    with Database() as db:
        # Obtener el próximo ID disponible
        last_id = db.fetch_one("SELECT COALESCE(MAX(idcobertura), 0) + 1 as next_id FROM cobertura;")
        id_generado = last_id["next_id"] if last_id else 1
        
        sql = "INSERT INTO cobertura (idcobertura, descripcion) VALUES (%s, %s) RETURNING idcobertura;"
        result = db.fetch_one(sql, (id_generado, cobertura.descripcion))
        return result["idcobertura"] if result else None


def listar_coberturas():
    sql = "SELECT idcobertura, descripcion FROM cobertura ORDER BY idcobertura;"
    with Database() as db:
        return db.fetch_all(sql)


def obtener_cobertura_por_id(idcobertura):
    sql = "SELECT idcobertura, descripcion FROM cobertura WHERE idcobertura = %s;"
    with Database() as db:
        return db.fetch_one(sql, (idcobertura,))


def actualizar_cobertura(cobertura):
    sql = "UPDATE cobertura SET descripcion = %s WHERE idcobertura = %s;"
    with Database() as db:
        db.execute(sql, (cobertura.descripcion, cobertura.id_cobertura))


def eliminar_cobertura(idcobertura):
    """Eliminar cobertura (verificar que no esté en uso)"""
    with Database() as db:
        # Verificar si está siendo usada
        en_uso = db.fetch_one(
            "SELECT idpoliza FROM poliza_cobertura WHERE idcobertura = %s LIMIT 1;",
            (idcobertura,)
        )
        if en_uso:
            raise ValueError(f"No se puede eliminar la cobertura {idcobertura} porque está asociada a una o más pólizas")
        db.execute("DELETE FROM cobertura WHERE idcobertura = %s;", (idcobertura,))


def agregar_cobertura_a_poliza(idpoliza, idcobertura, monto):
    """Asignar una cobertura a una póliza (relación N:M)"""
    with Database() as db:
        # Verificar que la póliza existe
        poliza = db.fetch_one("SELECT idpoliza FROM poliza WHERE idpoliza = %s;", (idpoliza,))
        if not poliza:
            raise ValueError(f"La póliza con ID {idpoliza} no existe")

        # Verificar que la cobertura existe
        cobertura = db.fetch_one("SELECT idcobertura FROM cobertura WHERE idcobertura = %s;", (idcobertura,))
        if not cobertura:
            raise ValueError(f"La cobertura con ID {idcobertura} no existe")

        # Verificar que no esté ya asignada
        existe = db.fetch_one(
            "SELECT idpoliza FROM poliza_cobertura WHERE idpoliza = %s AND idcobertura = %s;",
            (idpoliza, idcobertura)
        )
        if existe:
            raise ValueError(f"La cobertura ya está asignada a esta póliza")

        sql = "INSERT INTO poliza_cobertura (idpoliza, idcobertura, monto) VALUES (%s, %s, %s);"
        db.execute(sql, (idpoliza, idcobertura, monto))


def listar_coberturas_de_poliza(idpoliza):
    """Obtener todas las coberturas de una póliza"""
    sql = """
        SELECT c.idcobertura, c.descripcion, pc.monto
        FROM poliza_cobertura pc
        JOIN cobertura c ON pc.idcobertura = c.idcobertura
        WHERE pc.idpoliza = %s;
    """
    with Database() as db:
        return db.fetch_all(sql, (idpoliza,))


def eliminar_cobertura_de_poliza(idpoliza, idcobertura):
    """Quitar una cobertura de una póliza"""
    sql = "DELETE FROM poliza_cobertura WHERE idpoliza = %s AND idcobertura = %s;"
    with Database() as db:
        db.execute(sql, (idpoliza, idcobertura))