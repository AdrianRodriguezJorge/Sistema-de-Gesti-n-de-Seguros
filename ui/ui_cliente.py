import streamlit as st
import pandas as pd
from datetime import datetime
from data.class_cliente import Cliente
<<<<<<< HEAD
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
    opciones = [(p["idpais"], p["nombre"]) for p in paises]
    return opciones
=======
from db.conexionDB import Database
from db.queries_cliente import CrudCliente
from db.queries_catalogos import CrudPais, CrudEstadoPoliza, CrudEstadoReclamacion
from db.queries_poliza import CrudPoliza
from db.queries_poliza_cancelada import CrudPolizaCancelada
from db.queries_reclamacion import CrudReclamacion
from db.queries_reclamacion_rechazada import CrudReclamacionRechazada
>>>>>>> 73161b5 (mis cambios)

def _cargar_catalogos_cliente():
    paises = CrudPais().obtener_todos()
    return {'nombres_paises': [p.nombre for p in paises], 'pais_n_id': {p.nombre: p.id for p in paises}, 'pais_id_n': {p.id: p.nombre for p in paises}}

def pagina_clientes():
    st.title('Gestión de Clientes')
    st.divider()
    cat = _cargar_catalogos_cliente()
    crud_cliente = CrudCliente()
    tab1, tab2, tab3 = st.tabs(['Listado', 'Nuevo Cliente', 'Editar / Eliminar'])
    with tab1:
        st.subheader('Listado General de Clientes')
        with st.spinner('Cargando clientes...'):
            lista_clientes = crud_cliente.obtener_todos()
        if lista_clientes:
            filas_todos = []
            for c in lista_clientes:
                filas_todos.append({'ID': c.id, 'Nombre Completo': f'{c.nombre} {c.apellidos}', 'Identificación': c.noIdentificacion, 'Edad': c.edad, 'Sexo': c.sexo, 'País': cat['pais_id_n'].get(c.idPais, 'N/A'), 'Teléfono': c.telefono, 'Correo': c.correo})
            st.dataframe(pd.DataFrame(filas_todos), use_container_width=True, hide_index=True)
        else:
            st.info('No hay clientes registrados.')
        st.divider()
        st.subheader('Listado de Clientes por País')
        for id_p, nombre_p in cat['pais_id_n'].items():
            clientes_pais = [c for c in lista_clientes if c.idPais == id_p]
            if clientes_pais:
                with st.expander(f'País: {nombre_p} ({len(clientes_pais)})', expanded=True):
                    with st.spinner('Cargando pólizas...'):
                        lista_polizas = CrudPoliza().obtener_todos()
                        estados_poliza = {e.id: e.nombre for e in CrudEstadoPoliza().obtener_todos()}
                    filas_p = []
                    for c in clientes_pais:
                        p_activas = [p for p in lista_polizas if p.idCliente == c.id and estados_poliza.get(p.idEstadoPoliza) == 'Activa']
                        total_primas = sum((p.primaMensual for p in p_activas))
                        filas_p.append({'Nombre del cliente': f'{c.nombre} {c.apellidos}', 'Número de identificación': c.noIdentificacion, 'Cantidad de pólizas activas': len(p_activas), 'Total primas activas': f'${total_primas:,.2f}'})
                    st.dataframe(pd.DataFrame(filas_p), use_container_width=True, hide_index=True)
        st.divider()
        st.subheader('Clientes con Reclamaciones Rechazadas')
        with st.spinner('Cargando reclamaciones rechazadas...'):
            with Database() as db:
                sql = """
                    SELECT 
                        c.nombre,
                        c.apellidos,
                        c.no_identificacion,
                        COUNT(*) as cantidad
                    FROM reclamacion r
                    JOIN estado_reclamacion er ON r.idestadoreclamacion = er.idestadoreclamacion
                    JOIN poliza p ON r.idpoliza = p.idpoliza
                    JOIN cliente c ON p.idcliente = c.idcliente
                    WHERE er.nombre = 'Rechazada'
                    GROUP BY c.idcliente, c.nombre, c.apellidos, c.no_identificacion
                    ORDER BY c.nombre, c.apellidos
                """
                resultados = db.fetch_all(sql)
        
        if resultados:
            filas_rech = []
            for row in resultados:
                filas_rech.append({
                    'Nombre del cliente': f"{row['nombre']} {row['apellidos']}",
                    'Número de identificación': row['no_identificacion'],
                    'Cantidad de reclamaciones rechazadas': row['cantidad'],
                    'Motivo del rechazo': 'No disponible'
                })
            st.dataframe(pd.DataFrame(filas_rech), use_container_width=True, hide_index=True)
        else:
            st.info('No hay reclamaciones rechazadas.')
    with tab2:
