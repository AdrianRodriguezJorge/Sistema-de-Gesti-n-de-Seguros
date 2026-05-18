import streamlit as st
from models.agencia import Agencia
from db.queries_agencia import CrudAgencia

def pagina_agencia():
    st.title('Configuración de Agencia')
    st.divider()
    crud = CrudAgencia()
    try:
        agencias = crud.obtener_todos()
        agencia_registrada = agencias[0] if agencias else None
    except Exception as e:
        st.error(f'Error al conectar con la base de datos: {e}')
        return
    if agencia_registrada is None:
        st.info('No hay una agencia registrada. Complete los datos para configurar el sistema.')
        with st.form('form_crear_agencia'):
            nombre = st.text_input('Nombre de la agencia:')
            direccion = st.text_input('Dirección:')
            telefono = st.text_input('Teléfono:')
            email = st.text_input('Email:')
            directorGeneral = st.text_input('Director General:')
            jefeSeguros = st.text_input('Jefe de Seguros:')
            jefeReclamaciones = st.text_input('Jefe de Reclamaciones:')
            guardar = st.form_submit_button('Crear Agencia', use_container_width=True)
        if guardar:
            try:
                nueva_agencia_datos = Agencia(nombre=nombre, direccion=direccion, telefono=telefono, email=email, directorGeneral=directorGeneral, jefeSeguros=jefeSeguros, jefeReclamaciones=jefeReclamaciones)
                crud.crear(nueva_agencia_datos)
                st.success('Agencia creada correctamente.')
                st.rerun()
            except ValueError as e:
                st.error(f'Error de validacion: {e}')
            except Exception as e:
                st.error(f'Error inesperado: {e}')
    else:
        if not st.session_state.get('editando_agencia'):
            col1, col2 = st.columns(2)
            with col1:
                st.text(f'Nombre: {agencia_registrada.nombre}')
                st.text(f'Dirección: {agencia_registrada.direccion}')
                st.text(f'Teléfono: {agencia_registrada.telefono}')
                st.text(f'Email: {agencia_registrada.email}')
            with col2:
                st.text(f'Director General: {agencia_registrada.directorGeneral}')
                st.text(f'Jefe de Seguros: {agencia_registrada.jefeSeguros}')
                st.text(f'Jefe de Reclamaciones: {agencia_registrada.jefeReclamaciones}')
            st.divider()
            if st.button('Editar Datos', use_container_width=True):
                st.session_state.editando_agencia = True
                st.session_state.editing_active = True
                st.rerun()
        else:
            st.subheader('Editar Datos de la Agencia')
            with st.form('form_editar_agencia'):
                nombre = st.text_input('Nombre:', value=agencia_registrada.nombre)
                direccion = st.text_input('Dirección:', value=agencia_registrada.direccion)
                telefono = st.text_input('Teléfono:', value=agencia_registrada.telefono)
                email = st.text_input('Email:', value=agencia_registrada.email)
                directorGeneral = st.text_input('Director General:', value=agencia_registrada.directorGeneral)
                jefeSeguros = st.text_input('Jefe de Seguros:', value=agencia_registrada.jefeSeguros)
                jefeReclamaciones = st.text_input('Jefe de Reclamaciones:', value=agencia_registrada.jefeReclamaciones)
                col_b1, col_b2 = st.columns(2)
                actualizar = col_b1.form_submit_button('Guardar', use_container_width=True)
                cancelar = col_b2.form_submit_button('Cancelar', use_container_width=True)
            if actualizar:
                try:
                    agencia_actualizada = Agencia(nombre=nombre, direccion=direccion, telefono=telefono, email=email, directorGeneral=directorGeneral, jefeSeguros=jefeSeguros, jefeReclamaciones=jefeReclamaciones, idAgencia=agencia_registrada.id)
                    crud.actualizar(agencia_actualizada)
                    st.success('Datos actualizados correctamente.')
                    st.session_state.editando_agencia = False
                    st.session_state.editing_active = False
                    st.rerun()
                except Exception as e:
                    st.error(f'Error al actualizar: {e}')
            if cancelar:
                st.session_state.editando_agencia = False
                st.session_state.editing_active = False
                st.rerun()