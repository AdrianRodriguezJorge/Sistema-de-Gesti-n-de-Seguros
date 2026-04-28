import streamlit as st
import pandas as pd
from datetime import date

from data.class_poliza import Poliza
from data.class_cobertura import PolizaCobertura
from db.queries_poliza import (
    insertar_poliza, listar_polizas, obtener_poliza_por_id,
    actualizar_poliza, eliminar_poliza, cambiar_estado_poliza
)
from db.queries_cliente import listar_clientes
from db.queries_catalogos import listar_tipos_seguro, listar_estados_poliza
from db.queries_cobertura import listar_coberturas, listar_coberturas_de_poliza, agregar_cobertura_a_poliza
from db.conexionDB import Database


def _cargar_clientes():
    clientes = listar_clientes()
    if not clientes:
        return [], {}
    return clientes, {c["idcliente"]: f"{c['nombre']} {c['apellidos']}" for c in clientes}


def _cargar_tipos_seguro():
    tipos = listar_tipos_seguro()
    if not tipos:
        return [], {}
    return tipos, {t["idtiposeguro"]: t["nombre"] for t in tipos}


def _cargar_estados_poliza():
    estados = listar_estados_poliza()
    if not estados:
        return [], {}
    return estados, {e["idestadopoliza"]: e["nombre"] for e in estados}


def _cargar_coberturas_disponibles():
    coberturas = listar_coberturas()
    if not coberturas:
        return [], {}
    return coberturas, {c["idcobertura"]: c["descripcion"] for c in coberturas}


