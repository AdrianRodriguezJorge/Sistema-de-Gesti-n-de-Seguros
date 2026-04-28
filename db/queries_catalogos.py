from db.conexionDB import Database


def insertar_pais(pais):
    # Generar ID automáticamente (primeras 3 letras del nombre en mayúsculas)
    id_generado = pais.nombre[:3].upper()
    
    sql = "INSERT INTO pais (idpais, nombre) VALUES (%s, %s) RETURNING idpais;"
    with Database() as db:
        result = db.fetch_one(sql, (id_generado, pais.nombre))
        return result["idpais"] if result else None


def listar_paises():
    sql = "SELECT idpais, nombre FROM pais ORDER BY nombre;"
    with Database() as db:
        return db.fetch_all(sql)


def obtener_pais_por_id(idpais):
    sql = "SELECT idpais, nombre FROM pais WHERE idpais = %s;"
    with Database() as db:
        return db.fetch_one(sql, (idpais,))


def actualizar_pais(pais):
    sql = "UPDATE pais SET nombre = %s WHERE idpais = %s;"
    with Database() as db:
        db.execute(sql, (pais.nombre, pais.id_))


def eliminar_pais(idpais):
    sql = "DELETE FROM pais WHERE idpais = %s;"
    with Database() as db:
        db.execute(sql, (idpais,))


def insertar_tipo_seguro(tipo):
    with Database() as db:
        # Obtener el próximo ID disponible
        last_id = db.fetch_one("SELECT COALESCE(MAX(idtiposeguro), 0) + 1 as next_id FROM tipo_seguro;")
        id_generado = last_id["next_id"] if last_id else 1
        
        sql = "INSERT INTO tipo_seguro (idtiposeguro, nombre) VALUES (%s, %s) RETURNING idtiposeguro;"
        result = db.fetch_one(sql, (id_generado, tipo.nombre))
        return result["idtiposeguro"] if result else None


def listar_tipos_seguro():
    sql = "SELECT idtiposeguro, nombre FROM tipo_seguro ORDER BY nombre;"
    with Database() as db:
        return db.fetch_all(sql)


def obtener_tipo_seguro_por_id(idtiposeguro):
    sql = "SELECT idtiposeguro, nombre FROM tipo_seguro WHERE idtiposeguro = %s;"
    with Database() as db:
        return db.fetch_one(sql, (idtiposeguro,))


def actualizar_tipo_seguro(tipo):
    sql = "UPDATE tipo_seguro SET nombre = %s WHERE idtiposeguro = %s;"
    with Database() as db:
        db.execute(sql, (tipo.nombre, tipo.id_))


def eliminar_tipo_seguro(idtiposeguro):
    sql = "DELETE FROM tipo_seguro WHERE idtiposeguro = %s;"
    with Database() as db:
        db.execute(sql, (idtiposeguro,))


def insertar_estado_poliza(estado):
    with Database() as db:
        last_id = db.fetch_one("SELECT COALESCE(MAX(idestadopoliza), 0) + 1 as next_id FROM estado_poliza;")
        id_generado = last_id["next_id"] if last_id else 1
        
        sql = "INSERT INTO estado_poliza (idestadopoliza, nombre) VALUES (%s, %s) RETURNING idestadopoliza;"
        result = db.fetch_one(sql, (id_generado, estado.nombre))
        return result["idestadopoliza"] if result else None


def listar_estados_poliza():
    sql = "SELECT idestadopoliza, nombre FROM estado_poliza ORDER BY nombre;"
    with Database() as db:
        return db.fetch_all(sql)


def obtener_estado_poliza_por_id(idestadopoliza):
    sql = "SELECT idestadopoliza, nombre FROM estado_poliza WHERE idestadopoliza = %s;"
    with Database() as db:
        return db.fetch_one(sql, (idestadopoliza,))


def actualizar_estado_poliza(estado):
    sql = "UPDATE estado_poliza SET nombre = %s WHERE idestadopoliza = %s;"
    with Database() as db:
        db.execute(sql, (estado.nombre, estado.id_))


def eliminar_estado_poliza(idestadopoliza):
    sql = "DELETE FROM estado_poliza WHERE idestadopoliza = %s;"
    with Database() as db:
        db.execute(sql, (idestadopoliza,))


