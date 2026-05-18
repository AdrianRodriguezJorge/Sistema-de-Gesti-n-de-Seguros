import streamlit as st
import pandas as pd
from models.reaseguradora import Reaseguradora
from models.participacion_reaseguro import ParticipacionReaseguro
from db.queries_reaseguradora import CrudReaseguradora
from db.queries_participacion_reaseguro import CrudParticipacionReaseguro
from db.queries_catalogos import CrudPais, CrudTipoReaseguro, CrudTipoSeguro
from db.conexionDB import Database

def _cargar_mapeos():
    paises = CrudPais().obtener_todos()
    tipos_reaseguro = CrudTipoReaseguro().obtener_todos()
    tipos_seguro = CrudTipoSeguro().obtener_todos()
    return {'p_n_id': {p.nombre: p.id for p in paises}, 'p_id_n': {p.id: p.nombre for p in paises}, 'tr_n_id': {t.nombre: t.id for t in tipos_reaseguro}, 'tr_id_n': {t.id: t.nombre for t in tipos_reaseguro}, 'ts_n_id': {s.nombre: s.id for s in tipos_seguro}, 'ts_id_n': {s.id: s.nombre for s in tipos_seguro}}

def pagina_reaseguradoras():
    st.title('Gestión de Reaseguradoras')
    mapeos = _cargar_mapeos()
    crud_rea = CrudReaseguradora()
    
    # Check if there is an active editing session
    edit_id = st.session_state.get('editing_rea_id')
    
    if edit_id:
        reaseguradora_seleccionada = crud_rea.obtener(edit_id)
        if not reaseguradora_seleccionada:
            st.error("La reaseguradora seleccionada no existe.")
            st.session_state.pop('editing_rea_id', None)
            st.session_state.editing_active = False
            st.rerun()
            
        st.subheader(f'Editar Reaseguradora: {reaseguradora_seleccionada.nombre}')
        
        # Check if we are confirming deletion
        confirm_del = st.session_state.get('confirming_delete_rea', False)
        
        if confirm_del:
            st.warning(f" Está seguro de que desea eliminar permanentemente la reaseguradora **{reaseguradora_seleccionada.nombre}**?")
            st.write("Esta acción es irreversible y eliminará todos los registros y participaciones asociados.")
            col_conf1, col_conf2 = st.columns(2)
            if col_conf1.button("Sí, eliminar permanentemente", use_container_width=True, type="primary"):
                try:
                    crud_rea.eliminar(reaseguradora_seleccionada)
                    st.success("Reaseguradora y participaciones eliminadas.")
                    st.session_state.pop('editing_rea_id', None)
                    st.session_state.pop('confirming_delete_rea', None)
                    st.session_state.editing_active = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar: {e}")
            if col_conf2.button("No, mantener registro", use_container_width=True):
                st.session_state.pop('confirming_delete_rea', None)
                st.rerun()
        else:
            with st.form('form_edit_rea_focused'):
                nuevo_nombre = st.text_input('Nombre', value=reaseguradora_seleccionada.nombre)
                nombre_pais_actual = mapeos['p_id_n'].get(reaseguradora_seleccionada.idPais)
                nuevo_pais = st.selectbox('País', list(mapeos['p_n_id'].keys()), index=list(mapeos['p_n_id'].keys()).index(nombre_pais_actual))
                nombre_tipo_actual = mapeos['tr_id_n'].get(reaseguradora_seleccionada.idTipoReaseguro)
                nuevo_tipo = st.selectbox('Tipo Reaseguro', list(mapeos['tr_n_id'].keys()), index=list(mapeos['tr_n_id'].keys()).index(nombre_tipo_actual))
                
                c1, c2, c3 = st.columns(3)
                btn_upd = c1.form_submit_button('Actualizar', use_container_width=True)
                btn_del = c2.form_submit_button('Eliminar', use_container_width=True)
                btn_can = c3.form_submit_button('Cancelar', use_container_width=True)
                
                if btn_upd:
                    lista_busqueda = crud_rea.obtener_todos()
                    nombres_otros = [r.nombre.strip().lower() for r in lista_busqueda if r.id != reaseguradora_seleccionada.id]
                    if nuevo_nombre.strip().lower() in nombres_otros:
                        st.error('Ya existe otra reaseguradora con este nombre.')
                    else:
                        try:
                            upd_obj = Reaseguradora(nuevo_nombre, mapeos['p_n_id'][nuevo_pais], mapeos['tr_n_id'][nuevo_tipo], reaseguradora_seleccionada.id)
                            crud_rea.actualizar(upd_obj)
                            st.success('Actualizada')
                            st.session_state.pop('editing_rea_id', None)
                            st.session_state.editing_active = False
                            st.rerun()
                        except Exception as e:
                            st.error(f'Error al actualizar: {e}')
                if btn_del:
                    st.session_state.confirming_delete_rea = True
                    st.rerun()
                if btn_can:
                    st.session_state.pop('editing_rea_id', None)
                    st.session_state.editing_active = False
                    st.rerun()
        return

    tab1, tab2, tab3, tab4 = st.tabs(['Listado', 'Nueva Reaseguradora', 'Editar / Eliminar', 'Participaciones'])
    with tab1:
        st.subheader('Listado General de Reaseguradoras')
        try:
            lista_reaseguradoras = CrudReaseguradora().obtener_todos()
            lista_participaciones = CrudParticipacionReaseguro().obtener_todos()
            if lista_reaseguradoras:
                datos_reporte = []
                for r in lista_reaseguradoras:
                    participaciones_asociadas = [f"{mapeos['ts_id_n'].get(p.idTipoSeguro)} ({p.porcentaje}%)" for p in lista_participaciones if p.idReaseguradora == r.id]
                    datos_reporte.append({'ID': r.id, 'Nombre': r.nombre, 'País': mapeos['p_id_n'].get(r.idPais, 'N/A'), 'Tipo Reaseguro': mapeos['tr_id_n'].get(r.idTipoReaseguro, 'N/A'), 'Participaciones (%)': ', '.join(participaciones_asociadas) if participaciones_asociadas else 'Sin participaciones'})
                st.dataframe(pd.DataFrame(datos_reporte), use_container_width=True, hide_index=True)
            else:
                st.info('No hay reaseguradoras registradas.')
        except Exception as e:
            st.error(f'Error: {e}')
    with tab2:
        with st.form('form_nueva_rea'):
            nombre = st.text_input('Nombre')
            pais_sel = st.selectbox('País', list(mapeos['p_n_id'].keys()))
            tipo_sel = st.selectbox('Tipo de Reaseguro', list(mapeos['tr_n_id'].keys()))
            if st.form_submit_button('Añadir', use_container_width=True):
                if nombre:
                    todas_reas = CrudReaseguradora().obtener_todos()
                    nombres_existentes = [r.nombre.strip().lower() for r in todas_reas] if todas_reas else []
                    if nombre.strip().lower() in nombres_existentes:
                        st.error(f"Ya existe una reaseguradora con el nombre '{nombre}'.")
                    else:
                        nueva = Reaseguradora(nombre, mapeos['p_n_id'][pais_sel], mapeos['tr_n_id'][tipo_sel])
                        CrudReaseguradora().crear(nueva)
                        st.success('Añadida')
                        st.rerun()
    with tab3:
        lista_busqueda = CrudReaseguradora().obtener_todos()
        if not lista_busqueda:
            st.info('No hay reaseguradoras registradas para editar o eliminar.')
        else:
            opciones_rea = {r.nombre: r for r in lista_busqueda}
            seleccion = st.selectbox('Seleccione una reaseguradora para editar o eliminar:', list(opciones_rea.keys()))
            reaseguradora_seleccionada = opciones_rea[seleccion]
            st.markdown("### Detalles de la Reaseguradora")
            r_d1, r_d2 = st.columns(2)
            r_d1.markdown(f"**Nombre:** {reaseguradora_seleccionada.nombre}")
            r_d1.markdown(f"**País:** {mapeos['p_id_n'].get(reaseguradora_seleccionada.idPais, 'N/A')}")
            r_d2.markdown(f"**Tipo Reaseguro:** {mapeos['tr_id_n'].get(reaseguradora_seleccionada.idTipoReaseguro, 'N/A')}")
            
            if st.button(" Iniciar Edición / Eliminación", use_container_width=True, type="primary"):
                st.session_state.editing_rea_id = reaseguradora_seleccionada.id
                st.session_state.editing_active = True
                st.rerun()
    with tab4:
        lista_participaciones_rea = CrudReaseguradora().obtener_todos()
        if not lista_participaciones_rea:
            st.info('No hay reaseguradoras registradas para gestionar participaciones.')
        else:
            reaseguradora_participaciones = st.selectbox('Seleccione una reaseguradora para ver sus participaciones:', lista_participaciones_rea, format_func=lambda x: x.nombre)
            st.write(f'Participaciones actuales de **{reaseguradora_participaciones.nombre}**:')
            mis_participaciones = CrudParticipacionReaseguro().filtrar(idReaseguradora=reaseguradora_participaciones.id)
            if mis_participaciones:
                for p in mis_participaciones:
                    with st.expander(f"{mapeos['ts_id_n'].get(p.idTipoSeguro)} - {p.porcentaje}%"):
                        confirm_del_key = f'confirm_del_part_{p.idReaseguradora}_{p.idTipoSeguro}'
                        if st.session_state.get(confirm_del_key):
                            st.warning(" Eliminar participación?")
                            c_col1, c_col2 = st.columns(2)
                            if c_col1.button("Sí, eliminar", key=f"yes_del_{p.idReaseguradora}_{p.idTipoSeguro}", use_container_width=True, type="primary"):
                                sql_del = 'DELETE FROM participacion_reaseguro WHERE idreaseguradora = %s AND idtiposeguro = %s'
                                with Database() as db:
                                    db.execute(sql_del, (p.idReaseguradora, p.idTipoSeguro))
                                st.session_state.pop(confirm_del_key, None)
                                st.rerun()
                            if c_col2.button("No, cancelar", key=f"no_del_{p.idReaseguradora}_{p.idTipoSeguro}", use_container_width=True):
                                st.session_state.pop(confirm_del_key, None)
                                st.rerun()
                        else:
                            with st.form(f'edit_part_{p.idTipoSeguro}'):
                                nuevo_porc = st.number_input('Porcentaje (%)', 0.0, 100.0, float(p.porcentaje))
                                btn_upd, btn_del = st.columns(2)
                                if btn_upd.form_submit_button('Actualizar', use_container_width=True):
                                    p.porcentaje = nuevo_porc
                                    CrudParticipacionReaseguro().actualizar(p)
                                    st.rerun()
                                if btn_del.form_submit_button('Eliminar', use_container_width=True):
                                    st.session_state[confirm_del_key] = True
                                    st.rerun()
            else:
                st.caption('No tiene participaciones asignadas aún.')
            st.divider()
            st.text('Rellene el formulario para añadir una nueva participación a la reaseguradora seleccionada:')
            with st.form('new_p'):
                tipo_seguro_sel = st.selectbox('Seguro', list(mapeos['ts_n_id'].keys()))
                porcentaje_sel = st.number_input('Porcentaje (%)', 0.0, 100.0)
                if st.form_submit_button('Añadir'):
                    obj_p = ParticipacionReaseguro(reaseguradora_participaciones.id, mapeos['ts_n_id'][tipo_seguro_sel], porcentaje_sel)
                    CrudParticipacionReaseguro().crear(obj_p)
                    st.rerun()