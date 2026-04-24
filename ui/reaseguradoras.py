import streamlit as st
import pandas as pd

def pagina_reaseguradoras():
     st.title("🏢 Reaseguradoras")
     st.divider()
     tab1, tab2, tab3, tab4 = st.tabs(["Listado", "Nueva Reaseguradora","Editar/Eliminar", "Participaciones"])

     with tab1:
        c1, c2 = st.columns(2)
        with c1:
            id_buscar = st.text_input("Id de la reaseguradora:", key="buscar_rea")
        with c2:
            st.markdown("<br>", unsafe_allow_html=True)
            buscar = st.button("Buscar", key="btn_buscar_rea", use_container_width=True)

        columnas = ["Id", "Nombre", "País", "Tipo de reaseguro", "Email"]
        df = pd.DataFrame(columns=columnas)
        st.dataframe(df, use_container_width=True)

     with tab2:
        with st.form("form_nueva_reaseg"):
            nombre = st.text_input("Nombre:", key="nuevo_nombre_rea")
            email = st.text_input("Email:", key="nuevo_email_rea")
            pais = st.selectbox("País de origen:", ["Cuba", "México", "Colombia", "España","Argentina", "Brasil", "Panamá","Venezuela", "Perú", "Chile"],key="nuevo_pais_rea")
            tipo_reaseguro = st.selectbox("Tipo de reaseguro:",["Proporcional", "No proporcional"],key="nuevo_tipo_rea")
            guardar = st.form_submit_button("Guardar", use_container_width=True)

        if guardar:
            if not nombre:
                st.error("El nombre es obligatorio.")
            else:
                st.success(f"Reaseguradora {nombre} registrada correctamente.")

     with tab3:
        c1, c2 = st.columns(2)
        with c1:
            id_buscar = st.text_input("Id de la reaseguradora:", key="buscar_editar_rea")
        with c2:
            st.markdown("<br>", unsafe_allow_html=True)
            buscar = st.button("Buscar", key="btn_buscar_editar_rea", use_container_width=True)

        with st.form("form_editar_reaseg"):
            nombre = st.text_input("Nombre:", key="edit_nombre_rea")
            email = st.text_input("Email:", key="edit_email_rea")
            pais = st.selectbox("País de origen:", ["Cuba", "México", "Colombia", "España","Argentina", "Brasil", "Panamá","Venezuela", "Perú", "Chile"],key="edit_pais_rea")
            tipo_reaseguro = st.selectbox("Tipo de reaseguro:",["Proporcional", "No proporcional"],key="edit_tipo_rea")

            col1, col2 = st.columns(2)
            with col1:
                actualizar = st.form_submit_button("Actualizar",use_container_width=True)
            with col2:
                eliminar = st.form_submit_button("Eliminar",use_container_width=True)

        if actualizar:
            st.success(f"Reaseguradora {nombre} actualizada correctamente.")
        if eliminar:
            st.warning(f"Reaseguradora {nombre} eliminada.")

     with tab4:
        c1, c2 = st.columns(2)
        with c1:
            id_rea = st.text_input("Id de la reaseguradora:", key="partic_rea")
        with c2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("Buscar", key="btn_partic_rea", use_container_width=True)

        columnas = ["Tipo de seguro", "Porcentaje (%)"]
        df = pd.DataFrame(columns=columnas)
        st.dataframe(df, use_container_width=True)

        st.divider()
        with st.form("form_participacion"):
            c1, c2 = st.columns(2)
            tipo_seg = c1.selectbox("Tipo de seguro:", ["Vida", "Hogar", "Auto", "Salud"])
            porcentaje = c2.number_input("Porcentaje (%):", min_value=0.0,max_value=100.0, step=0.5)
            st.form_submit_button("Guardar participación", use_container_width=True)