def insertar_tipo_siniestro(tipo):
    with Database() as db:
        last_id = db.fetch_one("SELECT COALESCE(MAX(idtiposiniestro), 0) + 1 as next_id FROM tipo_siniestro;")
        id_generado = last_id["next_id"] if last_id else 1
        
        sql = "INSERT INTO tipo_siniestro (idtiposiniestro, nombre) VALUES (%s, %s) RETURNING idtiposiniestro;"
        result = db.fetch_one(sql, (id_generado, tipo.nombre))
        return result["idtiposiniestro"] if result else None


def listar_tipos_siniestro():
    sql = "SELECT idtiposiniestro, nombre FROM tipo_siniestro ORDER BY nombre;"
    with Database() as db:
        return db.fetch_all(sql)


def obtener_tipo_siniestro_por_id(idtiposiniestro):
    sql = "SELECT idtiposiniestro, nombre FROM tipo_siniestro WHERE idtiposiniestro = %s;"
    with Database() as db:
        return db.fetch_one(sql, (idtiposiniestro,))


def actualizar_tipo_siniestro(tipo):
    sql = "UPDATE tipo_siniestro SET nombre = %s WHERE idtiposiniestro = %s;"
    with Database() as db:
        db.execute(sql, (tipo.nombre, tipo.id_))


def eliminar_tipo_siniestro(idtiposiniestro):
    sql = "DELETE FROM tipo_siniestro WHERE idtiposiniestro = %s;"
    with Database() as db:
        db.execute(sql, (idtiposiniestro,))


def insertar_estado_reclamacion(estado):
    with Database() as db:
        last_id = db.fetch_one("SELECT COALESCE(MAX(idestadoreclamacion), 0) + 1 as next_id FROM estado_reclamacion;")
        id_generado = last_id["next_id"] if last_id else 1
        
        sql = "INSERT INTO estado_reclamacion (idestadoreclamacion, nombre) VALUES (%s, %s) RETURNING idestadoreclamacion;"
        result = db.fetch_one(sql, (id_generado, estado.nombre))
        return result["idestadoreclamacion"] if result else None


def listar_estados_reclamacion():
    sql = "SELECT idestadoreclamacion, nombre FROM estado_reclamacion ORDER BY nombre;"
    with Database() as db:
        return db.fetch_all(sql)


def obtener_estado_reclamacion_por_id(idestadoreclamacion):
    sql = "SELECT idestadoreclamacion, nombre FROM estado_reclamacion WHERE idestadoreclamacion = %s;"
    with Database() as db:
        return db.fetch_one(sql, (idestadoreclamacion,))


def actualizar_estado_reclamacion(estado):
    sql = "UPDATE estado_reclamacion SET nombre = %s WHERE idestadoreclamacion = %s;"
    with Database() as db:
        db.execute(sql, (estado.nombre, estado.id_))


def eliminar_estado_reclamacion(idestadoreclamacion):
    sql = "DELETE FROM estado_reclamacion WHERE idestadoreclamacion = %s;"
    with Database() as db:
        db.execute(sql, (idestadoreclamacion,))


def insertar_tipo_reaseguro(tipo):
    with Database() as db:
        last_id = db.fetch_one("SELECT COALESCE(MAX(idtiporeaseguro), 0) + 1 as next_id FROM tipo_reaseguro;")
        id_generado = last_id["next_id"] if last_id else 1
        
        sql = "INSERT INTO tipo_reaseguro (idtiporeaseguro, nombre) VALUES (%s, %s) RETURNING idtiporeaseguro;"
        result = db.fetch_one(sql, (id_generado, tipo.nombre))
        return result["idtiporeaseguro"] if result else None


def listar_tipos_reaseguro():
    sql = "SELECT idtiporeaseguro, nombre FROM tipo_reaseguro ORDER BY nombre;"
    with Database() as db:
        return db.fetch_all(sql)


def obtener_tipo_reaseguro_por_id(idtiporeaseguro):
    sql = "SELECT idtiporeaseguro, nombre FROM tipo_reaseguro WHERE idtiporeaseguro = %s;"
    with Database() as db:
        return db.fetch_one(sql, (idtiporeaseguro,))


def actualizar_tipo_reaseguro(tipo):
    sql = "UPDATE tipo_reaseguro SET nombre = %s WHERE idtiporeaseguro = %s;"
    with Database() as db:
        db.execute(sql, (tipo.nombre, tipo.id_))


def eliminar_tipo_reaseguro(idtiporeaseguro):
    sql = "DELETE FROM tipo_reaseguro WHERE idtiporeaseguro = %s;"
    with Database() as db:
        db.execute(sql, (idtiporeaseguro,))