# ui/ui_catalogos.py

import streamlit as st
import pandas as pd
from models.catalogos import Pais, TipoSeguro, EstadoPoliza, TipoSiniestro, EstadoReclamacion, TipoReaseguro
from db.queries_catalogos import CrudPais, CrudTipoSeguro, CrudEstadoPoliza, CrudTipoSiniestro, CrudEstadoReclamacion, CrudTipoReaseguro
from db.conexionDB import Database

def _seccion_catalogo(label, clase, crud, nombre_tabla):
    st.subheader(f'Listado de {label}')
    try:
        lista_registros = crud.obtener_todos()
        if lista_registros:
            df = pd.DataFrame([{'ID': r.id, 'Nombre': r.nombre} for r in lista_registros])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info(f'No hay registros en {label}.')
    except Exception as e:
        st.error(f'Error al cargar listado: {e}')
    st.divider()
    tab_nueva, tab_editar = st.tabs([f'Nuevo {label}', f'Editar / Eliminar {label}'])
    with tab_nueva:
        with st.form(f"form_nuevo_{label.replace(' ', '_').lower()}"):
            nombre_registro = st.text_input('Nombre')
            guardar = st.form_submit_button('Guardar Registro', use_container_width=True)
        if guardar:
            if any((char.isdigit() for char in nombre_registro)):
                st.error('El nombre no puede contener números.')
            elif not nombre_registro.strip():
                st.error('El nombre es obligatorio.')
            else:
                try:
                    todos_registros = crud.obtener_todos()
                    nombres_existentes = [r.nombre.strip().lower() for r in todos_registros] if todos_registros else []
                    if nombre_registro.strip().lower() in nombres_existentes:
                        st.error(f"El valor '{nombre_registro}' ya está registrado.")
                    else:
                        obj = clase(nombre=nombre_registro)
                        crud.crear(obj)
                        st.success(f'{label} guardado correctamente.')
                        st.rerun()
                except ValueError as e:
                    st.error(f'Error de validación: {e}')
                except Exception as e:
                    st.error(f'Error inesperado: {e}')
    with tab_editar:
        lista_registros_modificacion = crud.obtener_todos()
        if not lista_registros_modificacion:
            st.info(f'No hay registros de {label} para editar o eliminar.')
        else:
            opciones_modificacion = {r.nombre: r for r in lista_registros_modificacion}
            seleccion_modificacion = st.selectbox(f'Seleccione {label} a modificar:', list(opciones_modificacion.keys()), key=f'sel_{label}')
            registro_seleccionado = opciones_modificacion[seleccion_modificacion]
            
            st.markdown(f"**Registro Seleccionado:** ID: {registro_seleccionado.id} | Nombre: {registro_seleccionado.nombre}")
            if st.button(f" Editar / Eliminar {label}", key=f"btn_edit_act_{nombre_tabla}", use_container_width=True, type="primary"):
                st.session_state[f'editing_{nombre_tabla}_id'] = registro_seleccionado.id
                st.session_state.editing_active = True
                st.rerun()

