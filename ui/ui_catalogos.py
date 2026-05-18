# ui/ui_catalogos.py

import streamlit as st
import pandas as pd
from data.class_catalogos import Pais, TipoSeguro, EstadoPoliza, TipoSiniestro, EstadoReclamacion, TipoReaseguro
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
            with st.form(f"form_edit_{label.replace(' ', '_').lower()}"):
                nuevo_nombre = st.text_input('Nuevo Nombre', value=registro_seleccionado.nombre)
                c1, c2 = st.columns(2)
                btn_actualizar = c1.form_submit_button('Actualizar', use_container_width=True)
                btn_eliminar = c2.form_submit_button('Eliminar', use_container_width=True)
                if btn_actualizar:
                    if any((char.isdigit() for char in nuevo_nombre)):
                        st.error('El nombre no puede contener números.')
                    elif not nuevo_nombre.strip():
                        st.error('El nombre es obligatorio.')
                    else:
                        try:
                            otros_nombres = [r.nombre.strip().lower() for r in lista_registros_modificacion if r.id != registro_seleccionado.id]
                            if nuevo_nombre.strip().lower() in otros_nombres:
                                st.error('Ya existe otro registro con este nombre.')
                            else:
                                registro_seleccionado.nombre = nuevo_nombre
                                crud.actualizar(registro_seleccionado)
                                st.success('Registro actualizado.')
                                st.rerun()
                        except Exception as e:
                            st.error(f'Error al actualizar: {e}')
                if btn_eliminar:
                    try:
                        pk_col = f"id{nombre_tabla.replace('_', '')}"
                        sql_del = f'DELETE FROM {nombre_tabla} WHERE {pk_col} = %s'
                        with Database() as db:
                            db.execute(sql_del, (registro_seleccionado.id,))
                        st.warning('Registro eliminado exitosamente.')
                        st.rerun()
                    except Exception as e:
                        st.error(f'No se puede eliminar el registro porque está siendo usado en otras partes del sistema (Error de integridad). Detalle: {e}')

def pagina_catalogos():
    st.title('Gestión de Catálogos')
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
