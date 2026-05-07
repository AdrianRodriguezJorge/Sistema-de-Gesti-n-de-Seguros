import streamlit as st
import pandas as pd
from datetime import datetime
from data.class_reclamacion import Reclamacion
from data.class_reclamacion_rechazada import ReclamacionRechazada
from db.queries_reclamacion import CrudReclamacion
from db.queries_reclamacion_rechazada import CrudReclamacionRechazada
from db.queries_poliza import CrudPoliza
from db.queries_catalogos import CrudTipoSiniestro, CrudEstadoReclamacion, CrudTipoSeguro
from db.queries_cliente import CrudCliente
from db.validaciones import validar_poliza_activa

def _cargar_catalogos_reclamacion():
    siniestros = CrudTipoSiniestro().obtener_todos()
    estados = CrudEstadoReclamacion().obtener_todos()
    polizas = CrudPoliza().obtener_todos()
    clientes = CrudCliente().obtener_todos()
    tipos_seguro = CrudTipoSeguro().obtener_todos()
    cat = {'tsin_n_id': {s.nombre: s.id for s in siniestros}, 'tsin_id_n': {s.id: s.nombre for s in siniestros}, 'er_n_id': {e.nombre: e.id for e in estados}, 'er_id_n': {e.id: e.nombre for e in estados}, 'pol_id_obj': {p.id: p for p in polizas}, 'cli_id_obj': {c.id: c for c in clientes}, 'tseg_id_n': {t.id: t.nombre for t in tipos_seguro}}
    pol_etiquetas = []
    pol_etq_id = {}
    for p in polizas:
        cliente = cat['cli_id_obj'].get(p.idCliente)
        cliente_nombre = f'{cliente.nombre} {cliente.apellidos}' if cliente else 'Desconocido'
        etiqueta = f'Póliza #{p.id} - Cliente: {cliente_nombre}'
        pol_etiquetas.append(etiqueta)
        pol_etq_id[etiqueta] = p.id
    cat['pol_etq'] = pol_etiquetas
    cat['pol_etq_id'] = pol_etq_id
    return cat