def pagina_catalogos():
    st.title('Gestión de Catálogos')
    
    # Check if there is an active catalog editing session
    active_edit = None
    catalogs_info = [
        ('País', Pais, CrudPais(), 'pais'),
        ('Tipo de Seguro', TipoSeguro, CrudTipoSeguro(), 'tipo_seguro'),
        ('Estado de Póliza', EstadoPoliza, CrudEstadoPoliza(), 'estado_poliza'),
        ('Tipo de Siniestro', TipoSiniestro, CrudTipoSiniestro(), 'tipo_siniestro'),
        ('Estado de Reclamación', EstadoReclamacion, CrudEstadoReclamacion(), 'estado_reclamacion'),
        ('Tipo de Reaseguro', TipoReaseguro, CrudTipoReaseguro(), 'tipo_reaseguro')
    ]
    
    for label, clase, crud, nombre_tabla in catalogs_info:
        if st.session_state.get(f'editing_{nombre_tabla}_id'):
            active_edit = (label, clase, crud, nombre_tabla)
            break
            
    if active_edit:
        label, clase, crud, nombre_tabla = active_edit
        edit_id = st.session_state.get(f'editing_{nombre_tabla}_id')
        registro_seleccionado = crud.obtener(edit_id)
        if not registro_seleccionado:
            st.error("El registro seleccionado no existe.")
            st.session_state.pop(f'editing_{nombre_tabla}_id', None)
            st.session_state.editing_active = False
            st.rerun()
            
        st.subheader(f'Editar {label}: {registro_seleccionado.nombre}')
        
        # Check if confirming deletion
        confirm_del = st.session_state.get(f'confirming_delete_{nombre_tabla}', False)
        
        if confirm_del:
            st.warning(f" Está seguro de que desea eliminar permanentemente el registro **{registro_seleccionado.nombre}** de {label}?")
            st.write("Esta acción podría fallar si el registro está siendo referenciado por otras partes del sistema.")
            col_conf1, col_conf2 = st.columns(2)
            if col_conf1.button("Sí, eliminar", use_container_width=True, type="primary"):
                try:
                    pk_col = f"id{nombre_tabla.replace('_', '')}"
                    sql_del = f'DELETE FROM {nombre_tabla} WHERE {pk_col} = %s'
                    with Database() as db:
                        db.execute(sql_del, (registro_seleccionado.id,))
                    st.success("Registro eliminado exitosamente.")
                    st.session_state.pop(f'editing_{nombre_tabla}_id', None)
                    st.session_state.pop(f'confirming_delete_{nombre_tabla}', None)
                    st.session_state.editing_active = False
                    st.rerun()
                except Exception as e:
                    st.error(f'No se puede eliminar el registro porque está siendo usado en otras partes del sistema (Error de integridad). Detalle: {e}')
            if col_conf2.button("No, mantener registro", use_container_width=True):
                st.session_state.pop(f'confirming_delete_{nombre_tabla}', None)
                st.rerun()
        else:
            with st.form(f"form_edit_{nombre_tabla}_focused"):
                nuevo_nombre = st.text_input('Nuevo Nombre', value=registro_seleccionado.nombre)
                c1, c2, c3 = st.columns(3)
                btn_actualizar = c1.form_submit_button('Actualizar', use_container_width=True)
                btn_eliminar = c2.form_submit_button('Eliminar', use_container_width=True)
                btn_cancelar = c3.form_submit_button('Cancelar', use_container_width=True)
                
                if btn_actualizar:
                    if any((char.isdigit() for char in nuevo_nombre)):
                        st.error('El nombre no puede contener números.')
                    elif not nuevo_nombre.strip():
                        st.error('El nombre es obligatorio.')
                    else:
                        try:
                            lista_registros = crud.obtener_todos()
                            otros_nombres = [r.nombre.strip().lower() for r in lista_registros if r.id != registro_seleccionado.id]
                            if nuevo_nombre.strip().lower() in otros_nombres:
                                st.error('Ya existe otro registro con este nombre.')
                            else:
                                registro_seleccionado.nombre = nuevo_nombre
                                crud.actualizar(registro_seleccionado)
                                st.success('Registro actualizado.')
                                st.session_state.pop(f'editing_{nombre_tabla}_id', None)
                                st.session_state.editing_active = False
                                st.rerun()
                        except Exception as e:
                            st.error(f'Error al actualizar: {e}')
                if btn_eliminar:
                    st.session_state[f'confirming_delete_{nombre_tabla}'] = True
                    st.rerun()
                if btn_cancelar:
                    st.session_state.pop(f'editing_{nombre_tabla}_id', None)
                    st.session_state.editing_active = False
                    st.rerun()
        return

    tabs = st.tabs(['Países', 'Tipos de Seguro', 'Estados de Póliza', 'Tipos de Siniestro', 'Estados de Reclamación', 'Tipos de Reaseguro'])
    with tabs[0]:
        _seccion_catalogo('País', Pais, CrudPais(), 'pais')
    with tabs[1]:
        _seccion_catalogo('Tipo de Seguro', TipoSeguro, CrudTipoSeguro(), 'tipo_seguro')
    with tabs[2]:
        _seccion_catalogo('Estado de Póliza', EstadoPoliza, CrudEstadoPoliza(), 'estado_poliza')
    with tabs[3]:
        _seccion_catalogo('Tipo de Siniestro', TipoSiniestro, CrudTipoSiniestro(), 'tipo_siniestro')
    with tabs[4]:
        _seccion_catalogo('Estado de Reclamación', EstadoReclamacion, CrudEstadoReclamacion(), 'estado_reclamacion')
    with tabs[5]:
        _seccion_catalogo('Tipo de Reaseguro', TipoReaseguro, CrudTipoReaseguro(), 'tipo_reaseguro')