<<<<<<< HEAD
        st.subheader("➕ Registrar nuevo cliente")

        paises_opciones = _cargar_paises()

        if not paises_opciones:
            st.warning("No hay países registrados. Añade países en la sección de Catálogos primero.")
        else:
            with st.form("form_nuevo_cliente"):
                noIdentificacion = st.text_input("Número de identificación:")
                nombre = st.text_input("Nombre:")
                apellidos = st.text_input("Apellidos:")
                edad = st.number_input("Edad:", min_value=0, max_value=120)
                sexo = st.selectbox("Sexo:", ["M", "F"])
                pais_seleccionado = st.selectbox(
                    "País:",
                    options=paises_opciones,
                    format_func=lambda x: x[1]
                )
                dirPostal = st.text_input("Dirección postal:")
                telefono = st.text_input("Teléfono:")
                correo = st.text_input("Correo electrónico:")
                guardar = st.form_submit_button("Guardar", use_container_width=True)

            if guardar:
                try:
                    cliente = Cliente(
                        noIdentificacion=noIdentificacion,
                        nombre=nombre,
                        apellidos=apellidos,
                        edad=edad,
                        sexo=sexo,
                        telefono=telefono,
                        correo=correo,
                        idpais=pais_seleccionado[0],
                        dirPostal=dirPostal
                    )
                    insertar_cliente(cliente)
                    st.success(f"Cliente {cliente.nombre} registrado correctamente.")
                    st.rerun()
                except ValueError as e:
                    st.error(f"Error de validación: {e}")
=======
        st.subheader('Formulario de Registro')
        with st.form('form_nuevo_cliente'):
            c1, c2 = st.columns(2)
            dni = c1.text_input('Número de Identificación')
            nom = c2.text_input('Nombre')
            ape = c1.text_input('Apellidos')
            eda = c2.number_input('Edad', min_value=0, max_value=120, step=1)
            sex = c1.selectbox('Sexo', ['M', 'F'])
            pai = c2.selectbox('País', cat['nombres_paises'])
            dir_p = st.text_input('Dirección Postal')
            tel = c1.text_input('Teléfono')
            ema = c2.text_input('Correo electrónico')
            if st.form_submit_button('Confirmar Registro', use_container_width=True):
                try:
                    cliente_nuevo = Cliente(nom, ape, dni, eda, sex, cat['pais_n_id'][pai], dir_p, tel, ema)
                    crud_cliente.crear(cliente_nuevo)
                    st.success('Cliente registrado con éxito.')
                    st.rerun()
>>>>>>> 73161b5 (mis cambios)
                except Exception as e:
                    st.error(f'Error: {e}')
    with tab3:
