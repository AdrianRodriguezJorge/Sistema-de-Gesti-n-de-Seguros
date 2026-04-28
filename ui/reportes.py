import streamlit as st
import pandas as pd
from datetime import date, datetime

from db.conexionDB import Database
from db.queries_catalogos import listar_paises, listar_tipos_seguro, listar_estados_reclamacion
from db.queries_cliente import listar_clientes, obtener_cliente_por_id
from db.queries_poliza import listar_polizas, obtener_poliza_por_id
from db.queries_reaseguradora import obtener_reaseguradora_por_id
from db.queries_reclamacion import listar_reclamaciones
from db.queries_pago import total_pagado_por_cliente
from db.queries_agencia import obtener_agencia


def pagina_reportes():
    st.title("📊 Reportes")
    st.divider()

    reporte_seleccionado = st.selectbox(
        "Seleccione el reporte que desea generar:",
        options=[
            "Listado de Clientes",
            "Listado de Pólizas",
            "Listado de Reclamaciones",
            "Listado de Reaseguradoras",
            "Listado de Pólizas Vencidas",
            "Listado de Clientes con Pólizas Canceladas",
            "Resumen de Pólizas por Tipo de Seguro",
            "Resumen de Reclamaciones por Estado",
            "Listado de Ingresos Mensuales",
            "Reporte de Clientes con Reclamaciones Aprobadas",
            "Reporte de Clientes con Reclamaciones Rechazadas",
            "Ficha de la Agencia de Seguros",
            "Ficha de un Cliente Determinado",
            "Ficha de una Reaseguradora Asociada",
            "Reporte de Pólizas Emitidas en un Período",
            "Reporte de Estado de las Reclamaciones",
            "Reporte de Ingresos Mensuales por Concepto de Primas"
        ],
        key="select_reporte"
    )

    st.divider()

    # =====================================================
    # REPORTE 1: LISTADO DE CLIENTES
    # =====================================================
    if reporte_seleccionado == "Listado de Clientes":
        st.subheader("📋 Listado de Clientes")
        st.caption(f"Fecha del reporte: {date.today().strftime('%d/%m/%Y')}")

        paises = listar_paises()

        for pais in paises:
            st.markdown(f"### 🌍 {pais['nombre']}")
            with Database() as db:
                clientes = db.fetch_all(
                    """
                    SELECT c.idcliente, c.nombre, c.apellidos,
                           COUNT(CASE WHEN ep.nombre = 'Activa' THEN 1 END) as polizas_activas,
                           COALESCE(SUM(p.montopagado), 0) as total_pagado
                    FROM cliente c
                    LEFT JOIN poliza po ON c.idcliente = po.idcliente
                    LEFT JOIN estado_poliza ep ON po.idestadopoliza = ep.idestadopoliza
                    LEFT JOIN pago p ON po.idpoliza = p.idpoliza
                    WHERE c.idpais = %s
                    GROUP BY c.idcliente, c.nombre, c.apellidos
                    ORDER BY c.apellidos;
                    """,
                    (pais["idpais"],)
                )

            if clientes:
                df = pd.DataFrame(clientes)
                df_display = df.rename(columns={
                    "idcliente": "ID",
                    "nombre": "Nombre",
                    "apellidos": "Apellidos",
                    "polizas_activas": "Pólizas activas",
                    "total_pagado": "Total pagado ($)"
                })
                st.dataframe(df_display, use_container_width=True)
            else:
                st.info(f"No hay clientes registrados en {pais['nombre']}")

    # =====================================================
    # REPORTE 2: LISTADO DE PÓLIZAS
    # =====================================================
    elif reporte_seleccionado == "Listado de Pólizas":
        st.subheader("📋 Listado de Pólizas")
        st.caption(f"Fecha del reporte: {date.today().strftime('%d/%m/%Y')}")

        tipos_seguro = listar_tipos_seguro()

        for tipo in tipos_seguro:
            st.markdown(f"### 🛡️ {tipo['nombre']}")
            with Database() as db:
                polizas = db.fetch_all(
                    """
                    SELECT p.idpoliza, c.nombre || ' ' || c.apellidos as cliente,
                           p.fechainicio, p.fechafin, p.primamensual,
                           p.montoasegurado, ep.nombre as estado
                    FROM poliza p
                    JOIN cliente c ON p.idcliente = c.idcliente
                    JOIN estado_poliza ep ON p.idestadopoliza = ep.idestadopoliza
                    WHERE p.idtiposeguro = %s
                    ORDER BY p.idpoliza;
                    """,
                    (tipo["idtiposeguro"],)
                )

            if polizas:
                df = pd.DataFrame(polizas)
                df_display = df.rename(columns={
                    "idpoliza": "Número",
                    "cliente": "Cliente",
                    "fechainicio": "Fecha inicio",
                    "fechafin": "Fecha fin",
                    "primamensual": "Prima mensual",
                    "montoasegurado": "Monto asegurado",
                    "estado": "Estado"
                })
                st.dataframe(df_display, use_container_width=True)
            else:
                st.info(f"No hay pólizas registradas para {tipo['nombre']}")

    # =====================================================
    # REPORTE 3: LISTADO DE RECLAMACIONES
    # =====================================================
    elif reporte_seleccionado == "Listado de Reclamaciones":
        st.subheader("📋 Listado de Reclamaciones")

        reclamaciones = listar_reclamaciones()

        if reclamaciones:
            df = pd.DataFrame(reclamaciones)
            df_display = df.rename(columns={
                "cliente": "Cliente",
                "idpoliza": "Número de póliza",
                "tipo_seguro": "Tipo de seguro",
                "idreclamacion": "Número de reclamación",
                "tipo_siniestro": "Tipo de siniestro",
                "fechasiniestro": "Fecha del siniestro",
                "montoreclamado": "Monto reclamado",
                "montoindemnizado": "Monto indemnizado",
                "estado": "Estado"
            })
            st.dataframe(df_display[[
                "Cliente", "Número de póliza", "Tipo de seguro", "Número de reclamación",
                "Tipo de siniestro", "Fecha del siniestro", "Monto reclamado", "Monto indemnizado", "Estado"
            ]], use_container_width=True)
        else:
            st.info("No hay reclamaciones registradas.")

    # =====================================================
    # REPORTE 4: LISTADO DE REASEGURADORAS
    # =====================================================
    elif reporte_seleccionado == "Listado de Reaseguradoras":
        st.subheader("📋 Listado de Reaseguradoras")
        st.caption(f"Fecha del reporte: {date.today().strftime('%d/%m/%Y')}")

        with Database() as db:
            reaseguradoras = db.fetch_all(
                """
                SELECT r.idreaseguradora, r.nombre, p.nombre as pais,
                       tr.nombre as tipo_reaseguro
                FROM reaseguradora r
                JOIN pais p ON r.idpais = p.idpais
                JOIN tipo_reaseguro tr ON r.idtiporeaseguro = tr.idtiporeaseguro
                ORDER BY r.nombre;
                """
            )

        if reaseguradoras:
            for rea in reaseguradoras:
                with st.expander(f"🏢 {rea['nombre']} ({rea['idreaseguradora']})"):
                    st.markdown(f"**País de origen:** {rea['pais']}")
                    st.markdown(f"**Tipo de reaseguro:** {rea['tipo_reaseguro']}")

                    # Obtener participaciones
                    with Database() as db:
                        participaciones = db.fetch_all(
                            """
                            SELECT ts.nombre as tipo_seguro, pr.porcentaje
                            FROM participacion_reaseguro pr
                            JOIN tipo_seguro ts ON pr.idtiposeguro = ts.idtiposeguro
                            WHERE pr.idreaseguradora = %s;
                            """,
                            (rea["idreaseguradora"],)
                        )

                    if participaciones:
                        st.markdown("**Participaciones:**")
                        df = pd.DataFrame(participaciones)
                        df_display = df.rename(columns={
                            "tipo_seguro": "Tipo de seguro",
                            "porcentaje": "Porcentaje (%)"
                        })
                        st.dataframe(df_display, use_container_width=True)
        else:
            st.info("No hay reaseguradoras registradas.")

    # =====================================================
    # REPORTE 5: LISTADO DE PÓLIZAS VENCIDAS
    # =====================================================
    elif reporte_seleccionado == "Listado de Pólizas Vencidas":
        st.subheader("📋 Listado de Pólizas Vencidas")
        st.caption(f"Fecha del reporte: {date.today().strftime('%d/%m/%Y')}")

        with Database() as db:
            polizas = db.fetch_all(
                """
                SELECT p.idpoliza, c.nombre || ' ' || c.apellidos as cliente,
                       ts.nombre as tipo_seguro,
                       p.fechainicio, p.fechafin, p.montoasegurado
                FROM poliza p
                JOIN cliente c ON p.idcliente = c.idcliente
                JOIN tipo_seguro ts ON p.idtiposeguro = ts.idtiposeguro
                WHERE p.fechafin < CURRENT_DATE
                ORDER BY p.fechafin;
                """
            )

        if polizas:
            df = pd.DataFrame(polizas)
            df_display = df.rename(columns={
                "idpoliza": "Número de póliza",
                "cliente": "Cliente",
                "tipo_seguro": "Tipo de seguro",
                "fechainicio": "Fecha inicio",
                "fechafin": "Fecha fin",
                "montoasegurado": "Monto asegurado"
            })
            st.dataframe(df_display, use_container_width=True)
        else:
            st.success("✅ No hay pólizas vencidas.")

    # =====================================================
    # REPORTE 6: CLIENTES CON PÓLIZAS CANCELADAS
    # =====================================================
    elif reporte_seleccionado == "Listado de Clientes con Pólizas Canceladas":
        st.subheader("📋 Clientes con Pólizas Canceladas")
        st.caption(f"Fecha del reporte: {date.today().strftime('%d/%m/%Y')}")

        with Database() as db:
            clientes = db.fetch_all(
                """
                SELECT c.idcliente, c.nombre, c.apellidos,
                       COUNT(p.idpoliza) as cantidad_canceladas,
                       STRING_AGG(pc.motivo, '; ') as motivos
                FROM cliente c
                JOIN poliza p ON c.idcliente = p.idcliente
                JOIN poliza_cancelada pc ON p.idpoliza = pc.idpoliza
                GROUP BY c.idcliente, c.nombre, c.apellidos
                ORDER BY c.apellidos;
                """
            )

        if clientes:
            df = pd.DataFrame(clientes)
            df_display = df.rename(columns={
                "idcliente": "ID",
                "nombre": "Nombre",
                "apellidos": "Apellidos",
                "cantidad_canceladas": "Pólizas canceladas",
                "motivos": "Motivo(s) de cancelación"
            })
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("No hay clientes con pólizas canceladas.")

    # =====================================================
    # REPORTE 7: RESUMEN DE PÓLIZAS POR TIPO DE SEGURO
    # =====================================================
    elif reporte_seleccionado == "Resumen de Pólizas por Tipo de Seguro":
        st.subheader("📊 Resumen de Pólizas por Tipo de Seguro")
        st.caption(f"Fecha del reporte: {date.today().strftime('%d/%m/%Y')}")

        tipos_seguro = listar_tipos_seguro()
        resumen = []

        for tipo in tipos_seguro:
            with Database() as db:
                stats = db.fetch_one(
                    """
                    SELECT COUNT(*) as cantidad,
                           COALESCE(SUM(primamensual), 0) as total_primas,
                           COALESCE(SUM(montoasegurado), 0) as total_asegurado
                    FROM poliza
                    WHERE idtiposeguro = %s AND idestadopoliza = 1;
                    """,
                    (tipo["idtiposeguro"],)
                )
            resumen.append({
                "Tipo de seguro": tipo["nombre"],
                "Cantidad de pólizas activas": stats["cantidad"],
                "Total de primas mensuales": f"${stats['total_primas']:,.2f}",
                "Total de monto asegurado": f"${stats['total_asegurado']:,.2f}"
            })

        df = pd.DataFrame(resumen)
        st.dataframe(df, use_container_width=True)

    # =====================================================
    # REPORTE 8: RESUMEN DE RECLAMACIONES POR ESTADO
    # =====================================================
    elif reporte_seleccionado == "Resumen de Reclamaciones por Estado":
        st.subheader("📊 Resumen de Reclamaciones por Estado")
        st.caption(f"Fecha del reporte: {date.today().strftime('%d/%m/%Y')}")

        estados = listar_estados_reclamacion()
        resumen = []

        for estado in estados:
            with Database() as db:
                stats = db.fetch_one(
                    """
                    SELECT COUNT(*) as cantidad,
                           COALESCE(SUM(montoreclamado), 0) as total_reclamado,
                           COALESCE(SUM(montoindemnizado), 0) as total_indemnizado
                    FROM reclamacion
                    WHERE idestadoreclamacion = %s;
                    """,
                    (estado["idestadoreclamacion"],)
                )
            resumen.append({
                "Estado": estado["nombre"],
                "Cantidad": stats["cantidad"],
                "Total monto reclamado": f"${stats['total_reclamado']:,.2f}",
                "Total monto indemnizado": f"${stats['total_indemnizado']:,.2f}"
            })

        df = pd.DataFrame(resumen)
        st.dataframe(df, use_container_width=True)

    # =====================================================
    # REPORTE 9: LISTADO DE INGRESOS MENSUALES
    # =====================================================
    elif reporte_seleccionado == "Listado de Ingresos Mensuales":
        st.subheader("📊 Listado de Ingresos Mensuales")
        st.caption(f"Fecha del reporte: {date.today().strftime('%d/%m/%Y')}")

        with Database() as db:
            ingresos = db.fetch_all(
                """
                SELECT EXTRACT(YEAR FROM fechapago) as anio,
                       EXTRACT(MONTH FROM fechapago) as mes,
                       TO_CHAR(fechapago, 'Month') as nombre_mes,
                       COALESCE(SUM(montopagado), 0) as ingreso
                FROM pago
                GROUP BY anio, mes, nombre_mes
                ORDER BY anio DESC, mes DESC;
                """
            )

        if ingresos:
            # Calcular total anual
            df = pd.DataFrame(ingresos)
            total_anual = df["ingreso"].sum()

            st.metric("💰 Ingreso total anual", f"${total_anual:,.2f}")

            df_display = df.rename(columns={
                "anio": "Año",
                "nombre_mes": "Mes",
                "ingreso": "Ingreso mensual ($)"
            })
            st.dataframe(df_display[["Año", "Mes", "Ingreso mensual ($)"]], use_container_width=True)
        else:
            st.info("No hay pagos registrados.")

    # =====================================================
    # REPORTE 10: CLIENTES CON RECLAMACIONES APROBADAS
    # =====================================================
    elif reporte_seleccionado == "Reporte de Clientes con Reclamaciones Aprobadas":
        st.subheader("📋 Clientes con Reclamaciones Aprobadas")
        st.caption(f"Fecha del reporte: {date.today().strftime('%d/%m/%Y')}")

        with Database() as db:
            clientes = db.fetch_all(
                """
                SELECT c.idcliente, c.nombre, c.apellidos,
                       COUNT(r.idreclamacion) as cantidad_aprobadas,
                       COALESCE(SUM(r.montoindemnizado), 0) as total_indemnizado
                FROM cliente c
                JOIN poliza p ON c.idcliente = p.idcliente
                JOIN reclamacion r ON p.idpoliza = r.idpoliza
                WHERE r.idestadoreclamacion = (SELECT idestadoreclamacion FROM estado_reclamacion WHERE lower(nombre) = 'aprobada')
                GROUP BY c.idcliente, c.nombre, c.apellidos
                ORDER BY total_indemnizado DESC;
                """
            )

        if clientes:
            df = pd.DataFrame(clientes)
            df_display = df.rename(columns={
                "idcliente": "ID",
                "nombre": "Nombre",
                "apellidos": "Apellidos",
                "cantidad_aprobadas": "Reclamaciones aprobadas",
                "total_indemnizado": "Total indemnizado ($)"
            })
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("No hay clientes con reclamaciones aprobadas.")

    # =====================================================
    # REPORTE 11: CLIENTES CON RECLAMACIONES RECHAZADAS
    # =====================================================
    elif reporte_seleccionado == "Reporte de Clientes con Reclamaciones Rechazadas":
        st.subheader("📋 Clientes con Reclamaciones Rechazadas")
        st.caption(f"Fecha del reporte: {date.today().strftime('%d/%m/%Y')}")

        with Database() as db:
            clientes = db.fetch_all(
                """
                SELECT c.idcliente, c.nombre, c.apellidos,
                       COUNT(r.idreclamacion) as cantidad_rechazadas,
                       STRING_AGG(rr.motivo, '; ') as motivos
                FROM cliente c
                JOIN poliza p ON c.idcliente = p.idcliente
                JOIN reclamacion r ON p.idpoliza = r.idpoliza
                JOIN reclamacion_rechazada rr ON r.idreclamacion = rr.idreclamacion
                GROUP BY c.idcliente, c.nombre, c.apellidos
                ORDER BY cantidad_rechazadas DESC;
                """
            )

        if clientes:
            df = pd.DataFrame(clientes)
            df_display = df.rename(columns={
                "idcliente": "ID",
                "nombre": "Nombre",
                "apellidos": "Apellidos",
                "cantidad_rechazadas": "Reclamaciones rechazadas",
                "motivos": "Motivo(s) del rechazo"
            })
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("No hay clientes con reclamaciones rechazadas.")

    # =====================================================
    # REPORTE 12: FICHA DE LA AGENCIA
    # =====================================================
    elif reporte_seleccionado == "Ficha de la Agencia de Seguros":
        st.subheader("🏢 Ficha de la Agencia de Seguros")

        agencia = obtener_agencia()

        if agencia:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Nombre:** {agencia['nombre']}")
                st.markdown(f"**Dirección:** {agencia['direccion']}")
                st.markdown(f"**Teléfono:** {agencia['telefono']}")
                st.markdown(f"**Email:** {agencia['email']}")
            with col2:
                st.markdown(f"**Director General:** {agencia['directorgeneral']}")
                st.markdown(f"**Jefe de Seguros:** {agencia['jefeseguros']}")
                st.markdown(f"**Jefe de Reclamaciones:** {agencia['jefereclamaciones']}")
        else:
            st.warning("⚠️ No hay datos de la agencia registrados.")

    # =====================================================
    # REPORTE 13: FICHA DE UN CLIENTE DETERMINADO
    # =====================================================
    elif reporte_seleccionado == "Ficha de un Cliente Determinado":
        st.subheader("👤 Ficha de un Cliente Determinado")

        clientes = listar_clientes()
        if clientes:
            cliente_opciones = {c["idcliente"]: f"{c['nombre']} {c['apellidos']}" for c in clientes}
            cliente_seleccionado = st.selectbox(
                "Seleccione un cliente:",
                options=list(cliente_opciones.keys()),
                format_func=lambda x: cliente_opciones[x]
            )

            if cliente_seleccionado:
                cliente = obtener_cliente_por_id(cliente_seleccionado)
                if cliente:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Nombre:** {cliente['nombre']} {cliente['apellidos']}")
                        st.markdown(f"**Número de identificación:** {cliente['no_identificacion']}")
                        st.markdown(f"**Edad:** {cliente['edad']}")
                        st.markdown(f"**Sexo:** {'Masculino' if cliente['sexo'] == 'M' else 'Femenino'}")
                    with col2:
                        st.markdown(f"**Teléfono:** {cliente['telefono'] or 'No registrado'}")
                        st.markdown(f"**Dirección postal:** {cliente['dir_postal'] or 'No registrada'}")
                        st.markdown(f"**Correo electrónico:** {cliente['correo'] or 'No registrado'}")

                    # Pólizas activas
                    with Database() as db:
                        polizas_activas = db.fetch_one(
                            """
                            SELECT COUNT(*) as cantidad
                            FROM poliza
                            WHERE idcliente = %s AND idestadopoliza = 1;
                            """,
                            (cliente_seleccionado,)
                        )
                        total_pagado = total_pagado_por_cliente(cliente_seleccionado)

                    st.divider()
                    col1, col2 = st.columns(2)
                    col1.metric("📋 Pólizas activas", polizas_activas["cantidad"])
                    col2.metric("💰 Total primas pagadas", f"${total_pagado:,.2f}")

                    # Reclamaciones del cliente
                    with Database() as db:
                        reclamaciones = db.fetch_all(
                            """
                            SELECT r.idreclamacion, p.idpoliza, ts.nombre as tipo_seguro,
                                   r.fechasiniestro, r.montoreclamado, r.montoindemnizado,
                                   er.nombre as estado
                            FROM reclamacion r
                            JOIN poliza p ON r.idpoliza = p.idpoliza
                            JOIN tipo_seguro ts ON p.idtiposeguro = ts.idtiposeguro
                            JOIN estado_reclamacion er ON r.idestadoreclamacion = er.idestadoreclamacion
                            WHERE p.idcliente = %s
                            ORDER BY r.fechasiniestro DESC;
                            """,
                            (cliente_seleccionado,)
                        )

                    if reclamaciones:
                        st.subheader("📝 Reclamaciones")
                        df = pd.DataFrame(reclamaciones)
                        df_display = df.rename(columns={
                            "idreclamacion": "ID",
                            "idpoliza": "Póliza",
                            "tipo_seguro": "Tipo de seguro",
                            "fechasiniestro": "Fecha",
                            "montoreclamado": "Monto reclamado",
                            "montoindemnizado": "Monto indemnizado",
                            "estado": "Estado"
                        })
                        st.dataframe(df_display, use_container_width=True)
                    else:
                        st.info("Este cliente no tiene reclamaciones registradas.")
        else:
            st.warning("No hay clientes registrados.")

    # =====================================================
    # REPORTE 14: FICHA DE UNA REASEGURADORA ASOCIADA
    # =====================================================
    elif reporte_seleccionado == "Ficha de una Reaseguradora Asociada":
        st.subheader("🏢 Ficha de una Reaseguradora Asociada")

        with Database() as db:
            reaseguradoras = db.fetch_all("SELECT idreaseguradora, nombre FROM reaseguradora ORDER BY nombre;")

        if reaseguradoras:
            rea_opciones = {r["idreaseguradora"]: r["nombre"] for r in reaseguradoras}
            rea_seleccionada = st.selectbox(
                "Seleccione una reaseguradora:",
                options=list(rea_opciones.keys()),
                format_func=lambda x: rea_opciones[x]
            )

            if rea_seleccionada:
                rea = obtener_reaseguradora_por_id(rea_seleccionada)
                if rea:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Nombre:** {rea['nombre']}")
                        st.markdown(f"**País de origen:** {rea['pais_nombre']}")
                    with col2:
                        st.markdown(f"**Tipo de reaseguro:** {rea['tipo_reaseguro_nombre']}")
                        st.markdown(f"**Email:** {rea.get('email') or 'No registrado'}")

                    # Participaciones
                    with Database() as db:
                        participaciones = db.fetch_all(
                            """
                            SELECT ts.nombre as tipo_seguro, pr.porcentaje
                            FROM participacion_reaseguro pr
                            JOIN tipo_seguro ts ON pr.idtiposeguro = ts.idtiposeguro
                            WHERE pr.idreaseguradora = %s;
                            """,
                            (rea_seleccionada,)
                        )

                    if participaciones:
                        st.subheader("📊 Participaciones por tipo de seguro")
                        df = pd.DataFrame(participaciones)
                        df_display = df.rename(columns={
                            "tipo_seguro": "Tipo de seguro",
                            "porcentaje": "Porcentaje (%)"
                        })
                        st.dataframe(df_display, use_container_width=True)
                    else:
                        st.info("Esta reaseguradora no tiene participaciones registradas.")
        else:
            st.warning("No hay reaseguradoras registradas.")

    # =====================================================
    # REPORTE 15: PÓLIZAS EMITIDAS EN UN PERÍODO
    # =====================================================
    elif reporte_seleccionado == "Reporte de Pólizas Emitidas en un Período":
        st.subheader("📋 Pólizas Emitidas en un Período")

        col1, col2 = st.columns(2)
        with col1:
            fecha_desde = st.date_input("Fecha desde:", value=date.today().replace(month=1, day=1))
        with col2:
            fecha_hasta = st.date_input("Fecha hasta:", value=date.today())

        if st.button("Generar reporte", use_container_width=True):
            with Database() as db:
                polizas = db.fetch_all(
                    """
                    SELECT p.idpoliza, c.nombre || ' ' || c.apellidos as cliente,
                           ts.nombre as tipo_seguro,
                           p.fechainicio, p.fechafin, p.primamensual, ep.nombre as estado
                    FROM poliza p
                    JOIN cliente c ON p.idcliente = c.idcliente
                    JOIN tipo_seguro ts ON p.idtiposeguro = ts.idtiposeguro
                    JOIN estado_poliza ep ON p.idestadopoliza = ep.idestadopoliza
                    WHERE p.fechainicio BETWEEN %s AND %s
                    ORDER BY p.fechainicio;
                    """,
                    (fecha_desde, fecha_hasta)
                )

            if polizas:
                df = pd.DataFrame(polizas)
                df_display = df.rename(columns={
                    "idpoliza": "Número de póliza",
                    "cliente": "Cliente",
                    "tipo_seguro": "Tipo de seguro",
                    "fechainicio": "Fecha inicio",
                    "fechafin": "Fecha fin",
                    "primamensual": "Prima mensual",
                    "estado": "Estado"
                })
                st.dataframe(df_display, use_container_width=True)
                st.caption(f"Total de pólizas emitidas: {len(polizas)}")
            else:
                st.info("No hay pólizas emitidas en el período seleccionado.")

    # =====================================================
    # REPORTE 16: ESTADO DE LAS RECLAMACIONES
    # =====================================================
    elif reporte_seleccionado == "Reporte de Estado de las Reclamaciones":
        st.subheader("📋 Estado de las Reclamaciones")

        reclamaciones = listar_reclamaciones()

        if reclamaciones:
            df = pd.DataFrame(reclamaciones)
            df_display = df.rename(columns={
                "idreclamacion": "Número de reclamación",
                "cliente": "Cliente",
                "idpoliza": "Número de póliza",
                "tipo_seguro": "Tipo de seguro",
                "tipo_siniestro": "Tipo de siniestro",
                "fechasiniestro": "Fecha del siniestro",
                "estado": "Estado",
                "montoreclamado": "Monto reclamado",
                "montoindemnizado": "Monto indemnizado"
            })
            st.dataframe(df_display[[
                "Número de reclamación", "Cliente", "Número de póliza", "Tipo de seguro",
                "Tipo de siniestro", "Fecha del siniestro", "Estado", "Monto reclamado", "Monto indemnizado"
            ]], use_container_width=True)
        else:
            st.info("No hay reclamaciones registradas.")

    # =====================================================
    # REPORTE 17: INGRESOS MENSUALES POR CONCEPTO DE PRIMAS
    # =====================================================
    elif reporte_seleccionado == "Reporte de Ingresos Mensuales por Concepto de Primas":
        st.subheader("📊 Ingresos Mensuales por Concepto de Primas")

        años_disponibles = [date.today().year, date.today().year - 1, date.today().year - 2]
        año_seleccionado = st.selectbox("Seleccione el año:", options=años_disponibles, index=0)

        if st.button("Generar reporte", use_container_width=True):
            with Database() as db:
                ingresos = db.fetch_all(
                    """
                    SELECT EXTRACT(MONTH FROM fechapago) as mes,
                           TO_CHAR(fechapago, 'Month') as nombre_mes,
                           COALESCE(SUM(montopagado), 0) as ingreso
                    FROM pago
                    WHERE EXTRACT(YEAR FROM fechapago) = %s
                    GROUP BY mes, nombre_mes
                    ORDER BY mes;
                    """,
                    (año_seleccionado,)
                )

            if ingresos:
                # Asegurar que todos los meses del 1 al 12 estén presentes
                meses = {
                    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
                }

                datos_completos = []
                for mes_num, mes_nombre in meses.items():
                    ingreso = next((i["ingreso"] for i in ingresos if int(i["mes"]) == mes_num), 0)
                    datos_completos.append({
                        "Año": año_seleccionado,
                        "Mes": mes_nombre,
                        "Ingreso mensual ($)": f"${ingreso:,.2f}"
                    })

                df = pd.DataFrame(datos_completos)

                # Calcular total anual
                total_anual = sum(float(d["Ingreso mensual ($)"].replace("$", "").replace(",", "")) for d in datos_completos)
                st.metric("💰 Ingreso total anual", f"${total_anual:,.2f}")

                st.dataframe(df, use_container_width=True)

                # Gráfico de barras
                st.subheader("📈 Gráfico de ingresos mensuales")
                df_chart = pd.DataFrame(datos_completos)
                df_chart["Ingreso"] = df_chart["Ingreso mensual ($)"].str.replace("$", "").str.replace(",", "").astype(float)
                st.bar_chart(df_chart.set_index("Mes")["Ingreso"])
            else:
                st.info(f"No hay pagos registrados para el año {año_seleccionado}.")