from db.conexionDB import Database


def insertar_reclamacion(reclamacion):
    """Insertar una nueva reclamación"""

    with Database() as db:
        # Verificar que la póliza existe
        poliza = db.fetch_one("SELECT idpoliza FROM poliza WHERE idpoliza = %s;", (reclamacion.id_poliza,))
        if not poliza:
            raise ValueError(f"La póliza con ID {reclamacion.id_poliza} no existe")

        # Verificar que el tipo de siniestro existe
        tipo = db.fetch_one(
            "SELECT idtiposiniestro FROM tipo_siniestro WHERE idtiposiniestro = %s;",
            (reclamacion.id_tipo_siniestro,)
        )
        if not tipo:
            raise ValueError(f"El tipo de siniestro con ID {reclamacion.id_tipo_siniestro} no existe")

        # Verificar que el estado de reclamación existe
        estado = db.fetch_one(
            "SELECT idestadoreclamacion FROM estado_reclamacion WHERE idestadoreclamacion = %s;",
            (reclamacion.id_estado_reclamacion,)
        )
        if not estado:
            raise ValueError(f"El estado de reclamación con ID {reclamacion.id_estado_reclamacion} no existe")

        # Validar que indemnizado no exceda reclamado
        if reclamacion.monto_indemnizado > reclamacion.monto_reclamado:
            raise ValueError("El monto indemnizado no puede ser mayor que el monto reclamado")

        sql = """
            INSERT INTO reclamacion (idreclamacion, idtiposiniestro, fechasiniestro, montoreclamado, idestadoreclamacion, montoindemnizado, idpoliza)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING idreclamacion;
        """
        params = (
            reclamacion.id_reclamacion,
            reclamacion.id_tipo_siniestro,
            reclamacion.fecha_siniestro,
            reclamacion.monto_reclamado,
            reclamacion.id_estado_reclamacion,
            reclamacion.monto_indemnizado,
            reclamacion.id_poliza
        )
        result = db.fetch_one(sql, params)
        return result["idreclamacion"] if result else None


def listar_reclamaciones():
    sql = """
        SELECT r.idreclamacion, c.nombre || ' ' || c.apellidos as cliente, r.idpoliza, ts.nombre as tipo_seguro, tsini.nombre as tipo_siniestro, r.fechasiniestro, r.montoreclamado, r.montoindemnizado, er.nombre as estado
        FROM reclamacion r
        JOIN poliza p ON r.idpoliza = p.idpoliza
        JOIN cliente c ON p.idcliente = c.idcliente
        JOIN tipo_seguro ts ON p.idtiposeguro = ts.idtiposeguro
        JOIN tipo_siniestro tsini ON r.idtiposiniestro = tsini.idtiposiniestro
        JOIN estado_reclamacion er ON r.idestadoreclamacion = er.idestadoreclamacion
        ORDER BY r.idreclamacion;
    """
    with Database() as db:
        return db.fetch_all(sql)


def obtener_reclamacion_por_id(idreclamacion):
    sql = """
        SELECT r.*, c.nombre || ' ' || c.apellidos as cliente_nombre, ts.nombre as tipo_seguro
        FROM reclamacion r
        JOIN poliza p ON r.idpoliza = p.idpoliza
        JOIN cliente c ON p.idcliente = c.idcliente
        JOIN tipo_seguro ts ON p.idtiposeguro = ts.idtiposeguro
        WHERE r.idreclamacion = %s;
    """
    with Database() as db:
        return db.fetch_one(sql, (idreclamacion,))


def actualizar_reclamacion(reclamacion):
    """Actualizar datos de una reclamación existente"""

    with Database() as db:
        # Verificar que existe
        existente = db.fetch_one(
            "SELECT idreclamacion FROM reclamacion WHERE idreclamacion = %s;",
            (reclamacion.id_reclamacion,)
        )
        if not existente:
            raise ValueError(f"La reclamación con ID {reclamacion.id_reclamacion} no existe")

        # Verificar referencias
        if not db.fetch_one("SELECT idpoliza FROM poliza WHERE idpoliza = %s;", (reclamacion.id_poliza,)):
            raise ValueError(f"La póliza con ID {reclamacion.id_poliza} no existe")
        if not db.fetch_one("SELECT idtiposiniestro FROM tipo_siniestro WHERE idtiposiniestro = %s;", (reclamacion.id_tipo_siniestro,)):
            raise ValueError(f"El tipo de siniestro con ID {reclamacion.id_tipo_siniestro} no existe")

        if reclamacion.monto_indemnizado > reclamacion.monto_reclamado:
            raise ValueError("El monto indemnizado no puede ser mayor que el monto reclamado")

        sql = """
            UPDATE reclamacion
            SET idtiposiniestro = %s,
                fechasiniestro = %s,
                montoreclamado = %s,
                montoindemnizado = %s,
                idpoliza = %s
            WHERE idreclamacion = %s;
        """
        params = (
            reclamacion.id_tipo_siniestro,
            reclamacion.fecha_siniestro,
            reclamacion.monto_reclamado,
            reclamacion.monto_indemnizado,
            reclamacion.id_poliza,
            reclamacion.id_reclamacion
        )
        db.execute(sql, params)


