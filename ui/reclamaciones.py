import streamlit as st
import pandas as pd
from datetime import date

from data.class_reclamacion import Reclamacion, ReclamacionRechazada
from db.queries_reclamacion import (
    insertar_reclamacion, listar_reclamaciones, obtener_reclamacion_por_id,
    actualizar_reclamacion, eliminar_reclamacion, rechazar_reclamacion, aprobar_reclamacion
)
from db.queries_poliza import listar_polizas, obtener_poliza_por_id
from db.queries_catalogos import listar_tipos_siniestro, listar_estados_reclamacion


def _cargar_polizas():
    polizas = listar_polizas()
    if not polizas:
        return [], {}
    return polizas, {p["idpoliza"]: f"{p['idpoliza']} - {p['cliente_nombre']}" for p in polizas}


def _cargar_tipos_siniestro():
    tipos = listar_tipos_siniestro()
    if not tipos:
        return [], {}
    return tipos, {t["idtiposiniestro"]: t["nombre"] for t in tipos}


def _cargar_estados_reclamacion():
    estados = listar_estados_reclamacion()
    if not estados:
        return [], {}
    return estados, {e["idestadoreclamacion"]: e["nombre"] for e in estados}


def pagina_reclamaciones():
    st.title("📝 Reclamaciones")
    st.divider()

    polizas, polizas_dict = _cargar_polizas()
    tipos_siniestro, tipos_dict = _cargar_tipos_siniestro()
    estados_reclamacion, estados_dict = _cargar_estados_reclamacion()

    tab1, tab2, tab3 = st.tabs(["Listado", "Nueva Reclamación", "Editar/Estado"])

    # =====================================================
    # TAB 1: LISTADO
    # =====================================================
    with tab1:
        st.subheader("📋 Listado de reclamaciones")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            id_buscar = st.text_input("🔍 Buscar por ID:", key="buscar_rec_listado")
        with col_f2:
            filtro_estado = st.selectbox(
                "📌 Filtrar por estado:",
                ["Todos"] + list(estados_dict.values()),
                key="filtro_estado_rec"
            )

        reclamaciones = listar_reclamaciones()

        if id_buscar:
            reclamaciones = [r for r in reclamaciones if id_buscar.lower() in r["idreclamacion"].lower()]

        if filtro_estado != "Todos":
            reclamaciones = [r for r in reclamaciones if r["estado"] == filtro_estado]

        if reclamaciones:
            df = pd.DataFrame(reclamaciones)
            df_display = df.rename(columns={
                "idreclamacion": "ID",
                "cliente": "Cliente",
                "idpoliza": "Póliza",
                "tipo_seguro": "Tipo de seguro",
                "tipo_siniestro": "Tipo siniestro",
                "fechasiniestro": "Fecha siniestro",
                "montoreclamado": "Monto reclamado",
                "montoindemnizado": "Monto indemnizado",
                "estado": "Estado"
            })
            st.dataframe(df_display[[
                "ID", "Cliente", "Póliza", "Tipo de seguro", "Tipo siniestro",
                "Fecha siniestro", "Monto reclamado", "Monto indemnizado", "Estado"
            ]], use_container_width=True)
        else:
            st.info("No hay reclamaciones registradas.")

    # =====================================================
    # TAB 2: NUEVA RECLAMACIÓN
    # =====================================================
    with tab2:
        st.subheader("➕ Nueva reclamación")

        if not polizas:
            st.warning("⚠️ No hay pólizas registradas. Crea una póliza primero.")
        elif not tipos_siniestro:
            st.warning("⚠️ No hay tipos de siniestro registrados. Crea uno en Catálogos.")
        else:
            with st.form("form_nueva_reclamacion"):
                col1, col2 = st.columns(2)

                with col1:
                    poliza_opciones = {p["idpoliza"]: f"{p['idpoliza']} - {p['cliente_nombre']}" for p in polizas}
                    poliza_seleccionada = st.selectbox(
                        "Póliza:",
                        options=list(poliza_opciones.keys()),
                        format_func=lambda x: poliza_opciones[x]
                    )

                    tipo_opciones = {t["idtiposiniestro"]: t["nombre"] for t in tipos_siniestro}
                    tipo_seleccionado = st.selectbox(
                        "Tipo de siniestro:",
                        options=list(tipo_opciones.keys()),
                        format_func=lambda x: tipo_opciones[x]
                    )

                    fecha_siniestro = st.date_input("Fecha del siniestro:", value=date.today())

                with col2:
                    estado_opciones = {e["idestadoreclamacion"]: e["nombre"] for e in estados_reclamacion}
                    estado_seleccionado = st.selectbox(
                        "Estado inicial:",
                        options=list(estado_opciones.keys()),
                        format_func=lambda x: estado_opciones[x],
                        index=0  # En proceso normalmente es el primero
                    )

                    monto_reclamado = st.number_input("Monto reclamado ($):", min_value=0.01, step=100.00, format="%.2f")

                    # Solo mostrar monto indemnizado si el estado es Aprobada
                    if estado_opciones[estado_seleccionado] == "Aprobada":
                        monto_indemnizado = st.number_input("Monto indemnizado ($):", min_value=0.00, step=100.00, format="%.2f")
                    else:
                        monto_indemnizado = 0.00

                id_reclamacion = st.text_input("ID (dejar vacío para auto-generar):", placeholder="Ej: REC001")

                guardar = st.form_submit_button("💾 Guardar reclamación", use_container_width=True)

            if guardar:
                try:
                    # Validar que el monto indemnizado no exceda el reclamado
                    if monto_indemnizado > monto_reclamado:
                        st.error("❌ El monto indemnizado no puede ser mayor que el monto reclamado.")
                    else:
                        # Generar ID si está vacío
                        if not id_reclamacion:
                            from db.conexionDB import Database
                            with Database() as db:
                                last_id = db.fetch_one("SELECT idreclamacion FROM reclamacion ORDER BY idreclamacion DESC LIMIT 1;")
                                if last_id:
                                    num = int(last_id["idreclamacion"].replace("REC", "")) + 1
                                    id_reclamacion = f"REC{num:03d}"
                                else:
                                    id_reclamacion = "REC001"

                        reclamacion = Reclamacion(
                            id_tipo_siniestro=tipo_seleccionado,
                            fecha_siniestro=fecha_siniestro,
                            monto_reclamado=monto_reclamado,
                            id_estado_reclamacion=estado_seleccionado,
                            monto_indemnizado=monto_indemnizado,
                            id_poliza=poliza_seleccionada,
                            id_reclamacion=id_reclamacion
                        )
                        insertar_reclamacion(reclamacion)
                        st.success(f"✅ Reclamación {id_reclamacion} registrada correctamente.")
                        st.rerun()
                except ValueError as e:
                    st.error(f"❌ Error: {e}")
                except Exception as e:
                    st.error(f"❌ Error inesperado: {e}")

    # =====================================================
    # TAB 3: EDITAR / ESTADO
    # =====================================================
    with tab3:
        st.subheader("✏️ Editar reclamación o cambiar estado")

        id_buscar = st.text_input("ID de la reclamación a buscar:", key="buscar_editar_rec")

        if id_buscar:
            rec_data = obtener_reclamacion_por_id(id_buscar)

            if rec_data:
                # Obtener el nombre del cliente y tipo de seguro
                st.success(f"✅ Reclamación encontrada para: {rec_data['cliente_nombre']}")

                col_edit, col_estado = st.columns(2)

                # EDITAR
                with col_edit:
                    st.markdown("### 📝 Editar datos")
                    with st.form("form_editar_reclamacion"):
                        tipo_opciones = {t["idtiposiniestro"]: t["nombre"] for t in tipos_siniestro}
                        tipo_actual = rec_data["idtiposiniestro"]
                        tipo_nuevo = st.selectbox(
                            "Tipo de siniestro:",
                            options=list(tipo_opciones.keys()),
                            format_func=lambda x: tipo_opciones[x],
                            index=list(tipo_opciones.keys()).index(tipo_actual) if tipo_actual in tipo_opciones else 0
                        )

                        fecha_siniestro = st.date_input("Fecha del siniestro:", value=rec_data["fechasiniestro"])
                        monto_reclamado = st.number_input("Monto reclamado ($):", value=float(rec_data["montoreclamado"]), step=100.00)

                        # Solo mostrar monto indemnizado si no está rechazada
                        estado_actual_nombre = estados_dict.get(rec_data["idestadoreclamacion"], "")
                        if estado_actual_nombre != "Rechazada":
                            monto_indemnizado = st.number_input(
                                "Monto indemnizado ($):",
                                value=float(rec_data["montoindemnizado"] or 0),
                                step=100.00
                            )
                        else:
                            monto_indemnizado = rec_data["montoindemnizado"]
                            st.info("ℹ️ Esta reclamación está rechazada, no se puede modificar el monto indemnizado.")

                        actualizar = st.form_submit_button("🔄 Actualizar reclamación", use_container_width=True)

                    if actualizar:
                        try:
                            if monto_indemnizado > monto_reclamado:
                                st.error("❌ El monto indemnizado no puede ser mayor que el monto reclamado.")
                            else:
                                reclamacion_edit = Reclamacion(
                                    id_tipo_siniestro=tipo_nuevo,
                                    fecha_siniestro=fecha_siniestro,
                                    monto_reclamado=monto_reclamado,
                                    id_estado_reclamacion=rec_data["idestadoreclamacion"],
                                    monto_indemnizado=monto_indemnizado,
                                    id_poliza=rec_data["idpoliza"],
                                    id_reclamacion=id_buscar
                                )
                                actualizar_reclamacion(reclamacion_edit)
                                st.success(f"✅ Reclamación {id_buscar} actualizada correctamente.")
                                st.rerun()
                        except ValueError as e:
                            st.error(f"❌ Error: {e}")

                # CAMBIAR ESTADO
                with col_estado:
                    st.markdown("### 🔄 Cambiar estado")

                    # Mostrar estado actual
                    estado_actual_nombre = estados_dict.get(rec_data["idestadoreclamacion"], "Desconocido")
                    st.info(f"Estado actual: **{estado_actual_nombre}**")

                    with st.form("form_estado_reclamacion"):
                        estado_opciones = {e["idestadoreclamacion"]: e["nombre"] for e in estados_reclamacion}
                        # Filtrar opciones según estado actual (no se puede pasar de Rechazada a otro)
                        if estado_actual_nombre == "Rechazada":
                            opciones_disponibles = {k: v for k, v in estado_opciones.items() if v == "Rechazada"}
                            st.warning("⚠️ Esta reclamación ya está rechazada y no se puede cambiar de estado.")
                        elif estado_actual_nombre == "Aprobada":
                            opciones_disponibles = {k: v for k, v in estado_opciones.items() if v != "Rechazada"}
                        else:
                            opciones_disponibles = estado_opciones

                        nuevo_estado = st.selectbox(
                            "Nuevo estado:",
                            options=list(opciones_disponibles.keys()),
                            format_func=lambda x: opciones_disponibles[x],
                            key="nuevo_estado_rec"
                        )

                        motivo = st.text_area(
                            "Motivo (requerido si rechazas):",
                            height=80,
                            placeholder="Ej: Documentación insuficiente, no cubierto por la póliza, etc.",
                            key="motivo_rec"
                        )

                        aplicar = st.form_submit_button("📌 Aplicar cambio de estado", use_container_width=True)

                    if aplicar:
                        try:
                            nuevo_estado_nombre = opciones_disponibles[nuevo_estado]

                            if nuevo_estado_nombre == "Aprobada":
                                monto_ind = st.number_input(
                                    "Monto a indemnizar ($):",
                                    min_value=0.00,
                                    max_value=float(rec_data["montoreclamado"]),
                                    step=100.00,
                                    key="monto_ind_aprobar"
                                )
                                if st.button("Confirmar aprobación", use_container_width=True):
                                    aprobar_reclamacion(id_buscar, monto_ind)
                                    st.success(f"✅ Reclamación aprobada con indemnización de ${monto_ind:,.2f}.")
                                    st.rerun()
                            elif nuevo_estado_nombre == "Rechazada":
                                if not motivo.strip():
                                    st.error("❌ Debes proporcionar un motivo para rechazar la reclamación.")
                                else:
                                    rechazar_reclamacion(id_buscar, motivo)
                                    st.success(f"✅ Reclamación rechazada.")
                                    st.rerun()
                            else:
                                # Cambio a "En Proceso" sin más validaciones
                                from db.queries_reclamacion import cambiar_estado_reclamacion
                                cambiar_estado_reclamacion(id_buscar, nuevo_estado)
                                st.success(f"✅ Estado cambiado a {nuevo_estado_nombre}.")
                                st.rerun()
                        except ValueError as e:
                            st.error(f"❌ Error: {e}")

                    st.divider()

                    # Eliminar reclamación (solo si no está aprobada/rechazada)
                    if estado_actual_nombre not in ["Aprobada", "Rechazada"]:
                        if st.button("🗑️ Eliminar esta reclamación", type="secondary", use_container_width=True):
                            try:
                                eliminar_reclamacion(id_buscar)
                                st.success(f"✅ Reclamación {id_buscar} eliminada correctamente.")
                                st.rerun()
                            except ValueError as e:
                                st.error(f"❌ Error: {e}")
                    else:
                        st.info("ℹ️ Las reclamaciones aprobadas o rechazadas no se pueden eliminar.")
            else:
                st.error("❌ No se encontró una reclamación con ese ID.")