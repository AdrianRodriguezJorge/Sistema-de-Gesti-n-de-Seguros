import streamlit as st
import pandas as pd
from datetime import datetime
from db.queries_pago import CrudPago
from db.queries_agencia import CrudAgencia
from db.queries_cliente import CrudCliente
from db.queries_poliza import CrudPoliza
from db.queries_reclamacion import CrudReclamacion
from db.queries_reaseguradora import CrudReaseguradora
from db.queries_catalogos import CrudPais, CrudTipoSeguro, CrudTipoSiniestro, CrudTipoReaseguro, CrudEstadoPoliza, CrudEstadoReclamacion
from db.queries_reporte_generado import CrudReporteGenerado
import json

def _mostrar_reportes_guardados(nombre_prefix):
    crud = CrudReporteGenerado()
    reportes = [r for r in crud.obtener_todos() if r['nombre_reporte'].startswith(nombre_prefix)]
    if reportes:
        st.divider()
        st.subheader('Reportes Guardados')
        for rep in reportes:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.text(f"{rep['nombre_reporte']} - {rep['fecha_creacion'].strftime('%d/%m/%Y')}")
            with col2:
                if st.button('Ver', key=f"view_{rep['id_reporte']}", use_container_width=True):
                    st.session_state[f'rep_view_{nombre_prefix}'] = rep['id_reporte']
                    st.rerun()
            with col3:
                if st.button('Eliminar', key=f"del_{rep['id_reporte']}", use_container_width=True):
                    crud.eliminar(rep['id_reporte'])
                    if st.session_state.get(f'rep_view_{nombre_prefix}') == rep['id_reporte']:
                        del st.session_state[f'rep_view_{nombre_prefix}']
                    st.success('Reporte eliminado.')
                    st.rerun()
        
        rep_id = st.session_state.get(f'rep_view_{nombre_prefix}')
        if rep_id:
            rep = crud.obtener(rep_id)
            if rep:
                st.divider()
                st.subheader(f"Visualizando: {rep['nombre_reporte']}")
                datos = rep['datos_reporte'] if isinstance(rep['datos_reporte'], dict) else json.loads(rep['datos_reporte'])
                
                if 'Ingresos Mensuales' in rep['nombre_reporte']:
                    st.metric('Ingreso Total Anual', f"${datos.get('total_anual', 0):,.2f}")
                    if datos.get('ingresos'):
                        filas = [{'Mes': i['mes'], 'Ingreso Mensual': f"${i['ingreso']:,.2f}"} for i in datos['ingresos']]
                        st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)
                
                elif 'Ficha Agencia' in rep['nombre_reporte']:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown('**Datos de la Agencia**')
                        st.text(f'Nombre: {datos.get("nombre", "")}')
                        st.text(f'Dirección Postal: {datos.get("direccion", "")}')
                        st.text(f'Teléfono: {datos.get("telefono", "")}')
                        st.text(f'Email: {datos.get("email", "")}')
                    with col2:
                        st.markdown('**Directivos**')
                        st.text(f'Director General: {datos.get("director_general", "")}')
                        st.text(f'Jefe de Seguros: {datos.get("jefe_seguros", "")}')
                        st.text(f'Jefe de Reclamaciones: {datos.get("jefe_reclamaciones", "")}')
                
                elif 'Ficha Cliente' in rep['nombre_reporte']:
                    cli = datos.get('cliente', {})
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown('**Información del Cliente**')
                        st.text(f'Nombre: {cli.get("nombre", "")} {cli.get("apellidos", "")}')
                        st.text(f'No. Identificación: {cli.get("identificacion", "")}')
                        st.text(f'Teléfono: {cli.get("telefono", "")}')
                        st.text(f'Email: {cli.get("correo", "")}')
                        st.text(f'País: {cli.get("pais", "")}')
                    with col2:
                        st.markdown('**Resumen de Pólizas**')
                        st.metric('Pólizas Activas', datos.get('polizas_activas', 0))
                        st.metric('Valor Total Primas Pagadas', f"${datos.get('total_primas', 0):,.2f}")
                    st.metric('Total Reclamaciones', datos.get('reclamaciones', 0))
                
                elif 'Ficha Reaseguradora' in rep['nombre_reporte']:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown('**Datos de la Reaseguradora**')
                        st.text(f'Nombre: {datos.get("nombre", "")}')
                        st.text(f"País de Origen: {datos.get('pais', '')}")
                        st.text(f"Tipo de Reaseguro: {datos.get('tipo_reaseguro', '')}")
                    with col2:
                        st.markdown('**Participación en Tipos de Seguro**')
                        for part in datos.get('participaciones', []):
                            st.text(f"{part.get('tipo_seguro', 'N/A')}: {part.get('porcentaje', 0)}%")
                
                elif 'Pólizas por Período' in rep['nombre_reporte']:
                    st.caption(f"Período: {datos.get('fecha_inicio', '')} al {datos.get('fecha_fin', '')}")
                    if datos.get('polizas'):
                        filas = [{'No. Póliza': p['id'], 'Cliente': p.get('cliente', 'N/A'), 'Tipo Seguro': p.get('tipo_seguro', 'N/A'), 'Fecha Inicio': p.get('fecha_inicio', 'N/A'), 'Fecha Fin': p.get('fecha_fin', 'N/A'), 'Prima Mensual': f"${p.get('prima', 0):,.2f}", 'Estado': p.get('estado', 'N/A')} for p in datos['polizas']]
                        st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)
                        st.caption(f'Total de pólizas: {len(datos["polizas"])}')
                
                elif 'Estado Reclamaciones' in rep['nombre_reporte']:
                    st.caption(f"Período: {datos.get('fecha_inicio', '')} al {datos.get('fecha_fin', '')}")
                    if datos.get('reclamaciones'):
                        filas = [{'No. Reclamación': r['id'], 'Cliente': r.get('cliente', 'N/A'), 'Monto Reclamado': f"${r.get('monto_reclamado', 0):,.2f}", 'Monto Indemnizado': f"${r.get('monto_indemnizado', 0):,.2f}", 'Estado': r.get('estado', 'N/A')} for r in datos['reclamaciones']]
                        st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)
                        st.caption(f'Total de reclamaciones: {len(datos["reclamaciones"])}')
                
                if st.button('Cerrar Reporte', key=f'close_{rep["id_reporte"]}', use_container_width=True):
                    del st.session_state[f'rep_view_{nombre_prefix}']
                    st.rerun()