def eliminar_reclamacion(idreclamacion):
    """Eliminar una reclamación (verificar que no tenga registro de rechazo)"""

    with Database() as db:
        # Verificar si tiene registro de rechazo
        rechazo = db.fetch_one(
            "SELECT idreclamacionrechazada FROM reclamacion_rechazada WHERE idreclamacion = %s LIMIT 1;",
            (idreclamacion,)
        )
        if rechazo:
            raise ValueError(f"No se puede eliminar la reclamación {idreclamacion} porque tiene un registro de rechazo asociado")

        db.execute("DELETE FROM reclamacion WHERE idreclamacion = %s;", (idreclamacion,))

def rechazar_reclamacion(idreclamacion, motivo):
    """
    Rechazar una reclamación.
    El estado de rechazo debe ser Rechazada.
    Se añade registro en reclamacion_rechazada.
    """
    with Database() as db:
        # 1. Verificar que la reclamación existe
        reclamacion = db.fetch_one(
            "SELECT idreclamacion, idestadoreclamacion FROM reclamacion WHERE idreclamacion = %s;",
            (idreclamacion,)
        )
        if not reclamacion:
            raise ValueError(f"La reclamación con ID {idreclamacion} no existe")

        # 2. Obtener el ID del estado "Rechazada"
        estado_rechazada = db.fetch_one(
            "SELECT idestadoreclamacion FROM estado_reclamacion WHERE lower(nombre) = 'rechazada';"
        )
        if not estado_rechazada:
            raise ValueError("No existe el estado 'Rechazada' en la tabla estado_reclamacion")

        id_estado_rechazada = estado_rechazada["idestadoreclamacion"]

        # 3. Validar motivo
        if not motivo or not motivo.strip():
            raise ValueError("Debe proporcionar un motivo para rechazar la reclamación")

        # 4. Verificar si ya estaba rechazada
        if reclamacion["idestadoreclamacion"] == id_estado_rechazada:
            raise ValueError(f"La reclamación {idreclamacion} ya está rechazada")

        # 5. Verificar si ya existe un registro de rechazo
        existe_rechazo = db.fetch_one(
            "SELECT idreclamacionrechazada FROM reclamacion_rechazada WHERE idreclamacion = %s;",
            (idreclamacion,)
        )
        if existe_rechazo:
            raise ValueError(f"La reclamación {idreclamacion} ya tiene un registro de rechazo")

        # 6. Actualizar el estado de la reclamación
        db.execute(
            "UPDATE reclamacion SET idestadoreclamacion = %s WHERE idreclamacion = %s;",
            (id_estado_rechazada, idreclamacion)
        )

        # 7. Insertar en reclamacion_rechazada
        id_rechazo = f"RC{idreclamacion}"
        db.execute(
            """
            INSERT INTO reclamacion_rechazada (idreclamacionrechazada, motivo, idreclamacion)
            VALUES (%s, %s, %s);
            """,
            (id_rechazo, motivo.strip(), idreclamacion)
        )

        return True


def aprobar_reclamacion(idreclamacion, monto_indemnizado):
    """
    Aprobar una reclamación y establecer el monto indemnizado.
    El estado de aprobada debe ser 2 (Aprobada).
    """
    with Database() as db:
        # 1. Verificar que la reclamación existe
        reclamacion = db.fetch_one(
            "SELECT idreclamacion, idestadoreclamacion, montoreclamado FROM reclamacion WHERE idreclamacion = %s;",
            (idreclamacion,)
        )
        if not reclamacion:
            raise ValueError(f"La reclamación con ID {idreclamacion} no existe")

        # 2. Validar monto indemnizado
        if monto_indemnizado < 0:
            raise ValueError("El monto indemnizado no puede ser negativo")
        if monto_indemnizado > reclamacion["montoreclamado"]:
            raise ValueError(f"El monto indemnizado no puede ser mayor que el monto reclamado ({reclamacion['montoreclamado']})")

        # 3. Obtener ID del estado "Aprobada"
        estado_aprobada = db.fetch_one(
            "SELECT idestadoreclamacion FROM estado_reclamacion WHERE lower(nombre) = 'aprobada';"
        )
        if not estado_aprobada:
            raise ValueError("No existe el estado 'Aprobada' en la tabla estado_reclamacion")

        id_estado_aprobada = estado_aprobada["idestadoreclamacion"]

        # 4. Verificar si ya estaba aprobada o rechazada
        if reclamacion["idestadoreclamacion"] == id_estado_aprobada:
            raise ValueError(f"La reclamación {idreclamacion} ya está aprobada")

        estado_rechazada = db.fetch_one(
            "SELECT idestadoreclamacion FROM estado_reclamacion WHERE lower(nombre) = 'rechazada';"
        )
        if estado_rechazada and reclamacion["idestadoreclamacion"] == estado_rechazada["idestadoreclamacion"]:
            raise ValueError(f"La reclamación {idreclamacion} está rechazada, no se puede aprobar")

        # 5. Actualizar estado y monto indemnizado
        db.execute(
            "UPDATE reclamacion SET idestadoreclamacion = %s, montoindemnizado = %s WHERE idreclamacion = %s;",
            (id_estado_aprobada, monto_indemnizado, idreclamacion)
        )

        return True