def pagina_reclamaciones():
    st.title('Gestión de Reclamaciones')
    st.divider()
    catalogos = _cargar_catalogos_reclamacion()
    tab1, tab2, tab3 = st.tabs(['Listado', 'Nueva Reclamación', 'Editar Reclamación'])
    with tab1:
        with st.spinner('Cargando reclamaciones...'):
            lista_reclamaciones = CrudReclamacion().obtener_todos()
        st.subheader('Listado General de Reclamaciones')
        if lista_reclamaciones:
            filas_todas = []
            polizas_cache = {}
            clientes_cache = {}
            for r in lista_reclamaciones:
                if r.idPoliza not in polizas_cache:
                    polizas_cache[r.idPoliza] = catalogos['pol_id_obj'].get(r.idPoliza)
                poliza = polizas_cache[r.idPoliza]
                cliente_nombre = 'Desconocido'
                tipo_seguro_nombre = 'Desconocido'
                if poliza:
                    if poliza.idCliente not in clientes_cache:
                        clientes_cache[poliza.idCliente] = catalogos['cli_id_obj'].get(poliza.idCliente)
                    cliente = clientes_cache[poliza.idCliente]
                    if cliente:
                        cliente_nombre = f'{cliente.nombre} {cliente.apellidos}'
                    tipo_seguro_nombre = catalogos['tseg_id_n'].get(poliza.idTipoSeguro, 'Desconocido')
                filas_todas.append({'ID': r.id, 'Póliza': r.idPoliza, 'Cliente': cliente_nombre, 'Tipo Seguro': tipo_seguro_nombre, 'Fecha Siniestro': r.fechaSiniestro, 'Monto Reclamado': f'${r.montoReclamado:,.2f}', 'Estado': catalogos['er_id_n'].get(r.idEstadoReclamacion, '-'), 'Tipo Siniestro': catalogos['tsin_id_n'].get(r.idTipoSiniestro, '-')})
            st.dataframe(pd.DataFrame(filas_todas), use_container_width=True, hide_index=True)
        else:
            st.info('No hay reclamaciones registradas.')
        st.divider()
        st.subheader('Detalle de Reclamaciones')
        if lista_reclamaciones:
            filas_rec = []
            polizas_cache = {}
            clientes_cache = {}
            for r in lista_reclamaciones:
                if r.idPoliza not in polizas_cache:
                    polizas_cache[r.idPoliza] = catalogos['pol_id_obj'].get(r.idPoliza)
                poliza = polizas_cache[r.idPoliza]
                cliente_nombre = 'Desconocido'
                tipo_seguro_nombre = 'Desconocido'
                if poliza:
                    if poliza.idCliente not in clientes_cache:
                        clientes_cache[poliza.idCliente] = catalogos['cli_id_obj'].get(poliza.idCliente)
                    cliente = clientes_cache[poliza.idCliente]
                    if cliente:
                        cliente_nombre = f'{cliente.nombre} {cliente.apellidos}'
                    tipo_seguro_nombre = catalogos['tseg_id_n'].get(poliza.idTipoSeguro, 'Desconocido')
                filas_rec.append({'Nombre del cliente': cliente_nombre, 'Número de póliza': r.idPoliza, 'Tipo de seguro': tipo_seguro_nombre, 'Número de reclamación': r.id, 'Tipo de siniestro': catalogos['tsin_id_n'].get(r.idTipoSiniestro, '-'), 'Fecha del siniestro': r.fechaSiniestro, 'Monto reclamado': f'${r.montoReclamado:,.2f}', 'Estado de la reclamación': catalogos['er_id_n'].get(r.idEstadoReclamacion, '-'), 'Monto indemnizado': f'${r.montoIndemnizado:,.2f}' if r.montoIndemnizado else '$0.00'})
            st.dataframe(pd.DataFrame(filas_rec), use_container_width=True, hide_index=True)
        else:
            st.info('No hay reclamaciones registradas.')
        st.divider()
        st.subheader('Resumen de Reclamaciones por Estado')
        if lista_reclamaciones:
            resumen = {}
            for r in lista_reclamaciones:
                estado_nombre = catalogos['er_id_n'].get(r.idEstadoReclamacion, 'Desconocido')
                if estado_nombre not in resumen:
                    resumen[estado_nombre] = {'cantidad': 0, 'total_reclamado': 0.0, 'total_indemnizado': 0.0}
                resumen[estado_nombre]['cantidad'] += 1
                resumen[estado_nombre]['total_reclamado'] += float(r.montoReclamado or 0)
                resumen[estado_nombre]['total_indemnizado'] += float(r.montoIndemnizado or 0)
            filas_resumen = []
            for estado, datos in resumen.items():
                filas_resumen.append({'Estado de la reclamación': estado, 'Cantidad de reclamaciones': datos['cantidad'], 'Total de monto reclamado': f"${datos['total_reclamado']:,.2f}", 'Total de monto indemnizado': f"${datos['total_indemnizado']:,.2f}"})
            st.dataframe(pd.DataFrame(filas_resumen), use_container_width=True, hide_index=True)
        else:
            st.info('No hay datos suficientes para generar el resumen.')
    with tab2:
        st.subheader('Registrar Nueva Reclamación')
        if not catalogos['pol_etq'] or not catalogos['tsin_n_id']:
            st.warning('Se requieren pólizas y tipos de siniestro registrados en el sistema.')
        else:
            with st.form('form_nueva_rec'):
                c1, c2 = st.columns(2)
                poliza_sel = c1.selectbox('Seleccionar Póliza', catalogos['pol_etq'])
                tipo_siniestro_sel = c2.selectbox('Tipo de Siniestro', list(catalogos['tsin_n_id'].keys()))
                fecha_siniestro = st.date_input('Fecha del Siniestro')
                c3, c4 = st.columns(2)
                monto_reclamado = c3.number_input('Monto Reclamado ($)', min_value=0.0, step=0.01)
                monto_indemnizado = c4.number_input('Monto Indemnizado ($)', min_value=0.0, step=0.01)
                estado_sel = st.selectbox('Estado de la Reclamación', list(catalogos['er_n_id'].keys()))
                motivo_nuevo = ''
                if estado_sel == 'Rechazada':
                    motivo_nuevo = st.text_area('Motivo de rechazo', placeholder='Ingrese el motivo de rechazo...')
                btn_guardar_nueva = st.form_submit_button('Guardar Reclamación', use_container_width=True)
            if btn_guardar_nueva:
                if estado_sel == 'Rechazada' and (not motivo_nuevo.strip()):
                    st.error('Debe ingresar un motivo de rechazo.')
                else:
                    try:
                        identificador_poliza = catalogos['pol_etq_id'][poliza_sel]
                        validar_poliza_activa(identificador_poliza)
                        nueva_reclamacion_datos = Reclamacion(idTipoSiniestro=catalogos['tsin_n_id'][tipo_siniestro_sel], fechaSiniestro=fecha_siniestro, montoReclamado=monto_reclamado, idEstadoReclamacion=catalogos['er_n_id'][estado_sel], idPoliza=identificador_poliza, montoIndemnizado=monto_indemnizado)
                        id_generado = CrudReclamacion().crear(nueva_reclamacion_datos)
                        if estado_sel == 'Rechazada':
                            reclamacion_rechazada = ReclamacionRechazada(motivo=motivo_nuevo.strip(), idReclamacion=id_generado)
                            CrudReclamacionRechazada().crear(reclamacion_rechazada)
                        st.success(f'Reclamación #{id_generado} creada exitosamente.')
                        st.rerun()
                    except ValueError as e:
                        st.error(f'Error de validación: {e}')
    with tab3:
        st.subheader('Editar Reclamación')
        if 'edit_reclamacion_page' not in st.session_state:
            st.session_state.edit_reclamacion_page = 0
        PAGE_SIZE = 10
        with st.form('form_buscar_reclamacion'):
            st.markdown('**Buscar Reclamación para Editar**')
            col_bus1, col_bus2, col_bus3 = st.columns([2, 2, 1])
            busqueda_id = col_bus1.text_input('Por N° de Reclamación')
            busqueda_cliente = col_bus2.text_input('Por Nombre de Cliente')
            busqueda_estado = col_bus3.selectbox('Por Estado', ['Todos'] + list(catalogos['er_id_n'].values()))
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                btn_buscar = st.form_submit_button(' Buscar', use_container_width=True)
            with col_btn2:
                btn_limpiar = st.form_submit_button(' Limpiar', use_container_width=True)
        if 'buscar_reclamacion' not in st.session_state:
            st.session_state.buscar_reclamacion = False
        if btn_limpiar:
            st.session_state.buscar_reclamacion = False
            st.rerun()
        if btn_buscar:
            st.session_state.buscar_reclamacion = True
        lista_edicion = []
        if st.session_state.buscar_reclamacion:
            filtros = {}
            if busqueda_id:
                try:
                    filtros['idReclamacion'] = int(busqueda_id)
                except ValueError:
                    st.error('N° de Reclamación debe ser un número')
                    filtros['idReclamacion'] = -1
            if busqueda_estado != 'Todos':
                filtros['idEstadoReclamacion'] = catalogos['er_n_id'][busqueda_estado]
            if busqueda_cliente:
                with st.spinner('Buscando...'):
                    clientes_encontrados = CrudCliente().filtrar(nombre=busqueda_cliente)
                    if clientes_encontrados:
                        lista_edicion = []
                        polizas_cache = {}
                        for cli in clientes_encontrados:
                            if cli.id not in polizas_cache:
                                polizas_cache[cli.id] = CrudPoliza().filtrar(idCliente=cli.id)
                            for pol in polizas_cache[cli.id]:
                                recs = CrudReclamacion().filtrar(idPoliza=pol.id, **filtros)
                                lista_edicion.extend(recs)
                    else:
                        lista_edicion = []
            else:
                with st.spinner('Contando reclamaciones...'):
                    total_reclamaciones = CrudReclamacion().contar(**filtros)
                if total_reclamaciones == 0:
                    st.info('No se encontraron reclamaciones con los filtros aplicados.')
                    lista_edicion = []
                else:
                    total_pages = (total_reclamaciones + PAGE_SIZE - 1) // PAGE_SIZE
                    if st.session_state.edit_reclamacion_page >= total_pages:
                        st.session_state.edit_reclamacion_page = max(0, total_pages - 1)
                    col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
                    with col_pag1:
                        if st.button('← Anterior', key='edit_rec_ant', disabled=st.session_state.edit_reclamacion_page <= 0):
                            st.session_state.edit_reclamacion_page -= 1
                            st.rerun()
                    with col_pag2:
                        st.markdown(f'<center>Página {st.session_state.edit_reclamacion_page + 1} de {total_pages} ({total_reclamaciones} reclamaciones)</center>', unsafe_allow_html=True)
                    with col_pag3:
                        if st.button('Siguiente →', key='edit_rec_sig', disabled=st.session_state.edit_reclamacion_page >= total_pages - 1):
                            st.session_state.edit_reclamacion_page += 1
                            st.rerun()
                    with st.spinner(f'Cargando reclamaciones (página {st.session_state.edit_reclamacion_page + 1})...'):
                        lista_edicion = CrudReclamacion().filtrar(limit=PAGE_SIZE, offset=st.session_state.edit_reclamacion_page * PAGE_SIZE, **filtros)
        if lista_edicion:
            opciones_rec = {}
            polizas_cache = {}
            clientes_cache = {}
            for r in lista_edicion:
                if r.idPoliza not in polizas_cache:
                    polizas_cache[r.idPoliza] = catalogos['pol_id_obj'].get(r.idPoliza)
                poliza = polizas_cache[r.idPoliza]
                cliente_nombre = 'Desconocido'
                if poliza:
                    if poliza.idCliente not in clientes_cache:
                        clientes_cache[poliza.idCliente] = catalogos['cli_id_obj'].get(poliza.idCliente)
                    cliente = clientes_cache[poliza.idCliente]
                    if cliente:
                        cliente_nombre = f'{cliente.nombre} {cliente.apellidos}'
                etiqueta = f"Reclamación #{r.id} | Póliza #{r.idPoliza} | {cliente_nombre} | {catalogos['tsin_id_n'].get(r.idTipoSiniestro, '-')} | {catalogos['er_id_n'].get(r.idEstadoReclamacion, '-')}"
                opciones_rec[etiqueta] = r
            if opciones_rec:
                sel_rec = st.selectbox('Seleccione la reclamación a editar', list(opciones_rec.keys()))
                reclamacion_seleccionada = opciones_rec[sel_rec]
                st.divider()
                st.markdown(f'**Editando Reclamación #{reclamacion_seleccionada.id}**')
                with st.form('form_editar_rec'):
                    col_m1, col_m2 = st.columns(2)
                    nuevo_monto_reclamado = col_m1.number_input('Monto Reclamado ($)', value=float(reclamacion_seleccionada.montoReclamado), min_value=0.0, step=0.01)
                    nuevo_monto_indemnizado = col_m2.number_input('Monto Indemnizado ($)', value=float(reclamacion_seleccionada.montoIndemnizado) if reclamacion_seleccionada.montoIndemnizado else 0.0, min_value=0.0, step=0.01)
                    nombres_estados = list(catalogos['er_n_id'].keys())
                    idx_estado_actual = nombres_estados.index(catalogos['er_id_n'].get(reclamacion_seleccionada.idEstadoReclamacion)) if reclamacion_seleccionada.idEstadoReclamacion in catalogos['er_id_n'] else 0
                    nuevo_estado = st.selectbox('Estado de la Reclamación', nombres_estados, index=idx_estado_actual)
                    motivo_edicion = ''
                    if nuevo_estado == 'Rechazada':
                        motivo_edicion = st.text_area('Motivo de rechazo', placeholder='Ingrese el motivo de rechazo...')
                    btn_guardar_edicion = st.form_submit_button('Guardar Cambios', use_container_width=True)
                if btn_guardar_edicion:
                    if nuevo_estado == 'Rechazada' and (not motivo_edicion.strip()):
                        st.error('Debe ingresar un motivo de rechazo.')
                    else:
                        ya_rechazada = catalogos['er_id_n'].get(reclamacion_seleccionada.idEstadoReclamacion) == 'Rechazada'
                        reclamacion_seleccionada.montoReclamado = nuevo_monto_reclamado
                        reclamacion_seleccionada.montoIndemnizado = nuevo_monto_indemnizado
                        reclamacion_seleccionada.idEstadoReclamacion = catalogos['er_n_id'][nuevo_estado]
                        CrudReclamacion().actualizar(reclamacion_seleccionada)
                        if nuevo_estado == 'Rechazada' and (not ya_rechazada):
                            reclamacion_rechazada = ReclamacionRechazada(motivo=motivo_edicion.strip(), idReclamacion=reclamacion_seleccionada.id)
                            CrudReclamacionRechazada().crear(reclamacion_rechazada)
                        st.success('Reclamación actualizada correctamente.')
                        st.rerun()
            else:
                st.info('No hay resultados con datos completos en esta página.')
        else:
            st.info('No se encontraron reclamaciones para editar.')