def pagina_polizas():
    st.title("📋 Pólizas")
    st.divider()

    # Recargar datos al abrir la página
    clientes, clientes_dict = _cargar_clientes()
    tipos_seguro, tipos_dict = _cargar_tipos_seguro()
    estados_poliza, estados_dict = _cargar_estados_poliza()

    tab1, tab2, tab3, tab4 = st.tabs(["Listado", "Nueva Póliza", "Editar/Estado", "Coberturas"])

    # =====================================================
    # TAB 1: LISTADO
    # =====================================================
    with tab1:
        st.subheader("📋 Listado de pólizas")

        # Filtros
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            id_buscar = st.text_input("🔍 Buscar por ID:", key="buscar_listado_pol")
        with col_f2:
            filtro_estado = st.selectbox(
                "📌 Filtrar por estado:",
                ["Todos"] + list(estados_dict.values()),
                key="filtro_estado_pol"
            )

        # Obtener y filtrar datos
        polizas = listar_polizas()

        if id_buscar:
            polizas = [p for p in polizas if id_buscar.lower() in p["idpoliza"].lower()]

        if filtro_estado != "Todos":
            polizas = [p for p in polizas if p["estado"] == filtro_estado]

        if polizas:
            df = pd.DataFrame(polizas)
            # Renombrar columnas para mostrar
            df_display = df.rename(columns={
                "idpoliza": "ID",
                "cliente_nombre": "Cliente",
                "tipo_seguro": "Tipo de seguro",
                "fechainicio": "Fecha inicio",
                "fechafin": "Fecha fin",
                "primamensual": "Prima mensual",
                "montoasegurado": "Monto asegurado",
                "estado": "Estado"
            })
            st.dataframe(df_display[["ID", "Cliente", "Tipo de seguro", "Fecha inicio", "Fecha fin", "Prima mensual", "Monto asegurado", "Estado"]], use_container_width=True)
        else:
            st.info("No hay pólizas registradas.")

    # =====================================================
    # TAB 2: NUEVA PÓLIZA
    # =====================================================
    with tab2:
        st.subheader("➕ Nueva póliza")

        if not clientes:
            st.warning("⚠️ No hay clientes registrados. Crea un cliente primero en la sección Clientes.")
        elif not tipos_seguro:
            st.warning("⚠️ No hay tipos de seguro registrados. Crea uno en Catálogos.")
        else:
            with st.form("form_nueva_poliza"):
                col1, col2 = st.columns(2)

                with col1:
                    cliente_opciones = {c["idcliente"]: f"{c['nombre']} {c['apellidos']}" for c in clientes}
                    cliente_seleccionado = st.selectbox(
                        "Cliente:",
                        options=list(cliente_opciones.keys()),
                        format_func=lambda x: cliente_opciones[x]
                    )

                    tipo_opciones = {t["idtiposeguro"]: t["nombre"] for t in tipos_seguro}
                    tipo_seleccionado = st.selectbox(
                        "Tipo de seguro:",
                        options=list(tipo_opciones.keys()),
                        format_func=lambda x: tipo_opciones[x]
                    )

                    fecha_inicio = st.date_input("Fecha inicio:", value=date.today())

                with col2:
                    estado_opciones = {e["idestadopoliza"]: e["nombre"] for e in estados_poliza}
                    estado_seleccionado = st.selectbox(
                        "Estado inicial:",
                        options=list(estado_opciones.keys()),
                        format_func=lambda x: estado_opciones[x]
                    )

                    fecha_fin = st.date_input("Fecha fin:", value=date.today().replace(year=date.today().year + 1))

                prima_mensual = st.number_input("Prima mensual ($):", min_value=0.01, step=10.00, format="%.2f")
                monto_asegurado = st.number_input("Monto asegurado ($):", min_value=0.01, step=1000.00, format="%.2f")

                id_poliza = st.text_input("ID de la póliza (dejar vacío para auto-generar):", placeholder="Ej: POL001")

                guardar = st.form_submit_button("💾 Guardar póliza", use_container_width=True)

            if guardar:
                try:
                    # Generar ID si está vacío
                    if not id_poliza:
                        with Database() as db:
                            last_id = db.fetch_one("SELECT idpoliza FROM poliza ORDER BY idpoliza DESC LIMIT 1;")
                            if last_id:
                                num = int(last_id["idpoliza"].replace("POL", "")) + 1
                                id_poliza = f"POL{num:03d}"
                            else:
                                id_poliza = "POL001"

                    poliza = Poliza(
                        id_tipo_seguro=tipo_seleccionado,
                        fecha_inicio=fecha_inicio,
                        fecha_fin=fecha_fin,
                        prima_mensual=prima_mensual,
                        id_estado_poliza=estado_seleccionado,
                        monto_asegurado=monto_asegurado,
                        id_cliente=cliente_seleccionado,
                        id_poliza=id_poliza
                    )
                    insertar_poliza(poliza)
                    st.success(f"✅ Póliza {id_poliza} registrada correctamente.")
                    st.rerun()
                except ValueError as e:
                    st.error(f"❌ Error: {e}")
                except Exception as e:
                    st.error(f"❌ Error inesperado: {e}")

    # =====================================================
    # TAB 3: EDITAR / ESTADO
    # =====================================================
    with tab3:
        st.subheader("✏️ Editar póliza o cambiar estado")

        id_buscar = st.text_input("ID de la póliza a buscar:", key="buscar_editar_pol")

        if id_buscar:
            poliza_data = obtener_poliza_por_id(id_buscar)

            if poliza_data:
                st.success(f"✅ Póliza encontrada: {poliza_data['idpoliza']}")

                col_edit, col_estado = st.columns(2)

                # EDITAR
                with col_edit:
                    st.markdown("### 📝 Editar datos")
                    with st.form("form_editar_poliza"):
                        # Datos actuales
                        cliente_actual = poliza_data["idcliente"]
                        tipo_actual = poliza_data["idtiposeguro"]
                        estado_actual = poliza_data["idestadopoliza"]

                        cliente_opciones = {c["idcliente"]: f"{c['nombre']} {c['apellidos']}" for c in clientes}
                        cliente_nuevo = st.selectbox(
                            "Cliente:",
                            options=list(cliente_opciones.keys()),
                            format_func=lambda x: cliente_opciones[x],
                            index=list(cliente_opciones.keys()).index(cliente_actual) if cliente_actual in cliente_opciones else 0
                        )

                        tipo_opciones = {t["idtiposeguro"]: t["nombre"] for t in tipos_seguro}
                        tipo_nuevo = st.selectbox(
                            "Tipo de seguro:",
                            options=list(tipo_opciones.keys()),
                            format_func=lambda x: tipo_opciones[x],
                            index=list(tipo_opciones.keys()).index(tipo_actual) if tipo_actual in tipo_opciones else 0
                        )

                        fecha_inicio = st.date_input("Fecha inicio:", value=poliza_data["fechainicio"])
                        fecha_fin = st.date_input("Fecha fin:", value=poliza_data["fechafin"])
                        prima_mensual = st.number_input("Prima mensual ($):", value=float(poliza_data["primamensual"]), step=10.00)
                        monto_asegurado = st.number_input("Monto asegurado ($):", value=float(poliza_data["montoasegurado"]), step=1000.00)

                        actualizar = st.form_submit_button("🔄 Actualizar póliza", use_container_width=True)

                    if actualizar:
                        try:
                            poliza_edit = Poliza(
                                id_tipo_seguro=tipo_nuevo,
                                fecha_inicio=fecha_inicio,
                                fecha_fin=fecha_fin,
                                prima_mensual=prima_mensual,
                                id_estado_poliza=estado_actual,
                                monto_asegurado=monto_asegurado,
                                id_cliente=cliente_nuevo,
                                id_poliza=id_buscar
                            )
                            actualizar_poliza(poliza_edit)
                            st.success(f"✅ Póliza {id_buscar} actualizada correctamente.")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"❌ Error: {e}")

                # CAMBIAR ESTADO
                with col_estado:
                    st.markdown("### 🔄 Cambiar estado")
                    with st.form("form_estado_poliza"):
                        estado_opciones = {e["idestadopoliza"]: e["nombre"] for e in estados_poliza}
                        nuevo_estado = st.selectbox(
                            "Nuevo estado:",
                            options=list(estado_opciones.keys()),
                            format_func=lambda x: estado_opciones[x],
                            key="nuevo_estado"
                        )

                        motivo = st.text_area(
                            "Motivo (requerido si cancelas):",
                            height=80,
                            placeholder="Ej: Cliente solicitó cancelación, falta de pago, etc."
                        )

                        aplicar = st.form_submit_button("📌 Aplicar cambio de estado", use_container_width=True)

                    if aplicar:
                        try:
                            # Si el nuevo estado es Cancelada, validar motivo
                            if estado_opciones[nuevo_estado] == "Cancelada":
                                if not motivo.strip():
                                    st.error("❌ Debes proporcionar un motivo para cancelar la póliza.")
                                else:
                                    cambiar_estado_poliza(id_buscar, nuevo_estado, motivo)
                                    st.success(f"✅ Estado cambiado a {estado_opciones[nuevo_estado]}.")
                                    st.rerun()
                            else:
                                cambiar_estado_poliza(id_buscar, nuevo_estado)
                                st.success(f"✅ Estado cambiado a {estado_opciones[nuevo_estado]}.")
                                st.rerun()
                        except ValueError as e:
                            st.error(f"❌ Error: {e}")

                    st.divider()

                    # Eliminar póliza
                    if st.button("🗑️ Eliminar esta póliza", type="secondary", use_container_width=True):
                        try:
                            eliminar_poliza(id_buscar)
                            st.success(f"✅ Póliza {id_buscar} eliminada correctamente.")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"❌ Error: {e}")
            else:
                st.error("❌ No se encontró una póliza con ese ID.")

    # =====================================================
    # TAB 4: COBERTURAS
    # =====================================================
    with tab4:
        st.subheader("🛡️ Coberturas de la póliza")

        id_pol_cob = st.text_input("ID de la póliza:", key="cob_pol")

        if id_pol_cob:
            # Verificar que la póliza existe
            poliza_check = obtener_poliza_por_id(id_pol_cob)
            if poliza_check:
                st.success(f"✅ Póliza encontrada: {id_pol_cob}")

                # Mostrar coberturas actuales
                coberturas_actuales = listar_coberturas_de_poliza(id_pol_cob)

                if coberturas_actuales:
                    st.markdown("### 📋 Coberturas actuales")
                    for cob in coberturas_actuales:
                        col1, col2, col3 = st.columns([4, 2, 1])
                        col1.write(f"**{cob['descripcion']}**")
                        col2.write(f"${cob['monto']:,.2f}")
                        if col3.button("🗑️", key=f"del_{cob['idcobertura']}"):
                            from db.queries_cobertura import eliminar_cobertura_de_poliza
                            eliminar_cobertura_de_poliza(id_pol_cob, cob["idcobertura"])
                            st.rerun()
                else:
                    st.info("Esta póliza no tiene coberturas asignadas.")

                st.divider()

                # Agregar nueva cobertura
                st.markdown("### ➕ Agregar cobertura")
                coberturas_disponibles, coberturas_dict = _cargar_coberturas_disponibles()

                if not coberturas_disponibles:
                    st.warning("⚠️ No hay coberturas registradas. Crea una en Catálogos.")
                else:
                    with st.form("form_agregar_cobertura"):
                        col1, col2 = st.columns(2)
                        with col1:
                            cobertura_opciones = {c["idcobertura"]: c["descripcion"] for c in coberturas_disponibles}
                            cobertura_seleccionada = st.selectbox(
                                "Cobertura:",
                                options=list(cobertura_opciones.keys()),
                                format_func=lambda x: cobertura_opciones[x]
                            )
                        with col2:
                            monto = st.number_input("Monto asegurado para esta cobertura ($):", min_value=0.01, step=100.00)

                        agregar = st.form_submit_button("➕ Agregar cobertura", use_container_width=True)

                    if agregar:
                        try:
                            agregar_cobertura_a_poliza(id_pol_cob, cobertura_seleccionada, monto)
                            st.success(f"✅ Cobertura agregada correctamente.")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"❌ Error: {e}")
            else:
                st.error("❌ No se encontró una póliza con ese ID.")