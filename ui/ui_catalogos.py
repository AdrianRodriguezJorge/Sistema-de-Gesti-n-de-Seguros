# ui/ui_catalogos.py

import streamlit as st
import pandas as pd
from data.class_catalogos import Pais, TipoSeguro, EstadoPoliza, TipoSiniestro, EstadoReclamacion, TipoReaseguro
from db.queries_catalogos import CrudPais, CrudTipoSeguro, CrudEstadoPoliza, CrudTipoSiniestro, CrudEstadoReclamacion, CrudTipoReaseguro
from db.conexionDB import Database

<<<<<<< HEAD
from data.class_catalogos import (
    Pais, TipoSeguro, EstadoPoliza,
    TipoSiniestro, EstadoReclamacion, TipoReaseguro
)
from data.class_cobertura import Cobertura 

from db.queries_catalogos import (
    insertar_pais, listar_paises, obtener_pais_por_id, actualizar_pais, eliminar_pais,
    insertar_tipo_seguro, listar_tipos_seguro, obtener_tipo_seguro_por_id, actualizar_tipo_seguro, eliminar_tipo_seguro,
    insertar_estado_poliza, listar_estados_poliza, obtener_estado_poliza_por_id, actualizar_estado_poliza, eliminar_estado_poliza,
    insertar_tipo_siniestro, listar_tipos_siniestro, obtener_tipo_siniestro_por_id, actualizar_tipo_siniestro, eliminar_tipo_siniestro,
    insertar_estado_reclamacion, listar_estados_reclamacion, obtener_estado_reclamacion_por_id, actualizar_estado_reclamacion, eliminar_estado_reclamacion,
    insertar_tipo_reaseguro, listar_tipos_reaseguro, obtener_tipo_reaseguro_por_id, actualizar_tipo_reaseguro, eliminar_tipo_reaseguro,
)
from db.queries_cobertura import ( 
    insertar_cobertura, listar_coberturas, obtener_cobertura_por_id,
    actualizar_cobertura, eliminar_cobertura
)


def _seccion_catalogo(label, clase, fn_listar, fn_insertar, fn_obtener, fn_actualizar, fn_eliminar, col_id):
    """Renderiza listado, nuevo registro y editar/eliminar para un catálogo usando session_state."""

    key_encontrado = f"cat_{col_id}_encontrado"
    key_eliminado = f"cat_{col_id}_eliminado"

    if key_encontrado not in st.session_state:
        st.session_state[key_encontrado] = None
    if key_eliminado not in st.session_state:
        st.session_state[key_eliminado] = False

    # Listado
    st.subheader(f"📋 Listado de {label}")
    registros = fn_listar()
    if registros:
        st.dataframe(pd.DataFrame(registros), use_container_width=True)
    else:
        st.info(f"No hay registros en {label}.")

    st.divider()

    # Nuevo registro
    st.subheader(f"➕ Nuevo {label}")
    with st.form(f"form_nuevo_{col_id}"):
        nombre_nuevo = st.text_input("Nombre:" if label != "Cobertura" else "Descripción:")
        guardar = st.form_submit_button("Guardar", use_container_width=True)

    if guardar:
        try:
            if label == "Cobertura":
                obj = clase(descripcion=nombre_nuevo)  # Cobertura usa descripcion, no nombre
            else:
                obj = clase(nombre=nombre_nuevo)
            fn_insertar(obj)
            st.success(f"{label} registrado correctamente.")
            st.rerun()
        except ValueError as e:
            st.error(f"Error de validación: {e}")
        except Exception as e:
            st.error(f"Error inesperado: {e}")

    st.divider()

    # Editar / Eliminar 
    st.subheader(f"✏️ Editar o eliminar {label}")

    id_buscar = st.number_input(f"ID a buscar:", min_value=1, step=1, key=f"buscar_{col_id}")

    if st.button("Buscar", key=f"btn_buscar_{col_id}"):
        resultado = fn_obtener(int(id_buscar))
        if resultado is None:
            st.error(f"No se encontró {label} con ese ID.")
            st.session_state[key_encontrado] = None
        else:
            st.session_state[key_encontrado] = dict(resultado)
            st.session_state[key_eliminado] = False

    registro = st.session_state[key_encontrado]

    if registro and not st.session_state[key_eliminado]:
        # Mostrar el nombre o descripción según el tipo
        if label == "Cobertura":
            valor_actual = registro.get("descripcion", "")
            st.success(f"Registro encontrado: {valor_actual}")
        else:
            st.success(f"Registro encontrado: {registro['nombre']}")

        with st.form(f"form_editar_{col_id}"):
            if label == "Cobertura":
                nombre_edit = st.text_input("Descripción:", value=registro.get("descripcion", ""))
            else:
                nombre_edit = st.text_input("Nombre:", value=registro.get("nombre", ""))
            col1, col2 = st.columns(2)
            actualizar = col1.form_submit_button("Actualizar", use_container_width=True)
            eliminar = col2.form_submit_button("🗑️ Eliminar", use_container_width=True)

        if actualizar:
            try:
                if label == "Cobertura":
                    obj = clase(descripcion=nombre_edit, id_cobertura=registro[col_id])
                else:
                    obj = clase(nombre=nombre_edit, id_=registro[col_id])
                fn_actualizar(obj)
                st.session_state[key_encontrado] = dict(fn_obtener(registro[col_id]))
                st.success("Registro actualizado correctamente.")
                st.rerun()
            except ValueError as e:
                st.error(f"Error de validación: {e}")
            except Exception as e:
                st.error(f"Error inesperado: {e}")

        if eliminar:
            try:
                fn_eliminar(registro[col_id])
                st.session_state[key_encontrado] = None
                st.session_state[key_eliminado] = True
                st.rerun()
            except Exception as e:
                st.error(f"Error inesperado: {e}")

    if st.session_state[key_eliminado]:
        st.warning("Registro eliminado correctamente.")


