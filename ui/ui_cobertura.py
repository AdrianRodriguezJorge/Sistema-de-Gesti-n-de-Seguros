import streamlit as st
import pandas as pd
from models.cobertura import Cobertura
from db.queries_cobertura import CrudCobertura

def pagina_coberturas():
    st.title('Gestion de Coberturas')
    st.divider()
    
    # Check if there is an active editing session for a coverage
    cobertura = st.session_state.get('cobertura_edit')
    
    if cobertura:
        st.subheader(f'Editar Cobertura #{cobertura.id}')
        
        # Check if confirming deletion
        confirm_del = st.session_state.get('confirming_delete_cobertura', False)
        
        if confirm_del:
            st.warning(f" Está seguro de que desea eliminar permanentemente la cobertura **#{cobertura.id}**?")
            st.write(f"Descripción: {cobertura.descripcion}")
            st.write("Esta acción podría fallar si la cobertura está vinculada a alguna póliza.")
            col_conf1, col_conf2 = st.columns(2)
            if col_conf1.button("Sí, eliminar", use_container_width=True, type="primary"):
                try:
                    CrudCobertura().eliminar(cobertura.id)
                    st.success("Cobertura eliminada exitosamente.")
                    st.session_state.cobertura_edit = None
                    st.session_state.pop('confirming_delete_cobertura', None)
                    st.session_state.editing_active = False
                    st.rerun()
                except Exception as e:
                    st.error(f'No se pudo eliminar la cobertura porque está vinculada a pólizas activas (Error de integridad). Detalle: {e}')
            if col_conf2.button("No, mantener cobertura", use_container_width=True):
                st.session_state.pop('confirming_delete_cobertura', None)
                st.rerun()
        else:
            with st.form('form_editar_cobertura_focused'):
                nueva_descripcion = st.text_area('Actualizar Descripcion', value=cobertura.descripcion)
                c1, c2, c3 = st.columns(3)
                actualizar = c1.form_submit_button('Actualizar', use_container_width=True)
                eliminar = c2.form_submit_button('Eliminar', use_container_width=True)
                cancelar = c3.form_submit_button('Cancelar', use_container_width=True)
                
                if actualizar:
                    try:
                        cobertura_actualizada = Cobertura(descripcion=nueva_descripcion, idCobertura=cobertura.id)
                        CrudCobertura().actualizar(cobertura_actualizada)
                        st.success('Cambios guardados correctamente.')
                        st.session_state.cobertura_edit = None
                        st.session_state.editing_active = False
                        st.rerun()
                    except ValueError as e:
                        st.error(f'Error: {e}')
                if eliminar:
                    st.session_state.confirming_delete_cobertura = True
                    st.rerun()
                if cancelar:
                    st.session_state.cobertura_edit = None
                    st.session_state.editing_active = False
                    st.rerun()
        return

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
                st.session_state.editing_active = True
                st.rerun()
            else:
                st.error('No se encontro la cobertura.')
                st.session_state.cobertura_edit = None