<<<<<<< HEAD
        st.subheader("✏️ Editar o eliminar cliente")

        paises_opciones = _cargar_paises()

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

            pais_actual_id = cliente["idpais"]
            pais_actual_index = 0
            for i, (pid, _) in enumerate(paises_opciones):
                if pid == pais_actual_id:
                    pais_actual_index = i
                    break

            with st.form("form_editar_cliente"):
                noIdentificacion = st.text_input("Número de identificación:", value=cliente["noIdentificación"])
                nombre = st.text_input("Nombre:", value=cliente["nombre"])
                apellidos = st.text_input("Apellidos:", value=cliente["apellidos"])
                edad = st.number_input("Edad:", min_value=0, max_value=120, value=int(cliente["edad"]))
                sexo = st.selectbox("Sexo:", ["M", "F"], index=["M", "F"].index(cliente["sexo"]))
                pais_seleccionado = st.selectbox(
                    "País:",
                    options=paises_opciones,
                    format_func=lambda x: x[1],
                    index=pais_actual_index
                )
                dirPostal = st.text_input("Dirección postal:", value=cliente["dirPostal"] or "")
                telefono = st.text_input("Teléfono:", value=cliente["telefono"] or "")
                correo = st.text_input("Correo electrónico:", value=cliente["correo"] or "")

                col1, col2 = st.columns(2)
                actualizar = col1.form_submit_button("Actualizar", use_container_width=True)
                eliminar = col2.form_submit_button("🗑️ Eliminar", use_container_width=True)

            if actualizar:
                try:
                    cliente_editado = Cliente(
                        noIdentificacion=noIdentificacion,
                        nombre=nombre,
                        apellidos=apellidos,
                        edad=edad,
                        sexo=sexo,
                        telefono=telefono,
                        correo=correo,
                        idpais=pais_seleccionado[0],
                        dirPostal=dirPostal,
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
=======
        st.subheader('Gestión de Registros')
        if 'edit_cliente_page' not in st.session_state:
            st.session_state.edit_cliente_page = 0
        PAGE_SIZE = 10
        with st.form('form_buscar_cliente'):
            st.markdown('**Buscar Cliente para Editar/Eliminar**')
            col_bus1, col_bus2, col_bus3 = st.columns([2, 2, 1])
            busqueda_dni = col_bus1.text_input('Por Número de Identificación')
            busqueda_nombre = col_bus2.text_input('Por Nombre o Apellido')
            busqueda_pais = col_bus3.selectbox('Por País', ['Todos'] + cat['nombres_paises'])
            st.form_submit_button('Buscar', use_container_width=True)
           
        filtros = {}
        if busqueda_dni:
            filtros['noIdentificacion'] = busqueda_dni
        if busqueda_nombre and busqueda_nombre.strip():
            filtros['busqueda_nombre'] = busqueda_nombre.strip()
        if busqueda_pais != 'Todos':
            filtros['idPais'] = cat['pais_n_id'][busqueda_pais]
        with st.spinner('Contando clientes...'):
            total_clientes = crud_cliente.contar_filtrado(noIdentificacion=filtros.get('noIdentificacion'), busqueda_nombre=filtros.get('busqueda_nombre'), idPais=filtros.get('idPais'))
        if total_clientes == 0:
            st.info('No se encontraron clientes con los filtros aplicados.')
        else:
            total_pages = (total_clientes + PAGE_SIZE - 1) // PAGE_SIZE
            if st.session_state.edit_cliente_page >= total_pages:
                st.session_state.edit_cliente_page = max(0, total_pages - 1)
            col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
            with col_pag1:
                if st.button('← Anterior', key='edit_cli_ant', disabled=st.session_state.edit_cliente_page <= 0):
                    st.session_state.edit_cliente_page -= 1
                    st.rerun()
            with col_pag2:
                st.markdown(f'<center>Página {st.session_state.edit_cliente_page + 1} de {total_pages} ({total_clientes} clientes)</center>', unsafe_allow_html=True)
            with col_pag3:
                if st.button('Siguiente →', key='edit_cli_sig', disabled=st.session_state.edit_cliente_page >= total_pages - 1):
                    st.session_state.edit_cliente_page += 1
                    st.rerun()
            with st.spinner(f'Cargando clientes (página {st.session_state.edit_cliente_page + 1})...'):
                resultados = crud_cliente.filtrar(limit=PAGE_SIZE, offset=st.session_state.edit_cliente_page * PAGE_SIZE, **filtros)
            if resultados:
                opciones = {f'{c.noIdentificacion} - {c.nombre} {c.apellidos}': c for c in resultados}
                sel = st.selectbox('Seleccione el cliente a editar/eliminar', list(opciones.keys()))
                cliente_seleccionado = opciones[sel]
                st.markdown(f'**Editando: {cliente_seleccionado.nombre} {cliente_seleccionado.apellidos}**')
                with st.form('form_edit_cliente'):
                    n_nom = st.text_input('Nombre', value=cliente_seleccionado.nombre)
                    n_ape = st.text_input('Apellidos', value=cliente_seleccionado.apellidos)
                    n_eda = st.number_input('Edad', value=int(cliente_seleccionado.edad), min_value=0, max_value=120)
                    n_tel = st.text_input('Teléfono', value=cliente_seleccionado.telefono if cliente_seleccionado.telefono else '')
                    n_ema = st.text_input('Correo', value=cliente_seleccionado.correo if cliente_seleccionado.correo else '')
                    col_b1, col_b2 = st.columns(2)
                    btn_upd = col_b1.form_submit_button('Actualizar Datos', use_container_width=True)
                    btn_del = col_b2.form_submit_button('Eliminar Cliente', use_container_width=True)
                    if btn_upd:
                        try:
                            cliente_seleccionado.nombre = n_nom
                            cliente_seleccionado.apellidos = n_ape
                            cliente_seleccionado.edad = n_eda
                            cliente_seleccionado.telefono = n_tel
                            cliente_seleccionado.correo = n_ema
                            crud_cliente.actualizar(cliente_seleccionado)
                            st.success('Datos actualizados.')
                            st.rerun()
                        except Exception as e:
                            st.error(f'Error al actualizar: {e}')
                    if btn_del:
                        crud_cliente.eliminar(cliente_seleccionado.id)
                        st.warning('Cliente y registros asociados eliminados.')
                        st.rerun()
            else:
                st.info('No hay resultados en esta página.')
>>>>>>> 73161b5 (mis cambios)
