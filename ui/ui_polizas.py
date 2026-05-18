import streamlit as st
import pandas as pd
from datetime import datetime
from models.poliza import Poliza
from models.poliza_cancelada import PolizaCancelada
from models.poliza_cobertura import PolizaCobertura
from models.cobertura import Cobertura
from models.pago import Pago
from db.conexionDB import Database
from db.queries_poliza import CrudPoliza
from db.queries_poliza_cancelada import CrudPolizaCancelada
from db.queries_poliza_cobertura import CrudPolizaCobertura
from db.queries_cobertura import CrudCobertura
from db.queries_catalogos import CrudTipoSeguro, CrudEstadoPoliza
from db.queries_cliente import CrudCliente
from db.queries_pago import CrudPago
from db.validaciones import validar_claves_foraneas_poliza

def _cargar_catalogos():
    tipos_seguro = CrudTipoSeguro().obtener_todos()
    estados_poliza = CrudEstadoPoliza().obtener_todos()
    clientes = CrudCliente().obtener_todos()
    return {
        'ts_n_id': {t.nombre: t.id for t in tipos_seguro},
        'ts_id_n': {t.id: t.nombre for t in tipos_seguro},
        'ep_n_id': {e.nombre: e.id for e in estados_poliza},
        'ep_id_n': {e.id: e.nombre for e in estados_poliza},
        'cli_id_obj': {c.id: c for c in clientes},
        'cli_etq': [f'{c.id} - {c.nombre} {c.apellidos}' for c in clientes],
        'cli_etq_id': {f'{c.id} - {c.nombre} {c.apellidos}': c.id for c in clientes}
    }

