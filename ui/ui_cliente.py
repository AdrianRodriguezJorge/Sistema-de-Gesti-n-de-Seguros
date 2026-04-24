import streamlit as st
import pandas as pd

from data.class_cliente import Cliente
from db.queries_cliente import (
    obtener_cliente_por_id,
    insertar_cliente,
    actualizar_cliente,
    eliminar_cliente,
    listar_clientes
)
from db.queries_catalogos import listar_paises


def _cargar_paises():
    paises = listar_paises()
    nombres = [p["nombre"] for p in paises]
    nombre_a_id = {p["nombre"]: p["idpais"] for p in paises}
    id_a_nombre = {p["idpais"]: p["nombre"] for p in paises}
    return nombres, nombre_a_id, id_a_nombre


def pagina_clientes():
    st.title("👤 Gestión de Clientes")
    st.divider()

    if "cliente_encontrado" not in st.session_state:
        st.session_state.cliente_encontrado = None
    if "cliente_eliminado" not in st.session_state:
        st.session_state.cliente_eliminado = False

    tab1, tab2, tab3 = st.tabs(["Listado", "Nuevo Cliente", "Editar/Eliminar"])

    with tab1:
        st.subheader("📋 Listado de clientes")
        clientes = listar_clientes()
        if clientes:
            st.dataframe(pd.DataFrame(clientes), use_container_width=True)
        else:
            st.info("No hay clientes registrados.")

    with tab2:
        st.subheader("➕ Registrar nuevo cliente")

        paises_nombres, paises_nombre_a_id, _ = _cargar_paises()

        if not paises_nombres:
            st.warning("No hay países registrados. Añade países en la sección de Catálogos primero.")
        else:
            with st.form("form_nuevo_cliente"):
                no_identificacion = st.text_input("Número de identificación:")
                nombre = st.text_input("Nombre:")
                apellidos = st.text_input("Apellidos:")
                edad = st.number_input("Edad:", min_value=0, max_value=120)
                sexo = st.selectbox("Sexo:", ["M", "F"])
                pais_nombre = st.selectbox("País:", paises_nombres)
                direccion = st.text_input("Dirección postal:")
                telefono = st.text_input("Teléfono:")
                correo = st.text_input("Correo electrónico:")
                guardar = st.form_submit_button("Guardar", use_container_width=True)

            if guardar:
                try:
                    cliente = Cliente(
                        no_identificacion=no_identificacion,
                        nombre=nombre,
                        apellidos=apellidos,
                        edad=edad,
                        sexo=sexo,
                        telefono=telefono,
                        correo=correo,
                        idpais=paises_nombre_a_id[pais_nombre],
                        dir_postal=direccion
                    )
                    insertar_cliente(cliente)
                    st.success(f"Cliente {cliente.nombre} registrado correctamente.")
                except ValueError as e:
                    st.error(f"Error de validación: {e}")
                except Exception as e:
                    st.error(f"Error inesperado: {e}")

    with tab3:
        st.subheader("✏️ Editar o eliminar cliente")

        paises_nombres, paises_nombre_a_id, paises_id_a_nombre = _cargar_paises()

        id_buscar = st.number_input("ID del cliente a buscar:", min_value=1, step=1, key="input_id_cliente")

        if st.button("Buscar cliente"):
            resultado = obtener_cliente_por_id(int(id_buscar))
            if resultado is None:
                st.error("No se encontró un cliente con ese ID.")
                st.session_state.cliente_encontrado = None
            else:
                st.session_state.cliente_encontrado = dict(resultado)
                st.session_state.cliente_eliminado = False

        cliente = st.session_state.cliente_encontrado

        if cliente and not st.session_state.cliente_eliminado:
            st.success(f"Cliente encontrado: {cliente['nombre']} {cliente['apellidos']}")

            pais_actual_nombre = paises_id_a_nombre.get(cliente["idpais"], paises_nombres[0] if paises_nombres else "")
            pais_index = paises_nombres.index(pais_actual_nombre) if pais_actual_nombre in paises_nombres else 0

            with st.form("form_editar_cliente"):
                no_identificacion = st.text_input("Número de identificación:", value=cliente["no_identificacion"])
                nombre = st.text_input("Nombre:", value=cliente["nombre"])
                apellidos = st.text_input("Apellidos:", value=cliente["apellidos"])
                edad = st.number_input("Edad:", min_value=0, max_value=120, value=int(cliente["edad"]))
                sexo = st.selectbox("Sexo:", ["M", "F"], index=["M", "F"].index(cliente["sexo"]))
                pais_nombre = st.selectbox("País:", paises_nombres, index=pais_index)
                direccion = st.text_input("Dirección postal:", value=cliente["dir_postal"] or "")
                telefono = st.text_input("Teléfono:", value=cliente["telefono"] or "")
                correo = st.text_input("Correo electrónico:", value=cliente["correo"] or "")

                col1, col2 = st.columns(2)
                actualizar = col1.form_submit_button("Actualizar", use_container_width=True)
                eliminar = col2.form_submit_button("🗑️ Eliminar", use_container_width=True)

            if actualizar:
                try:
                    cliente_editado = Cliente(
                        no_identificacion=no_identificacion,
                        nombre=nombre,
                        apellidos=apellidos,
                        edad=edad,
                        sexo=sexo,
                        telefono=telefono,
                        correo=correo,
                        idpais=paises_nombre_a_id[pais_nombre],
                        dir_postal=direccion,
                        idcliente=cliente["idcliente"]
                    )
                    actualizar_cliente(cliente_editado)
                    st.session_state.cliente_encontrado = dict(obtener_cliente_por_id(cliente["idcliente"]))
                    st.success("Cliente actualizado correctamente.")
                    st.rerun()
                except ValueError as e:
                    st.error(f"Error de validación: {e}")
                except Exception as e:
                    st.error(f"Error inesperado: {e}")

            if eliminar:
                try:
                    eliminar_cliente(cliente["idcliente"])
                    st.session_state.cliente_encontrado = None
                    st.session_state.cliente_eliminado = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error inesperado: {e}")

        if st.session_state.cliente_eliminado:
            st.warning("Cliente eliminado correctamente.")
