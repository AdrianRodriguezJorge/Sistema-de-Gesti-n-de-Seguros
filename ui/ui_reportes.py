# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
from db.conexionDB import Database
from db.queries_catalogos import listar_paises, listar_tipos_seguro, listar_estados_reclamacion
from db.queries_cliente import listar_clientes, obtener_cliente_por_id
from db.queries_poliza import listar_polizas, obtener_poliza_por_id
from db.queries_reaseguradora import obtener_reaseguradora_por_id
from db.queries_reclamacion import listar_reclamaciones
from db.queries_pago import total_pagado_por_cliente
from db.queries_agencia import obtener_agencia
from db.queries_reporte_generado import CrudReporteGenerado
from utils.generador_pdf import GeneradorPDF

def _renderizar_reporte_detalle(nombre_reporte, datos):
    """
    Renderiza de forma visual y premium los datos de cualquiera de los 17 reportes guardados históricamente.
    """
    tipo = datos.get('tipo_reporte', '')
    
    # 1. LISTADO DE CLIENTES
    if tipo == 'Listado de Clientes':
        st.info("Visualizando Listado de Clientes guardado en el historial.")
        paises_datos = datos.get('paises_datos', [])
        todas_filas = []
        for p in paises_datos:
            if p['clientes']:
                for c in p['clientes']:
                    todas_filas.append({
                        "ID": c["idcliente"],
                        "País": p["pais"],
                        "Nombre": c["nombre"],
                        "Apellidos": c["apellidos"],
                        "Pólizas activas": c.get("polizas_activas", 0),
                        "Total pagado ($)": c.get("total_pagado", 0.0)
                    })
                    
        if todas_filas:
            df = pd.DataFrame(todas_filas)
            paises_disponibles = ["Todos"] + sorted(list(df["País"].unique()))
            pais_sel = st.selectbox("🌍 Filtrar por País (Histórico):", options=paises_disponibles, index=0, key="hist_cli_pais")
            
            if pais_sel != "Todos":
                st.dataframe(df[df["País"] == pais_sel], use_container_width=True, hide_index=True)
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.caption("No hay clientes registrados en este reporte.")

    # 2. LISTADO DE PÓLIZAS
    elif tipo == 'Listado de Pólizas':
        st.info("Visualizando Listado de Pólizas guardado en el historial.")
        tipos_datos = datos.get('tipos_datos', [])
        todas_filas = []
        for t in tipos_datos:
            if t['polizas']:
                for p in t['polizas']:
                    todas_filas.append({
                        "Número": p["idpoliza"],
                        "Tipo de Seguro": t["tipo"],
                        "Cliente": p["cliente"],
                        "Fecha inicio": p["fechainicio"],
                        "Fecha fin": p["fechafin"],
                        "Prima mensual": p["primamensual"],
                        "Monto asegurado": p["montoasegurado"],
                        "Estado": p["estado"]
                    })
                    
        if todas_filas:
            df = pd.DataFrame(todas_filas)
            tipos_disponibles = ["Todos"] + sorted(list(df["Tipo de Seguro"].unique()))
            tipo_sel = st.selectbox("🛡️ Filtrar por Tipo de Seguro (Histórico):", options=tipos_disponibles, index=0, key="hist_pol_tipo")
            
            if tipo_sel != "Todos":
                st.dataframe(df[df["Tipo de Seguro"] == tipo_sel], use_container_width=True, hide_index=True)
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.caption("No hay pólizas registradas en este reporte.")

    # 3. LISTADO DE RECLAMACIONES
    elif tipo == 'Listado de Reclamaciones':
        st.info("Visualizando Listado de Reclamaciones registradas.")
        reclamaciones = datos.get('reclamaciones', [])
        if reclamaciones:
            df = pd.DataFrame(reclamaciones)
            df_display = df.rename(columns={
                "cliente": "Cliente",
                "idpoliza": "Número de póliza",
                "tipo_seguro": "Tipo de seguro",
                "idreclamacion": "Número de reclamación",
                "tipo_siniestro": "Tipo de siniestro",
                "fechasiniestro": "Fecha del siniestro",
                "montoreclamado": "Monto reclamado",
                "montoindemnizado": "Monto indemnizado",
                "estado": "Estado"
            })
            st.dataframe(df_display[[
                "Cliente", "Número de póliza", "Tipo de seguro", "Número de reclamación",
                "Tipo de siniestro", "Fecha del siniestro", "Monto reclamado", "Monto indemnizado", "Estado"
            ]], use_container_width=True, hide_index=True)
        else:
            st.caption("No hay reclamaciones registradas.")

    # 4. LISTADO DE REASEGURADORAS
    elif tipo == 'Listado de Reaseguradoras':
        st.info("Visualizando Listado de Reaseguradoras.")
        reaseguradoras = datos.get('reaseguradoras', [])
        if reaseguradoras:
            for rea in reaseguradoras:
                with st.expander(f"{rea['nombre']} ({rea['idreaseguradora']})"):
                    st.markdown(f"**País de origen:** {rea['pais']}")
                    st.markdown(f"**Tipo de reaseguro:** {rea['tipo_reaseguro']}")
                    st.markdown("**Participaciones:**")
                    if rea['participaciones']:
                        df = pd.DataFrame(rea['participaciones'])
                        df_display = df.rename(columns={
                            "tipo_seguro": "Tipo de seguro",
                            "porcentaje": "Porcentaje (%)"
                        })
                        st.dataframe(df_display, use_container_width=True, hide_index=True)
                    else:
                        st.caption("Esta reaseguradora no posee participaciones.")
        else:
            st.caption("No hay reaseguradoras registradas.")

    # 5. LISTADO DE PÓLIZAS VENCIDAS
    elif tipo == 'Listado de Pólizas Vencidas':
        st.info("Visualizando Listado de Pólizas Vencidas históricamente.")
        polizas = datos.get('polizas', [])
        if polizas:
            df = pd.DataFrame(polizas)
            df_display = df.rename(columns={
                "idpoliza": "Número de póliza",
                "cliente": "Cliente",
                "tipo_seguro": "Tipo de seguro",
                "fechainicio": "Fecha inicio",
                "fechafin": "Fecha fin",
                "montoasegurado": "Monto asegurado"
            })
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.success("No se encontraron pólizas vencidas en este reporte.")

    # 6. LISTADO DE CLIENTES CON PÓLIZAS CANCELADAS
    elif tipo == 'Listado de Clientes con Pólizas Canceladas':
        st.info("Visualizando Clientes con Pólizas Canceladas.")
        clientes = datos.get('clientes', [])
        if clientes:
            df = pd.DataFrame(clientes)
            df_display = df.rename(columns={
                "idcliente": "ID",
                "nombre": "Nombre",
                "apellidos": "Apellidos",
                "cantidad_canceladas": "Pólizas canceladas",
                "motivos": "Motivo(s) de cancelación"
            })
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.caption("No hay clientes con pólizas canceladas.")

    # 7. RESUMEN DE PÓLIZAS POR TIPO DE SEGURO
    elif tipo == 'Resumen de Pólizas por Tipo de Seguro':
        st.info("Visualizando Resumen de Pólizas Activas por Tipo de Seguro.")
        resumen = datos.get('resumen', [])
        if resumen:
            df = pd.DataFrame(resumen)
            st.dataframe(df, use_container_width=True, hide_index=True)

    # 8. RESUMEN DE RECLAMACIONES POR ESTADO
    elif tipo == 'Resumen de Reclamaciones por Estado':
        st.info("Visualizando Resumen de Reclamaciones por Estado.")
        resumen = datos.get('resumen', [])
        if resumen:
            df = pd.DataFrame(resumen)
            st.dataframe(df, use_container_width=True, hide_index=True)

    # 9. INGRESOS MENSUALES / INGRESOS POR PRIMAS
    elif tipo == 'Ingresos Mensuales':
        st.metric('Ingreso Total Anual', f"${datos.get('total_anual', 0):,.2f}")
        ingresos = datos.get('ingresos', [])
        if ingresos:
            filas = [{'Mes': i['mes'], 'Ingreso Mensual': f"${i['ingreso']:,.2f}"} for i in ingresos]
            st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)
            
            # Recrear gráfico de ingresos en el historial
            df_chart = pd.DataFrame(filas)
            df_chart['Ingreso'] = df_chart['Ingreso Mensual'].str.replace('$', '').str.replace(',', '').astype(float)
            st.bar_chart(df_chart.set_index('Mes')['Ingreso'])

    # 10. CLIENTES CON RECLAMACIONES APROBADAS
    elif tipo == 'Reporte de Clientes con Reclamaciones Aprobadas':
        st.info("Visualizando Clientes con Reclamaciones Aprobadas.")
        clientes = datos.get('clientes', [])
        if clientes:
            df = pd.DataFrame(clientes)
            df_display = df.rename(columns={
                "idcliente": "ID",
                "nombre": "Nombre",
                "apellidos": "Apellidos",
                "cantidad_aprobadas": "Reclamaciones aprobadas",
                "total_indemnizado": "Total indemnizado ($)"
            })
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.caption("No hay clientes con reclamaciones aprobadas.")

    # 11. CLIENTES CON RECLAMACIONES RECHAZADAS
    elif tipo == 'Reporte de Clientes con Reclamaciones Rechazadas':
        st.info("Visualizando Clientes con Reclamaciones Rechazadas.")
        clientes = datos.get('clientes', [])
        if clientes:
            df = pd.DataFrame(clientes)
            df_display = df.rename(columns={
                "idcliente": "ID",
                "nombre": "Nombre",
                "apellidos": "Apellidos",
                "cantidad_rechazadas": "Reclamaciones rechazadas",
                "motivos": "Motivo(s) del rechazo"
            })
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.caption("No hay clientes con reclamaciones rechazadas.")

    # 12. FICHA DE LA AGENCIA
    elif tipo == 'Ficha de la Agencia de Seguros':
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

    # 13. FICHA DE CLIENTE DETERMINADO
    elif tipo == 'Ficha de un Cliente Determinado':
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
        
        reclamaciones_list = datos.get('reclamaciones_list', [])
        if reclamaciones_list:
            st.divider()
            st.markdown('**Listado de Reclamaciones**')
            df = pd.DataFrame(reclamaciones_list)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("El cliente no tiene reclamaciones registradas.")

    # 14. FICHA DE REASEGURADORA ASOCIADA
    elif tipo == 'Ficha de una Reaseguradora Asociada':
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('**Datos de la Reaseguradora**')
            st.text(f'Nombre: {datos.get("nombre", "")}')
            st.text(f"País de Origen: {datos.get('pais', '')}")
        with col2:
            st.markdown('**Contacto y Tipo**')
            st.text(f"Tipo de Reaseguro: {datos.get('tipo_reaseguro', '')}")
            st.text(f"Email: {datos.get('email', 'No registrado')}")
        
        st.divider()
        st.markdown('**Participación en Ramos de Seguro**')
        participaciones = datos.get('participaciones', [])
        if participaciones:
            df = pd.DataFrame(participaciones)
            df_display = df.rename(columns={
                "tipo_seguro": "Tipo de seguro",
                "porcentaje": "Porcentaje (%)"
            })
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("No tiene participaciones de reaseguro registradas.")

    # 15. REPORTE DE PÓLIZAS EMITIDAS EN PERÍODO
    elif tipo == 'Reporte de Pólizas Emitidas en un Período':
        st.caption(f"Período: {datos.get('fecha_inicio', '')} al {datos.get('fecha_fin', '')}")
        polizas = datos.get('polizas', [])
        if polizas:
            filas = [{
                'No. Póliza': p.get('id'), 
                'Cliente': p.get('cliente', 'N/A'), 
                'Tipo Seguro': p.get('tipo_seguro', 'N/A'), 
                'Fecha Inicio': p.get('fecha_inicio', 'N/A'), 
                'Fecha Fin': p.get('fecha_fin', 'N/A'), 
                'Prima Mensual': f"${p.get('prima', 0):,.2f}", 
                'Estado': p.get('estado', 'N/A')
            } for p in polizas]
            st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)
            st.caption(f'Total de pólizas: {len(polizas)}')
        else:
            st.info("No hay pólizas registradas en este período.")

    # 16. REPORTE DE ESTADO DE RECLAMACIONES
    elif tipo == 'Reporte de Estado de las Reclamaciones':
        st.caption(f"Período: {datos.get('fecha_inicio', '')} al {datos.get('fecha_fin', '')}")
        reclamaciones = datos.get('reclamaciones', [])
        if reclamaciones:
            filas = [{
                'No. Reclamación': r.get('id'), 
                'Cliente': r.get('cliente', 'N/A'), 
                'Monto Reclamado': f"${r.get('monto_reclamado', 0):,.2f}", 
                'Monto Indemnizado': f"${r.get('monto_indemnizado', 0):,.2f}", 
                'Estado': r.get('estado', 'N/A')
            } for r in reclamaciones]
            st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)
            st.caption(f'Total de reclamaciones: {len(reclamaciones)}')
        else:
            st.info("No hay reclamaciones registradas en este período.")