def pagina_polizas():
    st.title('Gestion de Polizas')
    catalogos = _cargar_catalogos()
    lista_polizas = CrudPoliza().obtener_todos()
    crud_poliza = CrudPoliza()
    
    # Check if there is an active editing session for a policy
    edit_id = st.session_state.get('editing_poliza_id')
    
    if edit_id:
        poliza_sel = crud_poliza.obtener(edit_id)
        if not poliza_sel:
            st.error("La póliza seleccionada no existe.")
            st.session_state.pop('editing_poliza_id', None)
            st.session_state.editing_active = False
            st.rerun()
            
        st.subheader(f'Editar Póliza #{poliza_sel.id}')
        
        # Check if we are confirming deletion
        confirm_del = st.session_state.get('confirming_delete_poliza', False)
        
        if confirm_del:
            st.warning(f" Está seguro de que desea eliminar permanentemente la póliza **#{poliza_sel.id}**?")
            st.write("Esta acción es irreversible y eliminará todos los pagos y coberturas asociados a esta póliza.")
            col_conf1, col_conf2 = st.columns(2)
            if col_conf1.button("Sí, eliminar permanentemente", use_container_width=True, type="primary"):
                try:
                    # Let's delete related payments and coverages first to maintain integrity
                    with Database() as db:
                        db.execute('DELETE FROM poliza_cobertura WHERE idpoliza=%s', (poliza_sel.id,))
                        db.execute('DELETE FROM pago WHERE idpoliza=%s', (poliza_sel.id,))
                        db.execute('DELETE FROM poliza_cancelada WHERE idpoliza=%s', (poliza_sel.id,))
                        db.execute('DELETE FROM reclamacion WHERE idpoliza=%s', (poliza_sel.id,))
                    crud_poliza.eliminar(poliza_sel.id)
                    st.success("Póliza eliminada con éxito.")
                    st.session_state.pop('editing_poliza_id', None)
                    st.session_state.pop('confirming_delete_poliza', None)
                    st.session_state.editing_active = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar: {e}")
            if col_conf2.button("No, mantener registro", use_container_width=True):
                st.session_state.pop('confirming_delete_poliza', None)
                st.rerun()
        else:
            with st.form('form_editar_poliza_focused'):
                col1, col2 = st.columns(2)
                nueva_prima = col1.number_input('Prima Mensual ($)', value=float(poliza_sel.primaMensual), min_value=0.01, format='%.2f')
                nuevo_monto = col2.number_input('Monto Asegurado ($)', value=float(poliza_sel.montoAsegurado), min_value=0.01, format='%.2f')
                nombres_estados = list(catalogos['ep_n_id'].keys())
                idx_estado = list(catalogos['ep_id_n'].keys()).index(poliza_sel.idEstadoPoliza) if poliza_sel.idEstadoPoliza in catalogos['ep_id_n'] else 0
                nuevo_estado = st.selectbox('Estado', nombres_estados, index=idx_estado)
                motivo_edicion = ''
                if nuevo_estado == 'Cancelada':
                    motivo_edicion = st.text_area('Motivo de cancelacion', placeholder='Ingrese el motivo...')
                
                col_b1, col_b2, col_b3 = st.columns(3)
                btn_guardar = col_b1.form_submit_button('Guardar Cambios', use_container_width=True)
                btn_del = col_b2.form_submit_button('Eliminar Póliza', use_container_width=True)
                btn_can = col_b3.form_submit_button('Cancelar', use_container_width=True)
                
                if btn_guardar:
                    try:
                        ya_cancelada = catalogos['ep_id_n'].get(poliza_sel.idEstadoPoliza) == 'Cancelada'
                        poliza_sel.primaMensual = nueva_prima
                        poliza_sel.montoAsegurado = nuevo_monto
                        poliza_sel.idEstadoPoliza = catalogos['ep_n_id'][nuevo_estado]
                        crud_poliza.actualizar(poliza_sel)
                        if nuevo_estado == 'Cancelada' and not ya_cancelada:
                            can_obj = PolizaCancelada(motivo=motivo_edicion.strip() if motivo_edicion.strip() else None, idPoliza=poliza_sel.id)
                            CrudPolizaCancelada().crear(can_obj)
                        st.success('Póliza actualizada.')
                        st.session_state.pop('editing_poliza_id', None)
                        st.session_state.editing_active = False
                        st.rerun()
                    except Exception as e:
                        st.error(f'Error al actualizar: {e}')
                if btn_del:
                    st.session_state.confirming_delete_poliza = True
                    st.rerun()
                if btn_can:
                    st.session_state.pop('editing_poliza_id', None)
                    st.session_state.editing_active = False
                    st.rerun()
        return

    # Ensure stable tab order unless explicitly requested to change
    if 'current_tab_order_poliza' not in st.session_state:
        st.session_state.current_tab_order_poliza = ['Listado', 'Nueva Poliza', 'Editar Poliza', 'Coberturas', 'Pagos']
        
    requested_tab = st.session_state.pop('active_tab_poliza', None)
    if requested_tab and requested_tab in st.session_state.current_tab_order_poliza:
        order = st.session_state.current_tab_order_poliza
        order.remove(requested_tab)
        order.insert(0, requested_tab)
        st.session_state.current_tab_order_poliza = order

    order = st.session_state.current_tab_order_poliza
    created_tabs = st.tabs(order)
    
    tabs_dict = {name: tab for name, tab in zip(order, created_tabs)}
    tab1 = tabs_dict['Listado']
    tab2 = tabs_dict['Nueva Poliza']
    tab3 = tabs_dict['Editar Poliza']
    tab4 = tabs_dict['Coberturas']
    tab5 = tabs_dict['Pagos']
    
    # Tab 1: Listado General
    with tab1:
        hoy = datetime.now().date()

        # Listado de Pólizas
        st.subheader('Listado de Pólizas ')
        if not lista_polizas:
            st.info('No hay polizas registradas.')
        else:
            todas_filas = []
            for p in lista_polizas:
                cliente = catalogos['cli_id_obj'].get(p.idCliente)
                nombre_cli = f'{cliente.nombre} {cliente.apellidos}' if cliente else 'Desconocido'
                tipo_name = catalogos['ts_id_n'].get(p.idTipoSeguro, f'Tipo desconocido (ID: {p.idTipoSeguro})')
                
                todas_filas.append({
                    'Número de póliza': p.id,
                    'Tipo de Seguro': tipo_name,
                    'Nombre del cliente': nombre_cli,
                    'Fecha de inicio': p.fechaInicio,
                    'Fecha de fin': p.fechaFin,
                    'Prima mensual': f'${p.primaMensual:,.2f}',
                    'Monto total asegurado': f'${p.montoAsegurado:,.2f}',
                    'Estado': catalogos['ep_id_n'].get(p.idEstadoPoliza, '-')
                })
                
            df_polizas = pd.DataFrame(todas_filas)
            
            # Filtro dinámico
            tipos_disponibles = ["Todos"] + sorted(list(df_polizas["Tipo de Seguro"].unique()))
            tipo_seleccionado = st.selectbox("🛡️ Filtrar por Tipo de Seguro:", options=tipos_disponibles, index=0)
            
            if tipo_seleccionado != "Todos":
                df_filtrado = df_polizas[df_polizas["Tipo de Seguro"] == tipo_seleccionado]
            else:
                df_filtrado = df_polizas
                
            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
            st.caption(f'Total de pólizas mostradas: {len(df_filtrado)}')

        st.divider()

        # Listado de Pólizas Vencidas
        st.subheader('Listado de Pólizas Vencidas')
        polizas_vencidas = [p for p in lista_polizas if p.fechaFin < hoy]
        if polizas_vencidas:
            filas_vencidas = []
            for p in polizas_vencidas:
                cliente = catalogos['cli_id_obj'].get(p.idCliente)
                nombre_cli = f'{cliente.nombre} {cliente.apellidos}' if cliente else 'Desconocido'
                filas_vencidas.append({
                    'Número de póliza': p.id,
                    'Nombre del cliente': nombre_cli,
                    'Tipo de seguro': catalogos['ts_id_n'].get(p.idTipoSeguro, '-'),
                    'Fecha de inicio': p.fechaInicio,
                    'Fecha de fin': p.fechaFin,
                    'Monto total asegurado': f'${p.montoAsegurado:,.2f}'
                })
            st.dataframe(pd.DataFrame(filas_vencidas), hide_index=True, use_container_width=True)
            st.caption(f'Total pólizas vencidas: {len(polizas_vencidas)}')
        else:
            st.info('No hay pólizas vencidas.')

        st.divider()

        # Resumen de Pólizas por Tipo de Seguro
        st.subheader('Resumen de Pólizas por Tipo de Seguro')
        id_activa = catalogos['ep_n_id'].get('Activa')
        if id_activa:
            resumen_tipo = {}
            for p in lista_polizas:
                if p.idEstadoPoliza == id_activa:
                    tipo = catalogos['ts_id_n'].get(p.idTipoSeguro, 'Desconocido')
                    if tipo not in resumen_tipo:
                        resumen_tipo[tipo] = {'cantidad': 0, 'primas': 0.0, 'monto': 0.0}
                    resumen_tipo[tipo]['cantidad'] += 1
                    resumen_tipo[tipo]['primas'] += float(p.primaMensual)
                    resumen_tipo[tipo]['monto'] += float(p.montoAsegurado)
            if resumen_tipo:
                filas_resumen = []
                for tipo, datos in resumen_tipo.items():
                    filas_resumen.append({
                        'Tipo de seguro': tipo,
                        'Cantidad de pólizas activas': datos['cantidad'],
                        'Total de primas mensuales': f'${datos["primas"]:,.2f}',
                        'Total de monto asegurado': f'${datos["monto"]:,.2f}'
                    })
                st.dataframe(pd.DataFrame(filas_resumen), hide_index=True, use_container_width=True)
            else:
                st.info('No hay pólizas activas.')
        else:
            st.warning('No se encontró el estado "Activa" en el catálogo.')
    
    # Tab 2: Nueva Poliza
    with tab2:
        st.subheader('Nueva Poliza')
        if not catalogos['cli_etq']:
            st.warning('No hay clientes registrados.')
        else:
            with st.form('form_nueva_poliza'):
                cliente_sel = st.selectbox('Cliente', catalogos['cli_etq'])
                tipo_seguro_sel = st.selectbox('Tipo de Seguro', list(catalogos['ts_n_id'].keys()))
                col1, col2 = st.columns(2)
                fecha_inicio = col1.date_input('Fecha de Inicio')
                fecha_fin = col2.date_input('Fecha de Fin')
                col3, col4 = st.columns(2)
                prima = col3.number_input('Prima Mensual ($)', min_value=0.01, format='%.2f')
                monto = col4.number_input('Monto Asegurado ($)', min_value=0.01, format='%.2f')
                estado = st.selectbox('Estado', list(catalogos['ep_n_id'].keys()))
                motivo_nuevo = ''
                if estado == 'Cancelada':
                    motivo_nuevo = st.text_area('Motivo de cancelacion', placeholder='Ingrese el motivo...')
                if st.form_submit_button('Guardar Poliza', use_container_width=True):
                    try:
                        id_cliente = catalogos['cli_etq_id'][cliente_sel]
                        id_tipo_seguro = catalogos['ts_n_id'][tipo_seguro_sel]
                        id_estado = catalogos['ep_n_id'][estado]
                        validar_claves_foraneas_poliza(id_cliente, id_tipo_seguro, id_estado)
                        poliza = Poliza(
                            idTipoSeguro=id_tipo_seguro,
                            fechaInicio=fecha_inicio,
                            fechaFin=fecha_fin,
                            primaMensual=prima,
                            idEstadoPoliza=id_estado,
                            montoAsegurado=monto,
                            idCliente=id_cliente
                        )
                        nuevo_id = CrudPoliza().crear(poliza)
                        if estado == 'Cancelada' and motivo_nuevo.strip():
                            can_obj = PolizaCancelada(motivo=motivo_nuevo.strip(), idPoliza=nuevo_id)
                            CrudPolizaCancelada().crear(can_obj)
                        st.success('Poliza creada.')
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
    
    # Tab 3: Editar Poliza
    with tab3:
        st.subheader('Editar Poliza')
        if 'edit_poliza_page' not in st.session_state:
            st.session_state.edit_poliza_page = 0
        PAGE_SIZE = 10
        
        with st.form('form_buscar_poliza'):
            st.markdown('**Buscar Poliza para Editar**')
            col_bus1, col_bus2, col_bus3 = st.columns([2, 2, 1])
            busqueda_id = col_bus1.text_input('Por Nde Poliza')
            busqueda_cliente = col_bus2.text_input('Por Nombre de Cliente')
            busqueda_estado = col_bus3.selectbox('Por Estado', ['Todos'] + list(catalogos['ep_id_n'].values()))
            st.form_submit_button('Buscar', use_container_width=True, on_click=lambda: st.session_state.update(active_tab_poliza='Editar Poliza'))
        
        filtros = {}
        if busqueda_id:
            try:
                filtros['idPoliza'] = int(busqueda_id)
            except ValueError:
                st.error('Nde Poliza debe ser numero')
                filtros['idPoliza'] = -1
        if busqueda_estado != 'Todos':
            filtros['idEstadoPoliza'] = catalogos['ep_n_id'][busqueda_estado]
        
        lista_filtrada = []
        if busqueda_cliente:
            clientes_encontrados = CrudCliente().filtrar(nombre=busqueda_cliente)
            if clientes_encontrados:
                for cli in clientes_encontrados:
                    lista_filtrada.extend(CrudPoliza().filtrar(idCliente=cli.id, **filtros))
        else:
            total_polizas = CrudPoliza().contar(**filtros)
            if total_polizas > 0:
                total_pages = (total_polizas + PAGE_SIZE - 1) // PAGE_SIZE
                if st.session_state.edit_poliza_page >= total_pages:
                    st.session_state.edit_poliza_page = max(0, total_pages - 1)
                col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
                with col_pag1:
                    if st.button('← Anterior', key='edit_pol_ant', disabled=st.session_state.edit_poliza_page <= 0, on_click=lambda: st.session_state.update(active_tab_poliza='Editar Poliza')):
                        st.session_state.edit_poliza_page -= 1
                        st.rerun()
                with col_pag2:
                    st.markdown(f'<center>Pagina {st.session_state.edit_poliza_page + 1} de {total_pages} ({total_polizas} polizas)</center>', unsafe_allow_html=True)
                with col_pag3:
                    if st.button('Siguiente →', key='edit_pol_sig', disabled=st.session_state.edit_poliza_page >= total_pages - 1, on_click=lambda: st.session_state.update(active_tab_poliza='Editar Poliza')):
                        st.session_state.edit_poliza_page += 1
                        st.rerun()
                lista_filtrada = CrudPoliza().filtrar(limit=PAGE_SIZE, offset=st.session_state.edit_poliza_page * PAGE_SIZE, **filtros)
        
        if lista_filtrada:
            opciones_sel = {
                f"Poliza #{p.id} | {catalogos['cli_id_obj'][p.idCliente].nombre} {catalogos['cli_id_obj'][p.idCliente].apellidos} | {catalogos['ts_id_n'].get(p.idTipoSeguro, '-')} | {catalogos['ep_id_n'].get(p.idEstadoPoliza, '-')}": p
                for p in lista_filtrada if p.idCliente in catalogos['cli_id_obj']
            }
            if opciones_sel:
                sel = st.selectbox('Seleccione la póliza', list(opciones_sel.keys()))
                poliza_sel = opciones_sel[sel]
                st.divider()
                
                # Show read-only details of the selected policy
                st.markdown(f"### Detalles de la Póliza Seleccionada")
                p_d1, p_d2 = st.columns(2)
                p_d1.markdown(f"**Número de Póliza:** #{poliza_sel.id}")
                cliente_pol = catalogos['cli_id_obj'].get(poliza_sel.idCliente)
                p_d1.markdown(f"**Cliente:** {cliente_pol.nombre} {cliente_pol.apellidos}" if cliente_pol else "**Cliente:** Desconocido")
                p_d1.markdown(f"**Tipo de Seguro:** {catalogos['ts_id_n'].get(poliza_sel.idTipoSeguro, 'N/A')}")
                p_d2.markdown(f"**Vigencia:** Desde {poliza_sel.fechaInicio} hasta {poliza_sel.fechaFin}")
                p_d2.markdown(f"**Prima Mensual:** ${poliza_sel.primaMensual:,.2f}")
                p_d2.markdown(f"**Monto Asegurado:** ${poliza_sel.montoAsegurado:,.2f}")
                p_d2.markdown(f"**Estado Actual:** {catalogos['ep_id_n'].get(poliza_sel.idEstadoPoliza, 'N/A')}")
                
                if st.button(" Iniciar Edición / Eliminación", use_container_width=True, type="primary"):
                    st.session_state.editing_poliza_id = poliza_sel.id
                    st.session_state.editing_active = True
                    st.rerun()
            else:
                st.info('No hay resultados.')
        else:
            st.info('No se encontraron polizas.')
    
    # Tab 4: Coberturas
    with tab4:
        st.subheader('Gestion de Coberturas')
        if not lista_polizas:
            st.info('No hay polizas.')
        else:
            opciones_cob = {
                f"Poliza #{p.id} | {catalogos['cli_id_obj'][p.idCliente].nombre} {catalogos['cli_id_obj'][p.idCliente].apellidos} | {catalogos['ts_id_n'].get(p.idTipoSeguro, '-')}": p
                for p in lista_polizas if p.idCliente in catalogos['cli_id_obj']
            }
            sel_cob = st.selectbox('Seleccione la poliza', list(opciones_cob.keys()), key='cob_sel')
            poliza_cob = opciones_cob[sel_cob]
            
            if st.session_state.get('editando_cob_poliza') != poliza_cob.id:
                st.session_state.pop('editando_cob_id', None)
                st.session_state.pop('editando_cob_poliza', None)
            st.divider()
            
            col_izq, col_der = st.columns([2, 1])
            with col_izq:
                editando_id = st.session_state.get('editando_cob_id')
                if editando_id is None:
                    st.markdown('**Añadir Cobertura**')
                    with st.form('form_nueva_cob'):
                        nueva_desc = st.text_input('Descripcion', placeholder='Descripcion...')
                        nuevo_mont = st.number_input('Monto ($)', min_value=0.01, format='%.2f')
                        if st.form_submit_button('Añadir', use_container_width=True):
                            if not nueva_desc.strip():
                                st.error('La descripcion no puede estar vacia.')
                            else:
                                try:
                                    cob_obj = Cobertura(descripcion=nueva_desc.strip())
                                    nuevo_id = CrudCobertura().crear(cob_obj)
                                    rel_obj = PolizaCobertura(idPoliza=poliza_cob.id, idCobertura=nuevo_id, monto=nuevo_mont)
                                    CrudPolizaCobertura().crear(rel_obj)
                                    st.success('Cobertura añadida.')
                                    st.rerun()
                                except ValueError as e:
                                    st.error(str(e))
                else:
                    cob_editando = CrudCobertura().obtener(editando_id)
                    rel_editando = CrudPolizaCobertura().obtener(poliza_cob.id, editando_id)
                    st.markdown('**Editar Cobertura**')
                    with st.form('form_editar_cob'):
                        ed_desc = st.text_input('Descripcion', value=cob_editando.descripcion if cob_editando else '')
                        ed_mont = st.number_input('Monto ($)', value=float(rel_editando.monto) if rel_editando else 0.01, min_value=0.01, format='%.2f')
                        col_upd, col_can = st.columns(2)
                        btn_upd = col_upd.form_submit_button('Guardar', use_container_width=True)
                        btn_can = col_can.form_submit_button('Cancelar', use_container_width=True)
                    if btn_upd:
                        if not ed_desc.strip():
                            st.error('La descripcion no puede estar vacia.')
                        else:
                            try:
                                cob_editando.descripcion = ed_desc.strip()
                                CrudCobertura().actualizar(cob_editando)
                                rel_editando.monto = ed_mont
                                CrudPolizaCobertura().actualizar(rel_editando)
                                st.session_state.pop('editando_cob_id', None)
                                st.session_state.pop('editando_cob_poliza', None)
                                st.success('Cobertura actualizada.')
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))
                    if btn_can:
                        st.session_state.pop('editando_cob_id', None)
                        st.session_state.pop('editando_cob_poliza', None)
                        st.rerun()
            
            with col_der:
                st.markdown('**Coberturas Actuales**')
                relaciones = CrudPolizaCobertura().filtrar(idPoliza=poliza_cob.id)
                if not relaciones:
                    st.info('No tiene coberturas.')
                else:
                    for r in relaciones:
                        c_info = CrudCobertura().obtener(r.idCobertura)
                        descripcion = c_info.descripcion if c_info else f'Cobertura #{r.idCobertura}'
                        with st.expander(f'{descripcion} — ${r.monto:,.2f}', expanded=True):
                            col_ed, col_el = st.columns(2)
                            if col_ed.button('Editar', key=f'edit_cob_{poliza_cob.id}_{r.idCobertura}', use_container_width=True):
                                st.session_state['editando_cob_id'] = r.idCobertura
                                st.session_state['editando_cob_poliza'] = poliza_cob.id
                                st.rerun()
                            if col_el.button('Eliminar', key=f'del_cob_{poliza_cob.id}_{r.idCobertura}', use_container_width=True):
                                with Database() as db:
                                    db.execute('DELETE FROM poliza_cobertura WHERE idpoliza=%s AND idcobertura=%s', (poliza_cob.id, r.idCobertura))
                                    db.execute('DELETE FROM cobertura WHERE idcobertura=%s', (r.idCobertura,))
                                    st.rerun()
    
    # Tab 5: Pagos (NUEVO)
    with tab5:
        st.subheader('Gestion de Pagos')
        if not lista_polizas:
            st.info('No hay polizas.')
        else:
            opciones_pago = {
                f"Poliza #{p.id} | {catalogos['cli_id_obj'][p.idCliente].nombre} {catalogos['cli_id_obj'][p.idCliente].apellidos} | {catalogos['ts_id_n'].get(p.idTipoSeguro, '-')}": p
                for p in lista_polizas if p.idCliente in catalogos['cli_id_obj']
            }
            sel_pago = st.selectbox('Seleccione la poliza', list(opciones_pago.keys()), key='pago_sel')
            poliza_pago = opciones_pago[sel_pago]
            st.divider()
            
            col_lista, col_form = st.columns([2, 1])
            
            with col_lista:
                st.markdown('**Listado de Pagos**')
                pagos = CrudPago().filtrar(idPoliza=poliza_pago.id)
                if not pagos:
                    st.info('Esta poliza no tiene pagos.')
                else:
                    filas_pagos = []
                    for p in pagos:
                        filas_pagos.append({
                            'ID': p.id,
                            'Fecha': p.fechaPago.strftime('%d/%m/%Y') if p.fechaPago else 'N/A',
                            'Monto Pagado': f'${p.montoPagado:,.2f}'
                        })
                    st.dataframe(pd.DataFrame(filas_pagos), hide_index=True, use_container_width=True)
                    st.caption(f'Total pagos: {len(pagos)}')
                    
                    if st.session_state.get('editando_pago_id'):
                        pago_edit = CrudPago().obtener(st.session_state['editando_pago_id'])
                        if pago_edit:
                            st.divider()
                            st.markdown('**Editar Pago**')
                            with st.form('form_editar_pago'):
                                nueva_fecha = st.date_input('Fecha de Pago', value=pago_edit.fechaPago)
                                nuevo_monto = st.number_input('Monto Pagado ($)', value=float(pago_edit.montoPagado), min_value=0.01, format='%.2f')
                                col_upd_p, col_del_p, col_can_p = st.columns(3)
                                btn_upd_p = col_upd_p.form_submit_button('Actualizar', use_container_width=True)
                                btn_del_p = col_del_p.form_submit_button('Eliminar', use_container_width=True)
                                btn_can_p = col_can_p.form_submit_button('Cancelar', use_container_width=True)
                            if btn_upd_p:
                                try:
                                    pago_edit.fechaPago = nueva_fecha
                                    pago_edit.montoPagado = nuevo_monto
                                    CrudPago().actualizar(pago_edit)
                                    st.session_state.pop('editando_pago_id', None)
                                    st.success('Pago actualizado.')
                                    st.rerun()
                                except ValueError as e:
                                    st.error(str(e))
                            if btn_del_p:
                                CrudPago().eliminar(pago_edit.id)
                                st.session_state.pop('editando_pago_id', None)
                                st.success('Pago eliminado.')
                                st.rerun()
                            if btn_can_p:
                                st.session_state.pop('editando_pago_id', None)
                                st.rerun()
            
            with col_form:
                if not st.session_state.get('editando_pago_id'):
                    st.markdown('**Registrar Nuevo Pago**')
                    with st.form('form_nuevo_pago'):
                        fecha_pago = st.date_input('Fecha de Pago', value=datetime.now().date())
                        monto_pago = st.number_input('Monto Pagado ($)', min_value=0.01, format='%.2f')
                        if st.form_submit_button('Registrar Pago', use_container_width=True):
                            try:
                                pago_obj = Pago(idPoliza=poliza_pago.id, fechaPago=fecha_pago, montoPagado=monto_pago)
                                CrudPago().crear(pago_obj)
                                st.success('Pago registrado.')
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))
                
                if pagos:
                    st.divider()
                    st.markdown('**Editar Pago Existente**')
                    opciones_edit_pago = {
                        f"Pago #{p.id} - ${p.montoPagado:,.2f} ({p.fechaPago.strftime('%d/%m/%Y') if p.fechaPago else 'N/A'})": p.id
                        for p in pagos
                    }
                    pago_a_editar = st.selectbox('Seleccione pago a editar', list(opciones_edit_pago.keys()))
                    if st.button('Cargar Pago', use_container_width=True):
                        st.session_state['editando_pago_id'] = opciones_edit_pago[pago_a_editar]
                        st.rerun()
