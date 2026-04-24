import streamlit as st
import pandas as pd

def pagina_reclamaciones():
    st.title("📝 Reclamaciones")
    st.divider()
    tab1, tab2, tab3 = st.tabs(["Listado", "Nueva Reclamación", "Editar/Estado"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            id_buscar = st.text_input("Id de la reclamación:", key="buscar_rec")
        with c2:
            filtro_estado = st.selectbox("Estado:", ["Todos", "En proceso", "Aprobada", "Rechazada"],key="festado_rec")

        columnas = ["Id", "Cliente", "Póliza", "Tipo de seguro", "Tipo siniestro","Fecha siniestro", "Monto reclamado", "Monto indemnizado", "Estado"]
        df = pd.DataFrame(columns=columnas)
        st.dataframe(df, use_container_width=True)

    with tab2:
        with st.form("form_nueva_reclamacion"):
            poliza = st.selectbox("Póliza:", [" "])
            tipo_siniestro = st.selectbox("Tipo de siniestro:",["Accidente", "Enfermedad", "Desastre natural","Robo", "Incendio", "Fallecimiento"])
            fecha_siniestro = st.date_input("Fecha del siniestro:")
            monto_reclamado = st.number_input("Monto reclamado ($):", min_value=0.01, step=0.01)
            monto_indemnizado = st.number_input("Monto indemnizado ($):", min_value=0.0, step=0.01)
            estado = st.selectbox("Estado:", ["En proceso", "Aprobada", "Rechazada"])
            guardar = st.form_submit_button("Guardar", use_container_width=True)

        if guardar:
            if poliza == " ":
                st.error("Debes seleccionar una póliza.")
            else:
                st.success("Reclamación registrada correctamente.")

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            id_buscar = st.text_input("Id de la reclamación:", key="buscar_editar_rec")
        with c2:
            st.markdown("<br>", unsafe_allow_html=True)
            buscar = st.button("Buscar", key="btn_buscar_editar_rec", use_container_width=True)

        col_edit, col_estado = st.columns(2)

        with col_edit:
            with st.form("form_editar_reclamacion"):
                tipo_siniestro = st.selectbox("Tipo de siniestro:",["Accidente", "Enfermedad", "Desastre natural","Robo", "Incendio", "Fallecimiento"])
                fecha_siniestro = st.date_input("Fecha del siniestro:")
                monto_reclamado = st.number_input("Monto reclamado ($):", min_value=0.01, step=0.01)
                monto_indemnizado = st.number_input("Monto indemnizado ($):", min_value=0.0, step=0.01)
                actualizar = st.form_submit_button("Actualizar", use_container_width=True)
            if actualizar:
                st.success("Reclamación actualizada correctamente.")

        with col_estado:
            with st.form("form_estado_reclamacion"):
                nuevo_estado = st.selectbox("Nuevo estado:", ["En proceso", "Aprobada", "Rechazada"])
                motivo = st.text_area("Motivo de rechazo (si aplica):", height=80)
                aplicar = st.form_submit_button("Aplicar cambio", use_container_width=True)
            if aplicar:
                st.success(f"Estado cambiado a {nuevo_estado}.")

            st.divider()
            if st.button("Eliminar esta reclamación",use_container_width=True):
                st.warning("Reclamación eliminada.")