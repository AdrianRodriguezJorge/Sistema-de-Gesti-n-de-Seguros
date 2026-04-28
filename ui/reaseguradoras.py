import streamlit as st
import pandas as pd

from data.class_reaseguradora import Reaseguradora, ParticipacionReaseguro
from db.queries_reaseguradora import (
    insertar_reaseguradora, listar_reaseguradoras, obtener_reaseguradora_por_id,
    actualizar_reaseguradora, eliminar_reaseguradora,
    agregar_participacion, listar_participaciones
)
from db.queries_catalogos import listar_paises, listar_tipos_seguro, listar_tipos_reaseguro


def _cargar_paises():
    paises = listar_paises()
    if not paises:
        return [], {}
    return paises, {p["idpais"]: p["nombre"] for p in paises}


def _cargar_tipos_reaseguro():
    tipos = listar_tipos_reaseguro()
    if not tipos:
        return [], {}
    return tipos, {t["idtiporeaseguro"]: t["nombre"] for t in tipos}


def _cargar_tipos_seguro():
    tipos = listar_tipos_seguro()
    if not tipos:
        return [], {}
    return tipos, {t["idtiposeguro"]: t["nombre"] for t in tipos}


def pagina_reaseguradoras():
    st.title("🏢 Reaseguradoras")
    st.divider()

    paises, paises_dict = _cargar_paises()
    tipos_reaseguro, tipos_reaseguro_dict = _cargar_tipos_reaseguro()
    tipos_seguro, tipos_seguro_dict = _cargar_tipos_seguro()

    tab1, tab2, tab3, tab4 = st.tabs(["Listado", "Nueva Reaseguradora", "Editar/Eliminar", "Participaciones"])

    # =====================================================
    # TAB 1: LISTADO
    # =====================================================
    with tab1:
        st.subheader("📋 Listado de reaseguradoras")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            id_buscar = st.text_input("🔍 Buscar por ID:", key="buscar_rea_listado")
        with col_f2:
            filtro_pais = st.selectbox(
                "📌 Filtrar por país:",
                ["Todos"] + list(paises_dict.values()),
                key="filtro_pais_rea"
            )

        reaseguradoras = listar_reaseguradoras()

        if id_buscar:
            reaseguradoras = [r for r in reaseguradoras if id_buscar.lower() in r["idreaseguradora"].lower()]

        if filtro_pais != "Todos":
            reaseguradoras = [r for r in reaseguradoras if r.get("pais") == filtro_pais]

        if reaseguradoras:
            df = pd.DataFrame(reaseguradoras)
            df_display = df.rename(columns={
                "idreaseguradora": "ID",
                "nombre": "Nombre",
                "pais": "País",
                "tipo_reaseguro": "Tipo de reaseguro",
                "email": "Email"
            })
            st.dataframe(df_display[["ID", "Nombre", "País", "Tipo de reaseguro", "Email"]], use_container_width=True)
        else:
            st.info("No hay reaseguradoras registradas.")

    # =====================================================
    # TAB 2: NUEVA REASEGURADORA
    # =====================================================
    with tab2:
        st.subheader("➕ Nueva reaseguradora")

        if not paises:
            st.warning("⚠️ No hay países registrados. Crea uno en Catálogos.")
        elif not tipos_reaseguro:
            st.warning("⚠️ No hay tipos de reaseguro registrados. Crea uno en Catálogos.")
        else:
            with st.form("form_nueva_reaseg"):
                col1, col2 = st.columns(2)

                with col1:
                    nombre = st.text_input("Nombre de la reaseguradora:")
                    email = st.text_input("Email:", placeholder="contacto@reaseguradora.com")

                with col2:
                    pais_opciones = {p["idpais"]: p["nombre"] for p in paises}
                    pais_seleccionado = st.selectbox(
                        "País de origen:",
                        options=list(pais_opciones.keys()),
                        format_func=lambda x: pais_opciones[x]
                    )

                    tipo_opciones = {t["idtiporeaseguro"]: t["nombre"] for t in tipos_reaseguro}
                    tipo_seleccionado = st.selectbox(
                        "Tipo de reaseguro:",
                        options=list(tipo_opciones.keys()),
                        format_func=lambda x: tipo_opciones[x]
                    )

                id_reaseg = st.text_input("ID (dejar vacío para auto-generar):", placeholder="Ej: RE001")

                guardar = st.form_submit_button("💾 Guardar reaseguradora", use_container_width=True)

            if guardar:
                if not nombre.strip():
                    st.error("❌ El nombre es obligatorio.")
                else:
                    try:
                        # Generar ID si está vacío
                        if not id_reaseg:
                            from db.conexionDB import Database
                            with Database() as db:
                                last_id = db.fetch_one("SELECT idreaseguradora FROM reaseguradora ORDER BY idreaseguradora DESC LIMIT 1;")
                                if last_id:
                                    num = int(last_id["idreaseguradora"].replace("RE", "")) + 1
                                    id_reaseg = f"RE{num:03d}"
                                else:
                                    id_reaseg = "RE001"

                        reaseg = Reaseguradora(
                            nombre=nombre.strip(),
                            id_pais=pais_seleccionado,
                            id_tipo_reaseguro=tipo_seleccionado,
                            email=email if email else None,
                            id_reaseguradora=id_reaseg
                        )
                        insertar_reaseguradora(reaseg)
                        st.success(f"✅ Reaseguradora {nombre} registrada correctamente con ID {id_reaseg}.")
                        st.rerun()
                    except ValueError as e:
                        st.error(f"❌ Error: {e}")
                    except Exception as e:
                        st.error(f"❌ Error inesperado: {e}")

    # =====================================================
    # TAB 3: EDITAR / ELIMINAR
    # =====================================================
    with tab3:
        st.subheader("✏️ Editar o eliminar reaseguradora")

        id_buscar = st.text_input("ID de la reaseguradora a buscar:", key="buscar_editar_rea")

        if id_buscar:
            reaseg_data = obtener_reaseguradora_por_id(id_buscar)

            if reaseg_data:
                st.success(f"✅ Reaseguradora encontrada: {reaseg_data['nombre']}")

                with st.form("form_editar_reaseg"):
                    col1, col2 = st.columns(2)

                    with col1:
                        nombre = st.text_input("Nombre:", value=reaseg_data["nombre"])
                        email = st.text_input("Email:", value=reaseg_data.get("email") or "")

                    with col2:
                        pais_opciones = {p["idpais"]: p["nombre"] for p in paises}
                        pais_actual = reaseg_data["idpais"]
                        pais_nuevo = st.selectbox(
                            "País de origen:",
                            options=list(pais_opciones.keys()),
                            format_func=lambda x: pais_opciones[x],
                            index=list(pais_opciones.keys()).index(pais_actual) if pais_actual in pais_opciones else 0
                        )

                        tipo_opciones = {t["idtiporeaseguro"]: t["nombre"] for t in tipos_reaseguro}
                        tipo_actual = reaseg_data["idtiporeaseguro"]
                        tipo_nuevo = st.selectbox(
                            "Tipo de reaseguro:",
                            options=list(tipo_opciones.keys()),
                            format_func=lambda x: tipo_opciones[x],
                            index=list(tipo_opciones.keys()).index(tipo_actual) if tipo_actual in tipo_opciones else 0
                        )

                    col_btn1, col_btn2 = st.columns(2)
                    actualizar = col_btn1.form_submit_button("🔄 Actualizar", use_container_width=True)
                    eliminar = col_btn2.form_submit_button("🗑️ Eliminar", type="secondary", use_container_width=True)

                if actualizar:
                    if not nombre.strip():
                        st.error("❌ El nombre es obligatorio.")
                    else:
                        try:
                            reaseg_edit = Reaseguradora(
                                nombre=nombre.strip(),
                                id_pais=pais_nuevo,
                                id_tipo_reaseguro=tipo_nuevo,
                                email=email if email else None,
                                id_reaseguradora=id_buscar
                            )
                            actualizar_reaseguradora(reaseg_edit)
                            st.success(f"✅ Reaseguradora {nombre} actualizada correctamente.")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"❌ Error: {e}")

                if eliminar:
                    try:
                        eliminar_reaseguradora(id_buscar)
                        st.success(f"✅ Reaseguradora {reaseg_data['nombre']} eliminada correctamente.")
                        st.rerun()
                    except ValueError as e:
                        st.error(f"❌ Error: {e}")
            else:
                st.error("❌ No se encontró una reaseguradora con ese ID.")

    # =====================================================
    # TAB 4: PARTICIPACIONES
    # =====================================================
    with tab4:
        st.subheader("📊 Participaciones por tipo de seguro")

        id_rea = st.text_input("ID de la reaseguradora:", key="partic_rea")

        if id_rea:
            reaseg_check = obtener_reaseguradora_por_id(id_rea)

            if reaseg_check:
                st.success(f"✅ Reaseguradora: {reaseg_check['nombre']}")

                # Mostrar participaciones actuales
                participaciones = listar_participaciones(id_rea)

                if participaciones:
                    st.markdown("### 📋 Participaciones actuales")
                    df = pd.DataFrame(participaciones)
                    df_display = df.rename(columns={
                        "tipo_seguro": "Tipo de seguro",
                        "porcentaje": "Porcentaje (%)"
                    })
                    st.dataframe(df_display[["Tipo de seguro", "Porcentaje (%)"]], use_container_width=True)
                else:
                    st.info("Esta reaseguradora no tiene participaciones registradas.")

                st.divider()

                # Agregar nueva participación
                st.markdown("### ➕ Agregar participación")

                if not tipos_seguro:
                    st.warning("⚠️ No hay tipos de seguro registrados. Crea uno en Catálogos.")
                else:
                    with st.form("form_participacion"):
                        col1, col2 = st.columns(2)

                        with col1:
                            tipo_opciones = {t["idtiposeguro"]: t["nombre"] for t in tipos_seguro}
                            tipo_seleccionado = st.selectbox(
                                "Tipo de seguro:",
                                options=list(tipo_opciones.keys()),
                                format_func=lambda x: tipo_opciones[x]
                            )

                        with col2:
                            porcentaje = st.number_input(
                                "Porcentaje de participación (%):",
                                min_value=0.0,
                                max_value=100.0,
                                step=0.5,
                                format="%.1f"
                            )

                        guardar_part = st.form_submit_button("💾 Guardar participación", use_container_width=True)

                    if guardar_part:
                        try:
                            agregar_participacion(id_rea, tipo_seleccionado, porcentaje)
                            st.success(f"✅ Participación de {porcentaje}% en {tipo_opciones[tipo_seleccionado]} guardada.")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"❌ Error: {e}")
            else:
                st.error("❌ No se encontró una reaseguradora con ese ID.")