def pagina_reportes():
    st.title('Reportes')
    st.divider()
    crud_reportes = CrudReporteGenerado()
    
    if 'rep_view_Ingresos Mensuales' not in st.session_state:
        st.session_state['rep_view_Ingresos Mensuales'] = None
    if 'rep_view_Ficha Agencia' not in st.session_state:
        st.session_state['rep_view_Ficha Agencia'] = None
    if 'rep_view_Ficha Cliente' not in st.session_state:
        st.session_state['rep_view_Ficha Cliente'] = None
    if 'rep_view_Ficha Reaseguradora' not in st.session_state:
        st.session_state['rep_view_Ficha Reaseguradora'] = None
    if 'rep_view_Pólizas por Período' not in st.session_state:
        st.session_state['rep_view_Pólizas por Período'] = None
    if 'rep_view_Estado Reclamaciones' not in st.session_state:
        st.session_state['rep_view_Estado Reclamaciones'] = None
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        'Ingresos Mensuales', 'Ficha Agencia', 'Ficha Cliente', 
        'Ficha Reaseguradora', 'Pólizas por Período', 'Estado Reclamaciones'
    ])
    
    with tab1:
        st.subheader('Listado de Ingresos Mensuales')
        st.caption(f"Fecha del reporte: {datetime.now().strftime('%d/%m/%Y')}")
        año_actual = datetime.now().year
        año = st.selectbox('Seleccione el año', [año_actual, año_actual - 1, año_actual - 2])
        
        crud_pago = CrudPago()
        with st.spinner('Cargando ingresos...'):
            ingresos = crud_pago.obtener_ingresos_mensuales(año)
            total_anual = crud_pago.obtener_total_anual(año)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric('Ingreso Total Anual', f'${total_anual:,.2f}' if total_anual else '$0.00')
        with col2:
            st.metric('Total Meses con Ingresos', len(ingresos))
        with col3:
            promedio = sum((i['ingreso_mensual'] for i in ingresos)) / len(ingresos) if ingresos else 0
            st.metric('Promedio Mensual', f'${promedio:,.2f}')
        
        st.divider()
        if ingresos:
            st.subheader('Desglose Mensual')
            filas = [{'Mes': i['nombre_mes'].strip(), 'Ingreso Mensual': f"${i['ingreso_mensual']:,.2f}"} for i in ingresos]
            st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)
            
            if st.checkbox('Mostrar gráfico de ingresos'):
                df = pd.DataFrame(filas)
                df['Ingreso Numerico'] = df['Ingreso Mensual'].str.replace('$', '').str.replace(',', '').astype(float)
                st.bar_chart(df.set_index('Mes')['Ingreso Numerico'])
            
            if st.button('Generar Reporte', key='gen_ingresos', use_container_width=True):
                datos = {
                    'año': año,
                    'total_anual': float(total_anual) if total_anual else 0,
                    'ingresos': [{'mes': i['nombre_mes'].strip(), 'ingreso': float(i['ingreso_mensual'])} for i in ingresos]
                }
                crud_reportes.crear(f'Ingresos Mensuales {año}', datos)
                st.success('Reporte guardado con la fecha de hoy.')
                st.rerun()
        else:
            st.info(f'No hay ingresos registrados para el año {año}.')
        _mostrar_reportes_guardados('Ingresos Mensuales')
    
    with tab2:
        st.subheader('Ficha de la Agencia de Seguros')
        st.caption(f"Fecha del reporte: {datetime.now().strftime('%d/%m/%Y')}")
        crud_agencia = CrudAgencia()
        agencias = crud_agencia.obtener_todos()
        
        if not agencias:
            st.warning('No hay agencia registrada.')
        else:
            agencia = agencias[0]
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('**Datos de la Agencia**')
                st.text(f'Nombre: {agencia.nombre}')
                st.text(f'Dirección Postal: {agencia.direccion}')
                st.text(f'Teléfono: {agencia.telefono}')
                st.text(f'Email: {agencia.email}')
            with col2:
                st.markdown('**Directivos**')
                st.text(f'Director General: {agencia.directorGeneral}')
                st.text(f'Jefe de Seguros: {agencia.jefeSeguros}')
                st.text(f'Jefe de Reclamaciones: {agencia.jefeReclamaciones}')
            
            if st.button('Generar Reporte', key='gen_agencia', use_container_width=True):
                datos = {
                    'nombre': agencia.nombre,
                    'direccion': agencia.direccion,
                    'telefono': agencia.telefono,
                    'email': agencia.email,
                    'director_general': agencia.directorGeneral,
                    'jefe_seguros': agencia.jefeSeguros,
                    'jefe_reclamaciones': agencia.jefeReclamaciones
                }
                crud_reportes.crear('Ficha Agencia', datos)
                st.success('Reporte guardado con la fecha de hoy.')
                st.rerun()
        _mostrar_reportes_guardados('Ficha Agencia')
    
    with tab3:
        st.subheader('Ficha de un Cliente Determinado')
        st.caption(f"Fecha del reporte: {datetime.now().strftime('%d/%m/%Y')}")
        crud_cliente = CrudCliente()
        clientes = crud_cliente.obtener_todos()
        
        if not clientes:
            st.warning('No hay clientes registrados.')
        else:
            cliente_sel = st.selectbox('Seleccione un cliente', options=clientes, format_func=lambda x: f'{x.nombre} {x.apellidos} - {x.noIdentificacion}')
            if cliente_sel:
                cliente = cliente_sel
                pais = CrudPais().obtener(cliente.idPais)
                polizas_cli = [p for p in CrudPoliza().obtener_todos() if p.idCliente == cliente.id]
                polizas_activas = [p for p in polizas_cli if p.idEstadoPoliza == 1]
                pagos = CrudPago().obtener_todos()
                total_primas = sum(p.montoPagado for p in pagos if any(pol.id == p.idPoliza for pol in polizas_cli))
                
                reclamaciones = []
                for pol in polizas_cli:
                    reclamaciones.extend([r for r in CrudReclamacion().obtener_todos() if r.idPoliza == pol.id])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('**Información del Cliente**')
                    st.text(f'Nombre: {cliente.nombre} {cliente.apellidos}')
                    st.text(f'No. Identificación: {cliente.noIdentificacion}')
                    st.text(f'Teléfono: {cliente.telefono}')
                    st.text(f'Email: {cliente.correo}')
                    st.text(f'Dirección Postal: {cliente.dirPostal}')
                    st.text(f"País: {pais.nombre if pais else 'N/A'}")
                with col2:
                    st.markdown('**Resumen de Pólizas**')
                    st.metric('Pólizas Activas', len(polizas_activas))
                    st.metric('Valor Total Primas Pagadas', f'${total_primas:,.2f}')
                
                if reclamaciones:
                    st.divider()
                    st.markdown('**Listado de Reclamaciones**')
                    filas_rec = []
                    for r in reclamaciones:
                        pol = next((p for p in CrudPoliza().obtener_todos() if p.id == r.idPoliza), None)
                        ts_obj = CrudTipoSeguro().obtener(pol.idTipoSeguro) if pol else None
                        filas_rec.append({
                            'No. Reclamación': r.id,
                            'Tipo Seguro': ts_obj.nombre if ts_obj else 'N/A',
                            'Fecha Siniestro': r.fechaSiniestro.strftime('%d/%m/%Y') if r.fechaSiniestro else 'N/A',
                            'Monto Reclamado': f'${r.montoReclamado:,.2f}',
                            'Monto Indemnizado': f'${r.montoIndemnizado:,.2f}' if r.montoIndemnizado else '$0.00',
                            'Estado': r.idEstadoReclamacion
                        })
                    st.dataframe(pd.DataFrame(filas_rec), hide_index=True, use_container_width=True)
                else:
                    st.info('El cliente no tiene reclamaciones registradas.')
                
                if st.button('Generar Reporte', key='gen_cliente', use_container_width=True):
                    datos = {
                        'cliente': {
                            'nombre': cliente.nombre,
                            'apellidos': cliente.apellidos,
                            'identificacion': cliente.noIdentificacion,
                            'telefono': cliente.telefono,
                            'correo': cliente.correo,
                            'pais': pais.nombre if pais else 'N/A'
                        },
                        'polizas_activas': len(polizas_activas),
                        'total_primas': float(total_primas),
                        'reclamaciones': len(reclamaciones)
                    }
                    crud_reportes.crear(f'Ficha Cliente {cliente.nombre} {cliente.apellidos}', datos)
                    st.success('Reporte guardado con la fecha de hoy.')
                    st.rerun()
        _mostrar_reportes_guardados('Ficha Cliente')
    
    with tab4:
        st.subheader('Ficha de una Reaseguradora Asociada')
        st.caption(f"Fecha del reporte: {datetime.now().strftime('%d/%m/%Y')}")
        crud_reaseg = CrudReaseguradora()
        reaseguradoras = crud_reaseg.obtener_todos()
        
        if not reaseguradoras:
            st.warning('No hay reaseguradoras registradas.')
        else:
            reas_sel = st.selectbox('Seleccione una reaseguradora', options=reaseguradoras, format_func=lambda x: f'{x.nombre}')
            if reas_sel:
                reaseguradora = reas_sel
                pais = CrudPais().obtener(reaseguradora.idPais)
                tipo_reaseguro = CrudTipoReaseguro().obtener(reaseguradora.idTipoReaseguro)
                
                from db.queries_participacion_reaseguro import CrudParticipacionReaseguro
                participaciones = [p for p in CrudParticipacionReaseguro().obtener_todos() if p.idReaseguradora == reaseguradora.id]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('**Datos de la Reaseguradora**')
                    st.text(f'Nombre: {reaseguradora.nombre}')
                    st.text(f"País de Origen: {pais.nombre if pais else 'N/A'}")
                    st.text(f"Tipo de Reaseguro: {tipo_reaseguro.nombre if tipo_reaseguro else 'N/A'}")
                with col2:
                    st.markdown('**Participación en Tipos de Seguro**')
                    if participaciones:
                        for part in participaciones:
                            ts_obj = CrudTipoSeguro().obtener(part.idTipoSeguro)
                            st.text(f'{ts_obj.nombre if ts_obj else "N/A"}: {part.porcentaje}%')
                    else:
                        st.info('No tiene participaciones registradas.')
                
                if st.button('Generar Reporte', key='gen_reaseg', use_container_width=True):
                    datos = {
                        'nombre': reaseguradora.nombre,
                        'pais': pais.nombre if pais else 'N/A',
                        'tipo_reaseguro': tipo_reaseguro.nombre if tipo_reaseguro else 'N/A',
                        'participaciones': [{
                            'tipo_seguro': CrudTipoSeguro().obtener(p.idTipoSeguro).nombre if CrudTipoSeguro().obtener(p.idTipoSeguro) else 'N/A',
                            'porcentaje': float(p.porcentaje)
                        } for p in participaciones]
                    }
                    crud_reportes.crear(f'Ficha Reaseguradora {reaseguradora.nombre}', datos)
                    st.success('Reporte guardado con la fecha de hoy.')
                    st.rerun()
        _mostrar_reportes_guardados('Ficha Reaseguradora')
    
    with tab5:
        st.subheader('Reporte de Pólizas Emitidas en un Período')
        st.caption(f"Fecha del reporte: {datetime.now().strftime('%d/%m/%Y')}")
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input('Fecha de inicio', value=datetime.now().replace(day=1))
        with col2:
            fecha_fin = st.date_input('Fecha de fin', value=datetime.now())
        
        if st.button('Generar Reporte', key='gen_polizas', use_container_width=True):
            crud_pol = CrudPoliza()
            crud_cli = CrudCliente()
            crud_ts = CrudTipoSeguro()
            crud_ep = CrudEstadoPoliza()
            
            todas = crud_pol.obtener_todos()
            filtradas = [p for p in todas if fecha_inicio <= p.fechaInicio <= fecha_fin]
            
            if filtradas:
                filas = []
                for pol in filtradas:
                    cli = crud_cli.obtener(pol.idCliente)
                    ts = crud_ts.obtener(pol.idTipoSeguro)
                    ep = crud_ep.obtener(pol.idEstadoPoliza)
                    filas.append({
                        'No. Póliza': pol.id,
                        'Cliente': f'{cli.nombre} {cli.apellidos}' if cli else 'N/A',
                        'Tipo Seguro': ts.nombre if ts else 'N/A',
                        'Fecha Inicio': pol.fechaInicio.strftime('%d/%m/%Y') if pol.fechaInicio else 'N/A',
                        'Fecha Fin': pol.fechaFin.strftime('%d/%m/%Y') if pol.fechaFin else 'N/A',
                        'Prima Mensual': f'${pol.primaMensual:,.2f}',
                        'Estado': ep.nombre if ep else 'N/A'
                    })
                st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)
                st.caption(f'Total de pólizas encontradas: {len(filas)}')
                
                datos = {
                    'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
                    'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
                    'polizas': [{
                        'id': p.id,
                        'cliente': f'{crud_cli.obtener(p.idCliente).nombre if crud_cli.obtener(p.idCliente) else "N/A"} {crud_cli.obtener(p.idCliente).apellidos if crud_cli.obtener(p.idCliente) else ""}',
                        'tipo_seguro': crud_ts.obtener(p.idTipoSeguro).nombre if crud_ts.obtener(p.idTipoSeguro) else 'N/A',
                        'fecha_inicio': p.fechaInicio.strftime('%Y-%m-%d') if p.fechaInicio else 'N/A',
                        'fecha_fin': p.fechaFin.strftime('%Y-%m-%d') if p.fechaFin else 'N/A',
                        'prima': float(p.primaMensual),
                        'estado': crud_ep.obtener(p.idEstadoPoliza).nombre if crud_ep.obtener(p.idEstadoPoliza) else 'N/A'
                    } for p in filtradas]
                }
                crud_reportes.crear(f'Pólizas por Período {fecha_inicio.strftime("%d/%m/%Y")} - {fecha_fin.strftime("%d/%m/%Y")}', datos)
                st.success('Reporte guardado con la fecha de hoy.')
                st.rerun()
            else:
                st.info('No se encontraron pólizas en el período seleccionado.')
        _mostrar_reportes_guardados('Pólizas por Período')
    
    with tab6:
        st.subheader('Reporte de Estado de las Reclamaciones')
        st.caption(f"Fecha del reporte: {datetime.now().strftime('%d/%m/%Y')}")
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio_rec = st.date_input('Fecha siniestro desde', value=datetime.now().replace(day=1), key='rec_inicio')
        with col2:
            fecha_fin_rec = st.date_input('Fecha siniestro hasta', value=datetime.now(), key='rec_fin')
        
        if st.button('Generar Reporte ', key='gen_reclam', use_container_width=True):
            crud_rec = CrudReclamacion()
            crud_pol = CrudPoliza()
            crud_cli = CrudCliente()
            crud_ts = CrudTipoSeguro()
            crud_tsi = CrudTipoSiniestro()
            crud_er = CrudEstadoReclamacion()
            
            todas = crud_rec.obtener_todos()
            filtradas = [r for r in todas if r.fechaSiniestro and fecha_inicio_rec <= r.fechaSiniestro <= fecha_fin_rec]
            
            if filtradas:
                filas = []
                for rec in filtradas:
                    pol = crud_pol.obtener(rec.idPoliza)
                    cli = crud_cli.obtener(pol.idCliente) if pol else None
                    ts = crud_ts.obtener(pol.idTipoSeguro) if pol else None
                    tsi = crud_tsi.obtener(rec.idTipoSiniestro)
                    er = crud_er.obtener(rec.idEstadoReclamacion)
                    filas.append({
                        'No. Reclamación': rec.id,
                        'Cliente': f'{cli.nombre} {cli.apellidos}' if cli else 'N/A',
                        'No. Póliza': rec.idPoliza,
                        'Tipo Seguro': ts.nombre if ts else 'N/A',
                        'Tipo Siniestro': tsi.nombre if tsi else 'N/A',
                        'Fecha Siniestro': rec.fechaSiniestro.strftime('%d/%m/%Y') if rec.fechaSiniestro else 'N/A',
                        'Estado': er.nombre if er else 'N/A',
                        'Monto Reclamado': f'${rec.montoReclamado:,.2f}',
                        'Monto Indemnizado': f'${rec.montoIndemnizado:,.2f}' if rec.montoIndemnizado else '$0.00'
                    })
                st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)
                st.caption(f'Total de reclamaciones encontradas: {len(filas)}')
                
                datos = {
                    'fecha_inicio': fecha_inicio_rec.strftime('%Y-%m-%d'),
                    'fecha_fin': fecha_fin_rec.strftime('%Y-%m-%d'),
                    'reclamaciones': [{
                        'id': r.id,
                        'cliente': f'{crud_cli.obtener(crud_pol.obtener(r.idPoliza).idCliente).nombre if crud_pol.obtener(r.idPoliza) and crud_cli.obtener(crud_pol.obtener(r.idPoliza).idCliente) else "N/A"}',
                        'monto_reclamado': float(r.montoReclamado),
                        'monto_indemnizado': float(r.montoIndemnizado) if r.montoIndemnizado else 0,
                        'estado': crud_er.obtener(r.idEstadoReclamacion).nombre if crud_er.obtener(r.idEstadoReclamacion) else 'N/A'
                    } for r in filtradas]
                }
                crud_reportes.crear(f'Estado Reclamaciones {fecha_inicio_rec.strftime("%d/%m/%Y")} - {fecha_fin_rec.strftime("%d/%m/%Y")}', datos)
                st.success('Reporte guardado con la fecha de hoy.')
                st.rerun()
            else:
                st.info('No se encontraron reclamaciones en el período seleccionado.')
        _mostrar_reportes_guardados('Estado Reclamaciones')