def _mostrar_reportes_guardados_centralizado():
    """
    Muestra en una sola interfaz todos los reportes historizados persistidos en la base de datos,
    permitiendo verlos (con renderizado de alta fidelidad), descargarlos en PDF o eliminarlos.
    """
    crud = CrudReporteGenerado()
    reportes = crud.obtener_todos()
    
    if not reportes:
        st.info("No hay reportes guardados en el historial actualmente.")
        return
        
    st.caption("Seleccione un reporte de la lista para cargarlo y visualizar su información histórica o guardarla en PDF.")
    
    # Selector de Reportes Guardados
    opciones_reporte = {r['id_reporte']: f"{r['nombre_reporte']} ({r['fecha_creacion'].strftime('%d/%m/%Y %H:%M')})" for r in reportes}
    
    col_sel, col_btn_del = st.columns([4, 1])
    with col_sel:
        rep_id_seleccionado = st.selectbox("Seleccione un reporte del histórico:", options=list(opciones_reporte.keys()), format_func=lambda x: opciones_reporte[x], label_visibility="collapsed")
    with col_btn_del:
        if st.button(" Eliminar", use_container_width=True):
            crud.eliminar(rep_id_seleccionado)
            st.success("Reporte eliminado de la base de datos.")
            st.rerun()
            
    if rep_id_seleccionado:
        rep = crud.obtener(rep_id_seleccionado)
        if rep:
            st.divider()
            st.subheader(f"Visualizando: {rep['nombre_reporte']}")
            st.caption(f"Generado el: {rep['fecha_creacion'].strftime('%d/%m/%Y a las %H:%M')}")
            
            datos = rep['datos_reporte'] if isinstance(rep['datos_reporte'], dict) else json.loads(rep['datos_reporte'])
            
            # Botón de Descarga PDF
            try:
                pdf_bytes = GeneradorPDF.generar(rep['nombre_reporte'], datos)
                st.download_button(
                    label="Descargar Reporte en PDF",
                    data=pdf_bytes,
                    file_name=f"{rep['nombre_reporte'].replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    key=f"dl_pdf_hist_{rep['id_reporte']}",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error al generar el PDF: {e}")
            
            st.divider()
            
            # Renderizado específico del detalle del reporte
            _renderizar_reporte_detalle(rep['nombre_reporte'], datos)

