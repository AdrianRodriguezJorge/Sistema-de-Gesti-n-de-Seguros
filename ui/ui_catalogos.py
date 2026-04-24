import streamlit as st
import pandas as pd

from data.class_catalogos import (
    Pais, TipoSeguro, EstadoPoliza,
    TipoSiniestro, EstadoReclamacion, TipoReaseguro
)
from db.queries_catalogos import (
    insertar_pais, listar_paises, obtener_pais_por_id, actualizar_pais, eliminar_pais,
    insertar_tipo_seguro, listar_tipos_seguro, obtener_tipo_seguro_por_id, actualizar_tipo_seguro, eliminar_tipo_seguro,
    insertar_estado_poliza, listar_estados_poliza, obtener_estado_poliza_por_id, actualizar_estado_poliza, eliminar_estado_poliza,
    insertar_tipo_siniestro, listar_tipos_siniestro, obtener_tipo_siniestro_por_id, actualizar_tipo_siniestro, eliminar_tipo_siniestro,
    insertar_estado_reclamacion, listar_estados_reclamacion, obtener_estado_reclamacion_por_id, actualizar_estado_reclamacion, eliminar_estado_reclamacion,
    insertar_tipo_reaseguro, listar_tipos_reaseguro, obtener_tipo_reaseguro_por_id, actualizar_tipo_reaseguro, eliminar_tipo_reaseguro,
)


def _seccion_catalogo(label, clase, fn_listar, fn_insertar, fn_obtener, fn_actualizar, fn_eliminar, col_id):
    """Renderiza listado, nuevo registro y editar/eliminar para un catálogo usando session_state."""

    key_encontrado = f"cat_{col_id}_encontrado"
    key_eliminado  = f"cat_{col_id}_eliminado"

    if key_encontrado not in st.session_state:
        st.session_state[key_encontrado] = None
    if key_eliminado not in st.session_state:
        st.session_state[key_eliminado] = False

    # ── Listado ──────────────────────────────────────────────
    st.subheader(f"📋 Listado de {label}")
    registros = fn_listar()
    if registros:
        st.dataframe(pd.DataFrame(registros), use_container_width=True)
    else:
        st.info(f"No hay registros en {label}.")

    st.divider()

    # ── Nuevo registro ────────────────────────────────────────
    st.subheader(f"➕ Nuevo {label}")
    with st.form(f"form_nuevo_{col_id}"):
        nombre_nuevo = st.text_input("Nombre:")
        guardar = st.form_submit_button("Guardar", use_container_width=True)

    if guardar:
        try:
            obj = clase(nombre=nombre_nuevo)
            fn_insertar(obj)
            st.success(f"{label} '{obj.nombre}' registrado correctamente.")
            st.rerun()
        except ValueError as e:
            st.error(f"Error de validación: {e}")
        except Exception as e:
            st.error(f"Error inesperado: {e}")

    st.divider()

    # ── Editar / Eliminar ─────────────────────────────────────
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
        st.success(f"Registro encontrado: {registro['nombre']}")

        with st.form(f"form_editar_{col_id}"):
            nombre_edit = st.text_input("Nombre:", value=registro["nombre"])
            col1, col2 = st.columns(2)
            actualizar = col1.form_submit_button("Actualizar", use_container_width=True)
            eliminar   = col2.form_submit_button("🗑️ Eliminar", use_container_width=True)

        if actualizar:
            try:
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

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🌍 Países",
        "🛡️ Tipos de Seguro",
        "📄 Estados de Póliza",
        "⚠️ Tipos de Siniestro",
        "📋 Estados de Reclamación",
        "🔁 Tipos de Reaseguro",
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