def pagina_catalogos():
    st.title("📚 Gestión de Catálogos")
    st.divider()

    # Añadir pestaña para Coberturas
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🌍 Países",
        "🛡️ Tipos de Seguro",
        "📄 Estados de Póliza",
        "⚠️ Tipos de Siniestro",
        "📋 Estados de Reclamación",
        "🔁 Tipos de Reaseguro",
        "📦 Coberturas",
    ])

    with tab1:
        _seccion_catalogo(
            label="País", clase=Pais,
            fn_listar=listar_paises, fn_insertar=insertar_pais,
            fn_obtener=obtener_pais_por_id, fn_actualizar=actualizar_pais,
            fn_eliminar=eliminar_pais, col_id="idpais",
        )

    with tab2:
        _seccion_catalogo(
            label="Tipo de Seguro", clase=TipoSeguro,
            fn_listar=listar_tipos_seguro, fn_insertar=insertar_tipo_seguro,
            fn_obtener=obtener_tipo_seguro_por_id, fn_actualizar=actualizar_tipo_seguro,
            fn_eliminar=eliminar_tipo_seguro, col_id="idtiposeguro",
        )

    with tab3:
        _seccion_catalogo(
            label="Estado de Póliza", clase=EstadoPoliza,
            fn_listar=listar_estados_poliza, fn_insertar=insertar_estado_poliza,
            fn_obtener=obtener_estado_poliza_por_id, fn_actualizar=actualizar_estado_poliza,
            fn_eliminar=eliminar_estado_poliza, col_id="idestadopoliza",
        )

    with tab4:
        _seccion_catalogo(
            label="Tipo de Siniestro", clase=TipoSiniestro,
            fn_listar=listar_tipos_siniestro, fn_insertar=insertar_tipo_siniestro,
            fn_obtener=obtener_tipo_siniestro_por_id, fn_actualizar=actualizar_tipo_siniestro,
            fn_eliminar=eliminar_tipo_siniestro, col_id="idtiposiniestro",
        )

    with tab5:
        _seccion_catalogo(
            label="Estado de Reclamación", clase=EstadoReclamacion,
            fn_listar=listar_estados_reclamacion, fn_insertar=insertar_estado_reclamacion,
            fn_obtener=obtener_estado_reclamacion_por_id, fn_actualizar=actualizar_estado_reclamacion,
            fn_eliminar=eliminar_estado_reclamacion, col_id="idestadoreclamacion",
        )

    with tab6:
        _seccion_catalogo(
            label="Tipo de Reaseguro", clase=TipoReaseguro,
            fn_listar=listar_tipos_reaseguro, fn_insertar=insertar_tipo_reaseguro,
            fn_obtener=obtener_tipo_reaseguro_por_id, fn_actualizar=actualizar_tipo_reaseguro,
            fn_eliminar=eliminar_tipo_reaseguro, col_id="idtiporeaseguro",
        )

    with tab7:
        _seccion_catalogo(
            label="Cobertura", clase=Cobertura,
            fn_listar=listar_coberturas, fn_insertar=insertar_cobertura,
            fn_obtener=obtener_cobertura_por_id, fn_actualizar=actualizar_cobertura,
            fn_eliminar=eliminar_cobertura, col_id="idcobertura",
        )
=======
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
>>>>>>> 73161b5 (mis cambios)
