import streamlit as st
import pandas as pd

def pagina_polizas():
    st.title("📋 Pólizas")
    st.divider()
    tab1, tab2, tab3, tab4 = st.tabs(["Listado", "Nueva Póliza", "Editar/Estado", "Coberturas"])

    with tab1:
        c1, c2, c3 = st.columns([3, 2, 2])
        with c1:
            id_buscar = st.text_input("Id de la Póliza:", key="buscar_listado")
        with c2:
            filtro_tipo = st.selectbox("Tipo de seguro:", ["Todos", "Vida", "Hogar", "Auto", "Salud"],key="ftipo_pol")
        with c3:
            filtro_estado = st.selectbox("Estado:", ["Todos", "Activa", "Vencida", "Cancelada"],key="festado_pol")
        columnas = ["Id", "Cliente", "Tipo de seguro", "Fecha inicio","Fecha fin", "Prima mensual", "Monto asegurado", "Estado"]
        df = pd.DataFrame(columns=columnas)
        st.dataframe(df, use_container_width=True)

    with tab2:
        with st.form("form_añadir_poliza"):
            cliente = st.selectbox("Cliente:", [" "])
            tipo_seguro = st.selectbox("Tipo de seguro:", ["Vida", "Hogar", "Auto", "Salud"])
            fecha_inicio = st.date_input("Fecha inicio:")
            fecha_fin = st.date_input("Fecha fin:")
            prima_mensual = st.number_input("Prima mensual ($):", min_value=0.01, step=0.01)
            monto_asegurado = st.number_input("Monto asegurado ($):", min_value=0.01, step=100.0)
            estado = st.selectbox("Estado inicial:", ["Activa", "Vencida", "Cancelada"])
            guardar = st.form_submit_button("Guardar", use_container_width=True )

        if guardar:
            if cliente == " ":
                st.error("Debes seleccionar un cliente.")
            elif fecha_fin <= fecha_inicio:
                st.error("La fecha de fin debe ser posterior a la fecha de inicio.")
            else:
                st.success("Póliza registrada correctamente.")

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            id_buscar = st.text_input("Id de la póliza:", key="buscar_editar_pol")
        with c2:
            st.markdown("<br>", unsafe_allow_html=True)
            buscar = st.button("Buscar", key="btn_buscar_editar_pol", use_container_width=True)

        col_edit, col_estado = st.columns(2)

        with col_edit:
            with st.form("form_editar_poliza"):
                cliente = st.selectbox("Cliente:", [" "])
                tipo_seguro = st.selectbox("Tipo de seguro:", ["Vida", "Hogar", "Auto", "Salud"])
                fecha_inicio = st.date_input("Fecha inicio:")
                fecha_fin = st.date_input("Fecha fin:")
                prima_mensual = st.number_input("Prima mensual ($):", min_value=0.01, step=0.01)
                monto_asegurado = st.number_input("Monto asegurado ($):", min_value=0.01, step=100.0)
                actualizar = st.form_submit_button("Actualizar",use_container_width=True)
            if actualizar:
                st.success("Póliza actualizada correctamente.")

        with col_estado:
            with st.form("form_estado_poliza"):
                nuevo_estado = st.selectbox("Nuevo estado:", ["Activa", "Vencida", "Cancelada"])
                motivo = st.text_area("Motivo (requerido si cancela):", height=80)
                aplicar = st.form_submit_button("Aplicar cambio", use_container_width=True)
            if aplicar:
                st.success(f"Estado cambiado a {nuevo_estado}.")

            st.divider()
            if st.button("Eliminar esta póliza", type="secondary", use_container_width=True):
                st.warning("Póliza eliminada.")

    with tab4:
        c1, c2 = st.columns(2)
        with c1:
            id_pol_cob = st.text_input("Id de la póliza:", key="cob_pol")
        with c2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("Buscar", key="btn_cob_pol", use_container_width=True)

        coberturas = []
        if coberturas:
            for cob in coberturas:
                c1, c2 = st.columns([5, 1])
                c1.write(f"{cob['nombre']} — {cob['descripcion']}")
                c2.button("Quitar", key=f"del_{cob['nombre']}", use_container_width=True)
        else:
            st.caption("Esta póliza no tiene coberturas registradas.")

        st.divider()
        with st.form("form_cobertura"):
            c1, c2 = st.columns(2)
            nombre_cob = c1.text_input("Nombre de la cobertura:")
            desc_cob = c2.text_input("Descripción:")
            st.form_submit_button("Agregar", use_container_width=True)