import streamlit as st
import pandas as pd
from data.class_cobertura import Cobertura
from db.queries_cobertura import CrudCobertura

def pagina_coberturas():
    st.title('Gestion de Coberturas')
    st.divider()
    if 'cobertura_edit' not in st.session_state:
        st.session_state.cobertura_edit = None
    tab1, tab2, tab3 = st.tabs(['Listado', 'Nueva Cobertura', 'Editar / Eliminar'])
    with tab1:
        st.subheader('Coberturas Disponibles')
        try:
            lista_coberturas = CrudCobertura().obtener_todos()
            if lista_coberturas:
                filas = [{'ID': c.id, 'Descripcion': c.descripcion} for c in lista_coberturas]
                st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)
            else:
                st.info('No hay coberturas registradas.')
        except Exception as e:
            st.error(f'Error al cargar listado: {e}')
    with tab2:
        st.subheader('Registrar Nueva Cobertura')
        with st.form('form_nueva_cobertura'):
            descripcion = st.text_area('Descripcion de la Cobertura', help='Maximo 200 caracteres')
            guardar = st.form_submit_button('Guardar Cobertura', use_container_width=True)
        if guardar:
            try:
                nueva_cobertura_datos = Cobertura(descripcion=descripcion)
                nuevo_id = CrudCobertura().crear(nueva_cobertura_datos)
                st.success(f'Cobertura #{nuevo_id} registrada con exito.')
                st.rerun()
            except ValueError as e:
                st.error(f'Error de validacion: {e}')
            except Exception as e:
                st.error(f'Error inesperado: {e}')
    with tab3:
        st.subheader('Mantenimiento de Coberturas')
        c1, c2 = st.columns([3, 1])
        identificador_busqueda = c1.number_input('ID de Cobertura', min_value=1, step=1)
        if c2.button('Buscar', use_container_width=True):
            resultado_busqueda = CrudCobertura().obtener(identificador_busqueda)
            if resultado_busqueda:
                st.session_state.cobertura_edit = resultado_busqueda
            else:
                st.error('No se encontro la cobertura.')
                st.session_state.cobertura_edit = None
        if st.session_state.cobertura_edit:
            cobertura = st.session_state.cobertura_edit
            st.info(f'Editando Cobertura #{cobertura.id}')
            with st.form('form_editar_cobertura'):
                nueva_descripcion = st.text_area('Actualizar Descripcion', value=cobertura.descripcion)
                col1, col2 = st.columns(2)
                actualizar = col1.form_submit_button('Actualizar', use_container_width=True)
                eliminar = col2.form_submit_button('Eliminar', use_container_width=True)
            if actualizar:
                try:
                    cobertura_actualizada = Cobertura(descripcion=nueva_descripcion, idCobertura=cobertura.id)
                    CrudCobertura().actualizar(cobertura_actualizada)
                    st.success('Cambios guardados correctamente.')
                    st.session_state.cobertura_edit = None
                    st.rerun()
                except ValueError as e:
                    st.error(f'Error: {e}')
            if eliminar:
                try:
                    CrudCobertura().eliminar(cobertura.id)
                    st.warning('Cobertura eliminada.')
                    st.session_state.cobertura_edit = None
                    st.rerun()
                except Exception as e:
                    st.error(f'No se pudo eliminar: {e}')