def pagina_reportes():
    st.title("Reportes y Salidas del Sistema")
    st.caption("Generación de reportes generales, resúmenes estadísticos, fichas de agencia y consultas temporales parametrizadas.")
    st.divider()
    
    crud_reportes = CrudReporteGenerado()
    
    # 5 Categorías principales descritas en el Plan de Diseño Fiel al PDF
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Listados Generales",
        "📈 Resúmenes y Estadísticas",
        "👤 Fichas Especiales",
        "📅 Reportes Paramétricos",
        "📜 Historial Guardado"
    ])
    
    # =========================================================================
    # TAB 1: LISTADOS GENERALES
    # =========================================================================
    with tab1:
        st.subheader("Listados Generales de la Base de Datos")
        reporte_listados = st.selectbox(
            "Seleccione el listado general a consultar:",
            options=[
                "Listado de Clientes",
                "Listado de Pólizas",
                "Listado de Reclamaciones",
                "Listado de Reaseguradoras",
                "Listado de Pólizas Vencidas",
                "Listado de Clientes con Pólizas Canceladas"
            ],
            key="sb_listados"
        )
        st.divider()
        
        # 1. LISTADO DE CLIENTES
        if reporte_listados == "Listado de Clientes":
            st.caption(f"Fecha del listado: {date.today().strftime('%d/%m/%Y')}")
            paises = listar_paises()
            
            paises_datos_json = []
            todas_filas_ui = [] # Para la tabla única
            
            for pais in paises:
                with Database() as db:
                    clientes = db.fetch_all(
                        """
                        SELECT c.idcliente, c.nombre, c.apellidos,
                               COUNT(CASE WHEN ep.nombre = 'Activa' THEN 1 END) as polizas_activas,
                               COALESCE(SUM(p.monto_pagado), 0) as total_pagado
                        FROM cliente c
                        LEFT JOIN poliza po ON c.idcliente = po.idcliente
                        LEFT JOIN estado_poliza ep ON po.idestadopoliza = ep.idestadopoliza
                        LEFT JOIN pago p ON po.idpoliza = p.idpoliza
                        WHERE c.idpais = %s
                        GROUP BY c.idcliente, c.nombre, c.apellidos
                        ORDER BY c.apellidos;
                        """,
                        (pais["idpais"],)
                    )
                
                clientes_list = []
                if clientes:
                    for cli in clientes:
                        # Para el JSON jerárquico (preservar estructura del PDF)
                        clientes_list.append({
                            "idcliente": cli["idcliente"],
                            "nombre": cli["nombre"],
                            "apellidos": cli["apellidos"],
                            "polizas_activas": int(cli["polizas_activas"]),
                            "total_pagado": float(cli["total_pagado"])
                        })
                        
                        # Para la UI unificada
                        todas_filas_ui.append({
                            "ID": cli["idcliente"],
                            "País": pais["nombre"],
                            "Nombre": cli["nombre"],
                            "Apellidos": cli["apellidos"],
                            "Pólizas activas": int(cli["polizas_activas"]),
                            "Total pagado ($)": float(cli["total_pagado"])
                        })
                
                paises_datos_json.append({
                    "pais": pais["nombre"],
                    "clientes": clientes_list
                })
                
            # Interfaz de Usuario Moderna: Una sola tabla con filtros
            if todas_filas_ui:
                df_clientes = pd.DataFrame(todas_filas_ui)
                
                # Filtro dinámico
                paises_disponibles = ["Todos"] + sorted(list(df_clientes["País"].unique()))
                pais_seleccionado = st.selectbox("🌍 Filtrar por País:", options=paises_disponibles, index=0)
                
                if pais_seleccionado != "Todos":
                    df_filtrado = df_clientes[df_clientes["País"] == pais_seleccionado]
                else:
                    df_filtrado = df_clientes
                    
                st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
            else:
                st.info("No hay clientes registrados en el sistema.")
                
            if st.button("Generar Reporte", key="btn_gen_lis_cli", use_container_width=True):
                datos = {
                    "tipo_reporte": "Listado de Clientes",
                    "paises_datos": paises_datos_json
                }
                crud_reportes.crear("Listado de Clientes", datos)
                st.success("Reporte de Listado de Clientes guardado con éxito en el historial.")
                st.rerun()

        # 2. LISTADO DE PÓLIZAS
        elif reporte_listados == "Listado de Pólizas":
            st.caption(f"Fecha del listado: {date.today().strftime('%d/%m/%Y')}")
            tipos_seguro = listar_tipos_seguro()
            
            tipos_datos_json = []
            todas_polizas_ui = []
            
            for tipo in tipos_seguro:
                with Database() as db:
                    polizas = db.fetch_all(
                        """
                        SELECT p.idpoliza, c.nombre || ' ' || c.apellidos as cliente,
                               p.fecha_inicio as fechainicio, p.fecha_fin as fechafin, p.prima_mensual as primamensual,
                               p.monto_asegurado as montoasegurado, ep.nombre as estado
                        FROM poliza p
                        JOIN cliente c ON p.idcliente = c.idcliente
                        JOIN estado_poliza ep ON p.idestadopoliza = ep.idestadopoliza
                        WHERE p.idtiposeguro = %s
                        ORDER BY p.idpoliza;
                        """,
                        (tipo["idtiposeguro"],)
                    )
                
                polizas_list = []
                if polizas:
                    for p in polizas:
                        # Para JSON jerárquico
                        polizas_list.append({
                            "idpoliza": p["idpoliza"],
                            "cliente": p["cliente"],
                            "fechainicio": p["fechainicio"].strftime('%Y-%m-%d'),
                            "fechafin": p["fechafin"].strftime('%Y-%m-%d'),
                            "primamensual": float(p["primamensual"]),
                            "montoasegurado": float(p["montoasegurado"]),
                            "estado": p["estado"]
                        })
                        
                        # Para UI unificada
                        todas_polizas_ui.append({
                            "Número": p["idpoliza"],
                            "Tipo de Seguro": tipo["nombre"],
                            "Cliente": p["cliente"],
                            "Fecha inicio": p["fechainicio"].strftime('%Y-%m-%d'),
                            "Fecha fin": p["fechafin"].strftime('%Y-%m-%d'),
                            "Prima mensual": float(p["primamensual"]),
                            "Monto asegurado": float(p["montoasegurado"]),
                            "Estado": p["estado"]
                        })
                    
                tipos_datos_json.append({
                    "tipo": tipo["nombre"],
                    "polizas": polizas_list
                })
                
            # Interfaz de Usuario Moderna: Una sola tabla con filtros
            if todas_polizas_ui:
                df_polizas = pd.DataFrame(todas_polizas_ui)
                
                # Filtro dinámico
                tipos_disponibles = ["Todos"] + sorted(list(df_polizas["Tipo de Seguro"].unique()))
                tipo_seleccionado = st.selectbox("🛡️ Filtrar por Tipo de Seguro:", options=tipos_disponibles, index=0)
                
                if tipo_seleccionado != "Todos":
                    df_filtrado = df_polizas[df_polizas["Tipo de Seguro"] == tipo_seleccionado]
                else:
                    df_filtrado = df_polizas
                    
                st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
            else:
                st.info("No hay pólizas registradas en el sistema.")
                
            if st.button("Generar Reporte", key="btn_gen_lis_pol", use_container_width=True):
                datos = {
                    "tipo_reporte": "Listado de Pólizas",
                    "tipos_datos": tipos_datos_json
                }
                crud_reportes.crear("Listado de Pólizas", datos)
                st.success("Reporte de Listado de Pólizas guardado con éxito en el historial.")
                st.rerun()

        # 3. LISTADO DE RECLAMACIONES
        elif reporte_listados == "Listado de Reclamaciones":
            st.caption(f"Fecha del listado: {date.today().strftime('%d/%m/%Y')}")
            reclamaciones = listar_reclamaciones()
            
            reclamaciones_json = []
            if reclamaciones:
                df = pd.DataFrame(reclamaciones)
                df_display = df.rename(columns={
                    "cliente": "Cliente",
                    "idpoliza": "Número de póliza",
                    "tipo_seguro": "Tipo de seguro",
                    "idreclamacion": "Número de reclamación",
                    "tipo_siniestro": "Tipo de siniestro",
                    "fechasiniestro": "Fecha del siniestro",
                    "montoreclamado": "Monto reclamado",
                    "montoindemnizado": "Monto indemnizado",
                    "estado": "Estado"
                })
                st.dataframe(df_display[[
                    "Cliente", "Número de póliza", "Tipo de seguro", "Número de reclamación",
                    "Tipo de siniestro", "Fecha del siniestro", "Monto reclamado", "Monto indemnizado", "Estado"
                ]], use_container_width=True, hide_index=True)
                
                for r in reclamaciones:
                    reclamaciones_json.append({
                        "cliente": r["cliente"],
                        "idpoliza": r["idpoliza"],
                        "tipo_seguro": r["tipo_seguro"],
                        "idreclamacion": r["idreclamacion"],
                        "tipo_siniestro": r["tipo_siniestro"],
                        "fechasiniestro": r["fechasiniestro"].strftime('%Y-%m-%d') if isinstance(r["fechasiniestro"], (date, datetime)) else str(r["fechasiniestro"]),
                        "montoreclamado": float(r["montoreclamado"]),
                        "montoindemnizado": float(r["montoindemnizado"]),
                        "estado": r["estado"]
                    })
            else:
                st.info("No hay reclamaciones registradas en el sistema.")
                
            if st.button("Generar Reporte", key="btn_gen_lis_rec", use_container_width=True):
                datos = {
                    "tipo_reporte": "Listado de Reclamaciones",
                    "reclamaciones": reclamaciones_json
                }
                crud_reportes.crear("Listado de Reclamaciones", datos)
                st.success("Reporte de Listado de Reclamaciones guardado con éxito en el historial.")
                st.rerun()

        # 4. LISTADO DE REASEGURADORAS
        elif reporte_listados == "Listado de Reaseguradoras":
            st.caption(f"Fecha del listado: {date.today().strftime('%d/%m/%Y')}")
            with Database() as db:
                reaseguradoras = db.fetch_all(
                    """
                    SELECT r.idreaseguradora, r.nombre, p.nombre as pais,
                           tr.nombre as tipo_reaseguro
                    FROM reaseguradora r
                    JOIN pais p ON r.idpais = p.idpais
                    JOIN tipo_reaseguro tr ON r.idtiporeaseguro = tr.idtiporeaseguro
                    ORDER BY r.nombre;
                    """
                )
            
            reaseguradoras_json = []
            if reaseguradoras:
                for rea in reaseguradoras:
                    with st.expander(f"{rea['nombre']} ({rea['idreaseguradora']})"):
                        st.markdown(f"**País de origen:** {rea['pais']}")
                        st.markdown(f"**Tipo de reaseguro:** {rea['tipo_reaseguro']}")
                        
                        # Obtener participaciones
                        with Database() as db:
                            participaciones = db.fetch_all(
                                """
                                SELECT ts.nombre as tipo_seguro, pr.porcentaje
                                FROM participacion_reaseguro pr
                                JOIN tipo_seguro ts ON pr.idtiposeguro = ts.idtiposeguro
                                WHERE pr.idreaseguradora = %s;
                                """,
                                (rea["idreaseguradora"],)
                            )
                        
                        part_json = []
                        if participaciones:
                            df = pd.DataFrame(participaciones)
                            df_display = df.rename(columns={
                                "tipo_seguro": "Tipo de seguro",
                                "porcentaje": "Porcentaje (%)"
                            })
                            st.dataframe(df_display, use_container_width=True, hide_index=True)
                            
                            for p in participaciones:
                                part_json.append({
                                    "tipo_seguro": p["tipo_seguro"],
                                    "porcentaje": float(p["porcentaje"])
                                })
                        else:
                            st.info("No tiene participaciones de reaseguro registradas.")
                            
                        reaseguradoras_json.append({
                            "idreaseguradora": rea["idreaseguradora"],
                            "nombre": rea["nombre"],
                            "pais": rea["pais"],
                            "tipo_reaseguro": rea["tipo_reaseguro"],
                            "participaciones": part_json
                        })
            else:
                st.info("No hay reaseguradoras registradas en el sistema.")
                
            if st.button("Generar Reporte", key="btn_gen_lis_reas", use_container_width=True):
                datos = {
                    "tipo_reporte": "Listado de Reaseguradoras",
                    "reaseguradoras": reaseguradoras_json
                }
                crud_reportes.crear("Listado de Reaseguradoras", datos)
                st.success("Reporte de Listado de Reaseguradoras guardado con éxito en el historial.")
                st.rerun()

        # 5. LISTADO DE PÓLIZAS VENCIDAS
        elif reporte_listados == "Listado de Pólizas Vencidas":
            st.caption(f"Fecha del listado: {date.today().strftime('%d/%m/%Y')}")
            with Database() as db:
                polizas = db.fetch_all(
                    """
                    SELECT p.idpoliza, c.nombre || ' ' || c.apellidos as cliente,
                           ts.nombre as tipo_seguro,
                           p.fecha_inicio as fechainicio, p.fecha_fin as fechafin, p.monto_asegurado as montoasegurado
                    FROM poliza p
                    JOIN cliente c ON p.idcliente = c.idcliente
                    JOIN tipo_seguro ts ON p.idtiposeguro = ts.idtiposeguro
                    WHERE p.fecha_fin < CURRENT_DATE
                    ORDER BY p.fecha_fin;
                    """
                )
            
            polizas_json = []
            if polizas:
                df = pd.DataFrame(polizas)
                df_display = df.rename(columns={
                    "idpoliza": "Número de póliza",
                    "cliente": "Cliente",
                    "tipo_seguro": "Tipo de seguro",
                    "fechainicio": "Fecha inicio",
                    "fechafin": "Fecha fin",
                    "montoasegurado": "Monto asegurado"
                })
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                for p in polizas:
                    polizas_json.append({
                        "idpoliza": p["idpoliza"],
                        "cliente": p["cliente"],
                        "tipo_seguro": p["tipo_seguro"],
                        "fechainicio": p["fechainicio"].strftime('%Y-%m-%d'),
                        "fechafin": p["fechafin"].strftime('%Y-%m-%d'),
                        "montoasegurado": float(p["montoasegurado"])
                    })
            else:
                st.success("No se registran pólizas vencidas actualmente en el sistema.")
                
            if st.button("Generar Reporte", key="btn_gen_lis_venc", use_container_width=True):
                datos = {
                    "tipo_reporte": "Listado de Pólizas Vencidas",
                    "polizas": polizas_json
                }
                crud_reportes.crear("Listado de Pólizas Vencidas", datos)
                st.success("Reporte de Listado de Pólizas Vencidas guardado con éxito en el historial.")
                st.rerun()

        # 6. LISTADO DE CLIENTES CON PÓLIZAS CANCELADAS
        elif reporte_listados == "Listado de Clientes con Pólizas Canceladas":
            st.caption(f"Fecha del listado: {date.today().strftime('%d/%m/%Y')}")
            with Database() as db:
                clientes = db.fetch_all(
                    """
                    SELECT c.idcliente, c.nombre, c.apellidos,
                           COUNT(p.idpoliza) as cantidad_canceladas,
                           STRING_AGG(pc.motivo, '; ') as motivos
                    FROM cliente c
                    JOIN poliza p ON c.idcliente = p.idcliente
                    JOIN poliza_cancelada pc ON p.idpoliza = pc.idpoliza
                    GROUP BY c.idcliente, c.nombre, c.apellidos
                    ORDER BY c.apellidos;
                    """
                )
            
            clientes_json = []
            if clientes:
                df = pd.DataFrame(clientes)
                df_display = df.rename(columns={
                    "idcliente": "ID",
                    "nombre": "Nombre",
                    "apellidos": "Apellidos",
                    "cantidad_canceladas": "Pólizas canceladas",
                    "motivos": "Motivo(s) de cancelación"
                })
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                for c in clientes:
                    clientes_json.append({
                        "idcliente": c["idcliente"],
                        "nombre": c["nombre"],
                        "apellidos": c["apellidos"],
                        "cantidad_canceladas": int(c["cantidad_canceladas"]),
                        "motivos": c["motivos"]
                    })
            else:
                st.info("No se registran clientes con pólizas canceladas en el sistema.")
                
            if st.button("Generar Reporte", key="btn_gen_lis_canc", use_container_width=True):
                datos = {
                    "tipo_reporte": "Listado de Clientes con Pólizas Canceladas",
                    "clientes": clientes_json
                }
                crud_reportes.crear("Listado de Clientes con Pólizas Canceladas", datos)
                st.success("Reporte de Clientes con Pólizas Canceladas guardado con éxito en el historial.")
                st.rerun()

    # =========================================================================
    # TAB 2: RESÚMENES Y ESTADÍSTICAS
    # =========================================================================
    with tab2:
        st.subheader("Análisis Estadísticos y Resúmenes Ejecutivos")
        reporte_resumenes = st.selectbox(
            "Seleccione el resumen estadístico a generar:",
            options=[
                "Resumen de Pólizas por Tipo de Seguro",
                "Resumen de Reclamaciones por Estado",
                "Listado de Ingresos Mensuales",
                "Reporte de Clientes con Reclamaciones Aprobadas",
                "Reporte de Clientes con Reclamaciones Rechazadas"
            ],
            key="sb_resumenes"
        )
        st.divider()
        
        # 7. RESUMEN DE PÓLIZAS POR TIPO DE SEGURO
        if reporte_resumenes == "Resumen de Pólizas por Tipo de Seguro":
            st.caption(f"Fecha del reporte: {date.today().strftime('%d/%m/%Y')}")
            tipos_seguro = listar_tipos_seguro()
            resumen_json = []
            
            for tipo in tipos_seguro:
                with Database() as db:
                    stats = db.fetch_one(
                        """
                        SELECT COUNT(*) as cantidad,
                               COALESCE(SUM(prima_mensual), 0) as total_primas,
                               COALESCE(SUM(monto_asegurado), 0) as total_asegurado
                        FROM poliza
                        WHERE idtiposeguro = %s AND idestadopoliza = 1;
                        """,
                        (tipo["idtiposeguro"],)
                    )
                resumen_json.append({
                    "Tipo de seguro": tipo["nombre"],
                    "Cantidad de pólizas activas": int(stats["cantidad"]),
                    "Total de primas mensuales": float(stats["total_primas"]),
                    "Total de monto asegurado": float(stats["total_asegurado"])
                })
            
            if resumen_json:
                df = pd.DataFrame(resumen_json)
                # Formatear visualmente para Streamlit sin dañar los tipos del JSON
                df_display = df.copy()
                df_display["Total de primas mensuales"] = df_display["Total de primas mensuales"].map(lambda x: f"${x:,.2f}")
                df_display["Total de monto asegurado"] = df_display["Total de monto asegurado"].map(lambda x: f"${x:,.2f}")
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
            if st.button("Generar Reporte", key="btn_gen_res_tipo", use_container_width=True):
                datos = {
                    "tipo_reporte": "Resumen de Pólizas por Tipo de Seguro",
                    "resumen": resumen_json
                }
                crud_reportes.crear("Resumen de Pólizas por Tipo de Seguro", datos)
                st.success("Reporte guardado con éxito en el historial.")
                st.rerun()

        # 8. RESUMEN DE RECLAMACIONES POR ESTADO
        elif reporte_resumenes == "Resumen de Reclamaciones por Estado":
            st.caption(f"Fecha del reporte: {date.today().strftime('%d/%m/%Y')}")
            estados = listar_estados_reclamacion()
            resumen_json = []
            
            for estado in estados:
                with Database() as db:
                    stats = db.fetch_one(
                        """
                        SELECT COUNT(*) as cantidad,
                               COALESCE(SUM(monto_reclamado), 0) as total_reclamado,
                               COALESCE(SUM(monto_indemnizado), 0) as total_indemnizado
                        FROM reclamacion
                        WHERE idestadoreclamacion = %s;
                        """,
                        (estado["idestadoreclamacion"],)
                    )
                resumen_json.append({
                    "Estado": estado["nombre"],
                    "Cantidad": int(stats["cantidad"]),
                    "Total monto reclamado": float(stats["total_reclamado"]),
                    "Total monto indemnizado": float(stats["total_indemnizado"])
                })
            
            if resumen_json:
                df = pd.DataFrame(resumen_json)
                df_display = df.copy()
                df_display["Total monto reclamado"] = df_display["Total monto reclamado"].map(lambda x: f"${x:,.2f}")
                df_display["Total monto indemnizado"] = df_display["Total monto indemnizado"].map(lambda x: f"${x:,.2f}")
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
            if st.button("Generar Reporte", key="btn_gen_res_est", use_container_width=True):
                datos = {
                    "tipo_reporte": "Resumen de Reclamaciones por Estado",
                    "resumen": resumen_json
                }
                crud_reportes.crear("Resumen de Reclamaciones por Estado", datos)
                st.success("Reporte guardado con éxito en el historial.")
                st.rerun()

        # 9. LISTADO DE INGRESOS MENSUALES
        elif reporte_resumenes == "Listado de Ingresos Mensuales":
            st.caption(f"Fecha del reporte: {date.today().strftime('%d/%m/%Y')}")
            año_actual = datetime.now().year
            año = st.selectbox("Seleccione el año fiscal para el desglose:", [año_actual, año_actual - 1, año_actual - 2], key="sb_año_ingresos_gen")
            
            with Database() as db:
                ingresos = db.fetch_all(
                    """
                    SELECT EXTRACT(MONTH FROM fecha_pago) as mes,
                           TO_CHAR(fecha_pago, 'Month') as nombre_mes,
                           COALESCE(SUM(monto_pagado), 0) as ingreso
                    FROM pago
                    WHERE EXTRACT(YEAR FROM fecha_pago) = %s
                    GROUP BY mes, nombre_mes
                    ORDER BY mes;
                    """,
                    (año,)
                )
            
            if ingresos:
                meses = {
                    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
                }
                
                datos_completos = []
                for mes_num, mes_nombre in meses.items():
                    ing_val = next((float(i["ingreso"]) for i in ingresos if int(i["mes"]) == mes_num), 0.0)
                    datos_completos.append({
                        "mes": mes_nombre,
                        "ingreso": ing_val
                    })
                
                total_anual = sum(d["ingreso"] for d in datos_completos)
                st.metric("Ingreso Total Anual", f"${total_anual:,.2f}")
                
                filas = [{'Mes': d['mes'], 'Ingreso Mensual': f"${d['ingreso']:,.2f}"} for d in datos_completos]
                st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)
                
                # Gráfico
                st.subheader("Gráfico de ingresos mensuales")
                df_chart = pd.DataFrame(datos_completos)
                st.bar_chart(df_chart.set_index("mes")["ingreso"])
                
                if st.button("Generar Reporte", key="btn_gen_ing_mens", use_container_width=True):
                    datos = {
                        "tipo_reporte": "Ingresos Mensuales",
                        "año": año,
                        "total_anual": float(total_anual),
                        "ingresos": datos_completos
                    }
                    crud_reportes.crear(f"Ingresos Mensuales {año}", datos)
                    st.success(f"Reporte de ingresos anuales {año} guardado con éxito.")
                    st.rerun()
            else:
                st.info(f"No hay pagos registrados para el año fiscal {año}.")

        # 10. CLIENTES CON RECLAMACIONES APROBADAS
        elif reporte_resumenes == "Reporte de Clientes con Reclamaciones Aprobadas":
            st.caption(f"Fecha del reporte: {date.today().strftime('%d/%m/%Y')}")
            with Database() as db:
                clientes = db.fetch_all(
                    """
                    SELECT c.idcliente, c.nombre, c.apellidos,
                           COUNT(r.idreclamacion) as cantidad_aprobadas,
                           COALESCE(SUM(r.monto_indemnizado), 0) as total_indemnizado
                    FROM cliente c
                    JOIN poliza p ON c.idcliente = p.idcliente
                    JOIN reclamacion r ON p.idpoliza = r.idpoliza
                    WHERE r.idestadoreclamacion = (SELECT idestadoreclamacion FROM estado_reclamacion WHERE lower(nombre) = 'aprobada')
                    GROUP BY c.idcliente, c.nombre, c.apellidos
                    ORDER BY total_indemnizado DESC;
                    """
                )
            
            clientes_json = []
            if clientes:
                df = pd.DataFrame(clientes)
                df_display = df.rename(columns={
                    "idcliente": "ID",
                    "nombre": "Nombre",
                    "apellidos": "Apellidos",
                    "cantidad_aprobadas": "Reclamaciones aprobadas",
                    "total_indemnizado": "Total indemnizado ($)"
                })
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                for c in clientes:
                    clientes_json.append({
                        "idcliente": c["idcliente"],
                        "nombre": c["nombre"],
                        "apellidos": c["apellidos"],
                        "cantidad_aprobadas": int(c["cantidad_aprobadas"]),
                        "total_indemnizado": float(c["total_indemnizado"])
                    })
            else:
                st.info("No se registran clientes con reclamaciones aprobadas actualmente.")
                
            if st.button("Generar Reporte", key="btn_gen_rec_aprob", use_container_width=True):
                datos = {
                    "tipo_reporte": "Reporte de Clientes con Reclamaciones Aprobadas",
                    "clientes": clientes_json
                }
                crud_reportes.crear("Reporte de Clientes con Reclamaciones Aprobadas", datos)
                st.success("Reporte guardado con éxito.")
                st.rerun()

        # 11. CLIENTES CON RECLAMACIONES RECHAZADAS
        elif reporte_resumenes == "Reporte de Clientes con Reclamaciones Rechazadas":
            st.caption(f"Fecha del reporte: {date.today().strftime('%d/%m/%Y')}")
            with Database() as db:
                clientes = db.fetch_all(
                    """
                    SELECT c.idcliente, c.nombre, c.apellidos,
                           COUNT(r.idreclamacion) as cantidad_rechazadas,
                           STRING_AGG(rr.motivo, '; ') as motivos
                    FROM cliente c
                    JOIN poliza p ON c.idcliente = p.idcliente
                    JOIN reclamacion r ON p.idpoliza = r.idpoliza
                    JOIN reclamacion_rechazada rr ON r.idreclamacion = rr.idreclamacion
                    GROUP BY c.idcliente, c.nombre, c.apellidos
                    ORDER BY cantidad_rechazadas DESC;
                    """
                )
            
            clientes_json = []
            if clientes:
                df = pd.DataFrame(clientes)
                df_display = df.rename(columns={
                    "idcliente": "ID",
                    "nombre": "Nombre",
                    "apellidos": "Apellidos",
                    "cantidad_rechazadas": "Reclamaciones rechazadas",
                    "motivos": "Motivo(s) del rechazo"
                })
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                for c in clientes:
                    clientes_json.append({
                        "idcliente": c["idcliente"],
                        "nombre": c["nombre"],
                        "apellidos": c["apellidos"],
                        "cantidad_rechazadas": int(c["cantidad_rechazadas"]),
                        "motivos": c["motivos"]
                    })
            else:
                st.info("No se registran clientes con reclamaciones rechazadas en el sistema.")
                
            if st.button("Generar Reporte", key="btn_gen_rec_rech", use_container_width=True):
                datos = {
                    "tipo_reporte": "Reporte de Clientes con Reclamaciones Rechazadas",
                    "clientes": clientes_json
                }
                crud_reportes.crear("Reporte de Clientes con Reclamaciones Rechazadas", datos)
                st.success("Reporte guardado con éxito.")
                st.rerun()

    # =========================================================================
    # TAB 3: FICHAS ESPECIALES
    # =========================================================================
    with tab3:
        st.subheader("Consultas de Fichas Técnicas e Informativas")
        reporte_fichas = st.selectbox(
            "Seleccione el tipo de ficha a consultar:",
            options=[
                "Ficha de la Agencia de Seguros",
                "Ficha de un Cliente Determinado",
                "Ficha de una Reaseguradora Asociada"
            ],
            key="sb_fichas"
        )
        st.divider()
        
        # 12. FICHA DE LA AGENCIA
        if reporte_fichas == "Ficha de la Agencia de Seguros":
            agencia = obtener_agencia()
            if agencia:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('**Datos de la Agencia**')
                    st.text(f"Nombre: {agencia['nombre']}")
                    st.text(f"Dirección Postal: {agencia['direccion']}")
                    st.text(f"Teléfono: {agencia['telefono']}")
                    st.text(f"Email: {agencia['email']}")
                with col2:
                    st.markdown('**Equipo Directivo**')
                    st.text(f"Director General: {agencia['directorgeneral']}")
                    st.text(f"Jefe de Seguros: {agencia['jefeseguros']}")
                    st.text(f"Jefe de Reclamaciones: {agencia['jefereclamaciones']}")
                    
                if st.button("Generar Reporte", key="btn_gen_fic_ag", use_container_width=True):
                    datos = {
                        "tipo_reporte": "Ficha de la Agencia de Seguros",
                        "nombre": agencia["nombre"],
                        "direccion": agencia["direccion"],
                        "telefono": agencia["telefono"],
                        "email": agencia["email"],
                        "director_general": agencia["directorgeneral"],
                        "jefe_seguros": agencia["jefeseguros"],
                        "jefe_reclamaciones": agencia["jefereclamaciones"]
                    }
                    crud_reportes.crear("Ficha Agencia", datos)
                    st.success("Ficha de la Agencia guardada históricamente.")
                    st.rerun()
            else:
                st.warning("No hay datos de la agencia registrados.")

        # 13. FICHA DE UN CLIENTE DETERMINADO
        elif reporte_fichas == "Ficha de un Cliente Determinado":
            clientes = listar_clientes()
            if clientes:
                cliente_opciones = {c["idcliente"]: f"{c['nombre']} {c['apellidos']} - {c['no_identificacion']}" for c in clientes}
                cliente_seleccionado = st.selectbox(
                    "Seleccione el cliente a consultar:",
                    options=list(cliente_opciones.keys()),
                    format_func=lambda x: cliente_opciones[x],
                    key="sb_ficha_cli_sel"
                )
                
                if cliente_seleccionado:
                    cliente = obtener_cliente_por_id(cliente_seleccionado)
                    if cliente:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Nombre:** {cliente['nombre']} {cliente['apellidos']}")
                            st.markdown(f"**Cédula/Pasaporte:** {cliente['no_identificacion']}")
                            st.markdown(f"**Edad:** {cliente['edad']} años")
                            st.markdown(f"**Sexo:** {'Masculino' if cliente['sexo'] == 'M' else 'Femenino'}")
                        with col2:
                            st.markdown(f"**Teléfono:** {cliente['telefono'] or 'No registrado'}")
                            st.markdown(f"**Dirección:** {cliente['dir_postal'] or 'No registrada'}")
                            st.markdown(f"**Correo:** {cliente['correo'] or 'No registrado'}")
                            
                        # Consultar pólizas y primas pagadas
                        with Database() as db:
                            polizas_activas = db.fetch_one(
                                """
                                SELECT COUNT(*) as cantidad
                                FROM poliza
                                WHERE idcliente = %s AND idestadopoliza = 1;
                                """,
                                (cliente_seleccionado,)
                            )
                            total_pagado = total_pagado_por_cliente(cliente_seleccionado)
                            
                        st.divider()
                        col_m1, col_m2 = st.columns(2)
                        with col_m1:
                            st.metric("Pólizas Activas", polizas_activas["cantidad"])
                        with col_m2:
                            st.metric("Total Primas Pagadas", f"${total_pagado:,.2f}")
                            
                        # Reclamaciones
                        with Database() as db:
                            reclamaciones = db.fetch_all(
                                """
                                SELECT r.idreclamacion, p.idpoliza, ts.nombre as tipo_seguro,
                                       r.fecha_siniestro as fechasiniestro, r.monto_reclamado as montoreclamado, r.monto_indemnizado as montoindemnizado,
                                       er.nombre as estado
                                FROM reclamacion r
                                JOIN poliza p ON r.idpoliza = p.idpoliza
                                JOIN tipo_seguro ts ON p.idtiposeguro = ts.idtiposeguro
                                JOIN estado_reclamacion er ON r.idestadoreclamacion = er.idestadoreclamacion
                                WHERE p.idcliente = %s
                                ORDER BY r.fecha_siniestro DESC;
                                """,
                                (cliente_seleccionado,)
                            )
                        
                        reclamaciones_list_json = []
                        if reclamaciones:
                            st.subheader("Historial de Reclamaciones")
                            df = pd.DataFrame(reclamaciones)
                            df_display = df.rename(columns={
                                "idreclamacion": "ID Reclamación",
                                "idpoliza": "Póliza",
                                "tipo_seguro": "Ramo Seguro",
                                "fechasiniestro": "Fecha",
                                "montoreclamado": "Monto reclamado",
                                "montoindemnizado": "Monto indemnizado",
                                "estado": "Estado"
                            })
                            st.dataframe(df_display, use_container_width=True, hide_index=True)
                            
                            for r in reclamaciones:
                                reclamaciones_list_json.append({
                                    "idreclamacion": r["idreclamacion"],
                                    "idpoliza": r["idpoliza"],
                                    "tipo_seguro": r["tipo_seguro"],
                                    "fechasiniestro": r["fechasiniestro"].strftime('%Y-%m-%d') if isinstance(r["fechasiniestro"], (date, datetime)) else str(r["fechasiniestro"]),
                                    "montoreclamado": float(r["montoreclamado"]),
                                    "montoindemnizado": float(r["montoindemnizado"]),
                                    "estado": r["estado"]
                                })
                        else:
                            st.info("El cliente no tiene reclamaciones de siniestros registradas.")
                            
                        if st.button("Generar Reporte", key="btn_gen_fic_cli", use_container_width=True):
                            # Consultar el nombre del país para el JSON
                            with Database() as db:
                                pais_row = db.fetch_one("SELECT nombre FROM pais WHERE idpais = %s", (cliente["idpais"],))
                            
                            datos = {
                                "tipo_reporte": "Ficha de un Cliente Determinado",
                                "cliente": {
                                    "nombre": cliente["nombre"],
                                    "apellidos": cliente["apellidos"],
                                    "identificacion": cliente["no_identificacion"],
                                    "telefono": cliente["telefono"],
                                    "correo": cliente["correo"],
                                    "pais": pais_row["nombre"] if pais_row else "N/A"
                                },
                                "polizas_activas": int(polizas_activas["cantidad"]),
                                "total_primas": float(total_pagado),
                                "reclamaciones": len(reclamaciones),
                                "reclamaciones_list": reclamaciones_list_json
                            }
                            crud_reportes.crear(f"Ficha Cliente {cliente['nombre']} {cliente['apellidos']}", datos)
                            st.success(f"Ficha del cliente {cliente['nombre']} guardada con éxito.")
                            st.rerun()
            else:
                st.warning("No hay clientes registrados en el sistema.")

        # 14. FICHA DE UNA REASEGURADORA ASOCIADA
        elif reporte_fichas == "Ficha de una Reaseguradora Asociada":
            with Database() as db:
                reaseguradoras = db.fetch_all("SELECT idreaseguradora, nombre FROM reaseguradora ORDER BY nombre;")
            
            if reaseguradoras:
                rea_opciones = {r["idreaseguradora"]: r["nombre"] for r in reaseguradoras}
                rea_seleccionada = st.selectbox(
                    "Seleccione la reaseguradora a consultar:",
                    options=list(rea_opciones.keys()),
                    format_func=lambda x: rea_opciones[x],
                    key="sb_ficha_reas_sel"
                )
                
                if rea_seleccionada:
                    rea = obtener_reaseguradora_por_id(rea_seleccionada)
                    if rea:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Nombre:** {rea['nombre']}")
                            st.markdown(f"**País de origen:** {rea['pais_nombre']}")
                        with col2:
                            st.markdown(f"**Tipo de reaseguro:** {rea['tipo_reaseguro_nombre']}")
                            st.markdown(f"**Email de contacto:** {rea.get('email') or 'No registrado'}")
                            
                        # Participaciones
                        with Database() as db:
                            participaciones = db.fetch_all(
                                """
                                SELECT ts.nombre as tipo_seguro, pr.porcentaje
                                FROM participacion_reaseguro pr
                                JOIN tipo_seguro ts ON pr.idtiposeguro = ts.idtiposeguro
                                WHERE pr.idreaseguradora = %s;
                                """,
                                (rea_seleccionada,)
                            )
                        
                        part_json = []
                        if participaciones:
                            st.subheader("Participación por Tipo de Seguro")
                            df = pd.DataFrame(participaciones)
                            df_display = df.rename(columns={
                                "tipo_seguro": "Tipo de seguro",
                                "porcentaje": "Porcentaje (%)"
                            })
                            st.dataframe(df_display, use_container_width=True, hide_index=True)
                            
                            for p in participaciones:
                                part_json.append({
                                    "tipo_seguro": p["tipo_seguro"],
                                    "porcentaje": float(p["porcentaje"])
                                })
                        else:
                            st.info("Esta reaseguradora no posee participaciones de cobertura registradas.")
                            
                        if st.button("Generar Reporte", key="btn_gen_fic_reas", use_container_width=True):
                            datos = {
                                "tipo_reporte": "Ficha de una Reaseguradora Asociada",
                                "nombre": rea["nombre"],
                                "pais": rea["pais_nombre"],
                                "tipo_reaseguro": rea["tipo_reaseguro_nombre"],
                                "email": rea.get("email") or "No registrado",
                                "participaciones": part_json
                            }
                            crud_reportes.crear(f"Ficha Reaseguradora {rea['nombre']}", datos)
                            st.success(f"Ficha técnica de la reaseguradora {rea['nombre']} guardada.")
                            st.rerun()
            else:
                st.warning("No hay reaseguradoras registradas en el sistema.")

    # =========================================================================
    # TAB 4: REPORTES PARAMÉTRICOS
    # =========================================================================
    with tab4:
        st.subheader("Filtros Temporales y Reportes de Fechas")
        reporte_param = st.selectbox(
            "Seleccione el reporte paramétrico a generar:",
            options=[
                "Reporte de Pólizas Emitidas en un Período",
                "Reporte de Estado de las Reclamaciones",
                "Reporte de Ingresos Mensuales por Concepto de Primas"
            ],
            key="sb_param"
        )
        st.divider()
        
        # 15. REPORTES DE PÓLIZAS EN PERÍODO
        if reporte_param == "Reporte de Pólizas Emitidas en un Período":
            col1, col2 = st.columns(2)
            with col1:
                fecha_desde = st.date_input("Fecha desde:", value=date.today().replace(month=1, day=1), key="dp_pol_desde")
            with col2:
                fecha_hasta = st.date_input("Fecha hasta:", value=date.today(), key="dp_pol_hasta")
                
            with Database() as db:
                polizas = db.fetch_all(
                    """
                    SELECT p.idpoliza, c.nombre || ' ' || c.apellidos as cliente,
                           ts.nombre as tipo_seguro,
                           p.fecha_inicio as fechainicio, p.fecha_fin as fechafin, p.prima_mensual as primamensual, ep.nombre as estado
                    FROM poliza p
                    JOIN cliente c ON p.idcliente = c.idcliente
                    JOIN tipo_seguro ts ON p.idtiposeguro = ts.idtiposeguro
                    JOIN estado_poliza ep ON p.idestadopoliza = ep.idestadopoliza
                    WHERE p.fecha_inicio BETWEEN %s AND %s
                    ORDER BY p.fecha_inicio;
                    """,
                    (fecha_desde, fecha_hasta)
                )
            
            polizas_json = []
            if polizas:
                df = pd.DataFrame(polizas)
                df_display = df.rename(columns={
                    "idpoliza": "Número de póliza",
                    "cliente": "Cliente",
                    "tipo_seguro": "Tipo de seguro",
                    "fechainicio": "Fecha inicio",
                    "fechafin": "Fecha fin",
                    "primamensual": "Prima mensual ($)",
                    "estado": "Estado"
                })
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                st.caption(f"Total de pólizas emitidas en el período seleccionado: {len(polizas)}")
                
                for p in polizas:
                    polizas_json.append({
                        "id": p["idpoliza"],
                        "cliente": p["cliente"],
                        "tipo_seguro": p["tipo_seguro"],
                        "fecha_inicio": p["fechainicio"].strftime('%Y-%m-%d'),
                        "fecha_fin": p["fechafin"].strftime('%Y-%m-%d'),
                        "prima": float(p["primamensual"]),
                        "estado": p["estado"]
                    })
            else:
                st.info("No se registraron emisiones de pólizas en el rango temporal seleccionado.")
                
            if polizas and st.button("Generar Reporte", key="btn_gen_pol_per", use_container_width=True):
                datos = {
                    "tipo_reporte": "Reporte de Pólizas Emitidas en un Período",
                    "fecha_inicio": fecha_desde.strftime('%d/%m/%Y'),
                    "fecha_fin": fecha_hasta.strftime('%d/%m/%Y'),
                    "polizas": polizas_json
                }
                crud_reportes.crear(f"Pólizas por Período {fecha_desde.strftime('%d%m%Y')} - {fecha_hasta.strftime('%d%m%Y')}", datos)
                st.success("Reporte temporal de pólizas guardado con éxito.")
                st.rerun()

        # 16. REPORTE DE ESTADO DE RECLAMACIONES
        elif reporte_param == "Reporte de Estado de las Reclamaciones":
            col1, col2 = st.columns(2)
            with col1:
                fecha_desde_sini = st.date_input("Fecha siniestro desde:", value=date.today().replace(month=1, day=1), key="dp_rec_desde")
            with col2:
                fecha_hasta_sini = st.date_input("Fecha siniestro hasta:", value=date.today(), key="dp_rec_hasta")
                
            with Database() as db:
                reclamaciones = db.fetch_all(
                    """
                    SELECT r.idreclamacion, c.nombre || ' ' || c.apellidos as cliente,
                           r.idpoliza, ts.nombre as tipo_seguro, tsi.nombre as tipo_siniestro,
                           r.fecha_siniestro as fechasiniestro, er.nombre as estado, r.monto_reclamado as montoreclamado, r.monto_indemnizado as montoindemnizado
                    FROM reclamacion r
                    JOIN poliza p ON r.idpoliza = p.idpoliza
                    JOIN cliente c ON p.idcliente = c.idcliente
                    JOIN tipo_seguro ts ON p.idtiposeguro = ts.idtiposeguro
                    JOIN tipo_siniestro tsi ON r.idtiposiniestro = tsi.idtiposiniestro
                    JOIN estado_reclamacion er ON r.idestadoreclamacion = er.idestadoreclamacion
                    WHERE r.fecha_siniestro BETWEEN %s AND %s
                    ORDER BY r.fecha_siniestro DESC;
                    """,
                    (fecha_desde_sini, fecha_hasta_sini)
                )
            
            reclamaciones_json = []
            if reclamaciones:
                df = pd.DataFrame(reclamaciones)
                df_display = df.rename(columns={
                    "idreclamacion": "No. Reclamación",
                    "cliente": "Cliente",
                    "idpoliza": "Número de póliza",
                    "tipo_seguro": "Ramo Seguro",
                    "tipo_siniestro": "Causa Siniestro",
                    "fechasiniestro": "Fecha Siniestro",
                    "estado": "Estado",
                    "montoreclamado": "Reclamado ($)",
                    "montoindemnizado": "Indemnizado ($)"
                })
                st.dataframe(df_display[[
                    "No. Reclamación", "Cliente", "Número de póliza", "Ramo Seguro",
                    "Causa Siniestro", "Fecha Siniestro", "Estado", "Reclamado ($)", "Indemnizado ($)"
                ]], use_container_width=True, hide_index=True)
                
                for r in reclamaciones:
                    reclamaciones_json.append({
                        "id": r["idreclamacion"],
                        "cliente": r["cliente"],
                        "monto_reclamado": float(r["montoreclamado"]),
                        "monto_indemnizado": float(r["montoindemnizado"]),
                        "estado": r["estado"]
                    })
            else:
                st.info("No se registraron reclamaciones de siniestros en el rango temporal seleccionado.")
                
            if reclamaciones and st.button("Generar Reporte", key="btn_gen_rec_per", use_container_width=True):
                datos = {
                    "tipo_reporte": "Reporte de Estado de las Reclamaciones",
                    "fecha_inicio": fecha_desde_sini.strftime('%d/%m/%Y'),
                    "fecha_fin": fecha_hasta_sini.strftime('%d/%m/%Y'),
                    "reclamaciones": reclamaciones_json
                }
                crud_reportes.crear(f"Estado Reclamaciones {fecha_desde_sini.strftime('%d%m%Y')} - {fecha_hasta_sini.strftime('%d%m%Y')}", datos)
                st.success("Reporte temporal de reclamaciones guardado.")
                st.rerun()

        # 17. REPORTES DE INGRESOS MENSUALES POR CONCEPTOS DE PRIMAS
        elif reporte_param == "Reporte de Ingresos Mensuales por Concepto de Primas":
            st.caption("Detalle de ingresos mensuales filtrado por año fiscal y graficado para análisis de tendencia.")
            años_disponibles = [date.today().year, date.today().year - 1, date.today().year - 2]
            año_seleccionado = st.selectbox("Seleccione el año fiscal de interés:", options=años_disponibles, index=0, key="sb_año_primas_gen")
            
            with Database() as db:
                ingresos = db.fetch_all(
                    """
                    SELECT EXTRACT(MONTH FROM fecha_pago) as mes,
                           TO_CHAR(fecha_pago, 'Month') as nombre_mes,
                           COALESCE(SUM(monto_pagado), 0) as ingreso
                    FROM pago
                    WHERE EXTRACT(YEAR FROM fecha_pago) = %s
                    GROUP BY mes, nombre_mes
                    ORDER BY mes;
                    """,
                    (año_seleccionado,)
                )
            
            if ingresos:
                meses = {
                    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
                }
                
                datos_completos = []
                for mes_num, mes_nombre in meses.items():
                    ingreso_val = next((float(i["ingreso"]) for i in ingresos if int(i["mes"]) == mes_num), 0.0)
                    datos_completos.append({
                        "mes": mes_nombre,
                        "ingreso": ingreso_val
                    })
                
                total_anual = sum(d["ingreso"] for d in datos_completos)
                st.metric("Ingreso total anual por primas", f"${total_anual:,.2f}")
                
                filas = [{'Mes': d['mes'], 'Ingreso mensual ($)': f"${d['ingreso']:,.2f}"} for d in datos_completos]
                st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)
                
                # Gráfico
                st.subheader("Gráfico de ingresos mensuales por primas")
                df_chart = pd.DataFrame(datos_completos)
                st.bar_chart(df_chart.set_index("mes")["ingreso"])
                
                if st.button("Generar Reporte", key="btn_gen_ing_primas", use_container_width=True):
                    datos = {
                        "tipo_reporte": "Ingresos Mensuales",
                        "año": año_seleccionado,
                        "total_anual": float(total_anual),
                        "ingresos": [{"mes": d["mes"], "ingreso": d["ingreso"]} for d in datos_completos]
                    }
                    crud_reportes.crear(f"Ingresos por Primas {año_seleccionado}", datos)
                    st.success(f"Reporte de ingresos por primas {año_seleccionado} guardado con éxito.")
                    st.rerun()
            else:
                st.info(f"No hay pagos de primas registrados para el año {año_seleccionado}.")

    # =========================================================================
    # TAB 5: CENTRALIZED HISTORICAL REPORTS VIEW (CRITICAL GAP FILLED)
    # =========================================================================
    with tab5:
        st.subheader("Historial de Reportes Guardados")
        _mostrar_reportes_guardados_centralizado()
