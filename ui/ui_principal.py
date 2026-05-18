# -*- coding: utf-8 -*-
import streamlit as st
from datetime import date
from db.conexionDB import Database

def pagina_principal():
     st.title("🛡️ Panel de Control de Seguros")
     st.caption(f"📅 Fecha actual: {date.today().strftime('%d/%m/%Y')}")
     st.divider()

     # Obtener métricas de la base de datos
     with Database() as db:
          # Total de clientes
          total_clientes = db.fetch_one("SELECT COUNT(*) as total FROM cliente;")
          total_clientes = total_clientes["total"] if total_clientes else 0

          # Total de pólizas activas
          polizas_activas = db.fetch_one(
               """
               SELECT COUNT(*) as total
               FROM poliza p
               JOIN estado_poliza ep ON p.idestadopoliza = ep.idestadopoliza
               WHERE ep.nombre = 'Activa';
               """
          )
          polizas_activas = polizas_activas["total"] if polizas_activas else 0

          # Total de reclamaciones en proceso (pendientes)
          reclamaciones_pendientes = db.fetch_one(
               """
               SELECT COUNT(*) as total
               FROM reclamacion r
               JOIN estado_reclamacion er ON r.idestadoreclamacion = er.idestadoreclamacion
               WHERE er.nombre = 'En Proceso';
               """
          )
          reclamaciones_pendientes = reclamaciones_pendientes["total"] if reclamaciones_pendientes else 0

          # Ingresos del mes actual
          ingresos_mes = db.fetch_one(
               """
               SELECT COALESCE(SUM(monto_pagado), 0) as total
               FROM pago
               WHERE EXTRACT(YEAR FROM fecha_pago) = EXTRACT(YEAR FROM CURRENT_DATE)
                    AND EXTRACT(MONTH FROM fecha_pago) = EXTRACT(MONTH FROM CURRENT_DATE);
               """
          )
          ingresos_mes = ingresos_mes["total"] if ingresos_mes else 0

     # Mostrar métricas en 4 columnas con hermosas tarjetas de contenedor
     col1, col2, col3, col4 = st.columns(4)

     with col1:
          with st.container(border=True):
               st.markdown("👥 **Clientes registrados**")
               st.markdown(f"<h2 style='margin: 0; color: #1E88E5;'>{total_clientes}</h2>", unsafe_allow_html=True)

     with col2:
          with st.container(border=True):
               st.markdown("📄 **Pólizas activas**")
               st.markdown(f"<h2 style='margin: 0; color: #43A047;'>{polizas_activas}</h2>", unsafe_allow_html=True)

     with col3:
          with st.container(border=True):
               st.markdown("⏳ **Reclamaciones pend.**")
               st.markdown(f"<h2 style='margin: 0; color: #FB8C00;'>{reclamaciones_pendientes}</h2>", unsafe_allow_html=True)

     with col4:
          with st.container(border=True):
               st.markdown("💰 **Ingresos del mes**")
               st.markdown(f"<h2 style='margin: 0; color: #8E24AA;'>${ingresos_mes:,.2f}</h2>", unsafe_allow_html=True)

     st.divider()

     # Accesos rápidos
     st.subheader("⚡ Accesos rápidos")
     col1, col2, col3, col4 = st.columns(4)

     # Callbacks de navegación para evitar doble renderizado o retroceso de pestaña
     def ir_a_clientes():
          st.session_state.menu = "Clientes"
          st.session_state.menu_selection = "Clientes"
          st.session_state.active_tab_cliente = "Nuevo Cliente"

     def ir_a_polizas():
          st.session_state.menu = "Pólizas"
          st.session_state.menu_selection = "Pólizas"
          st.session_state.active_tab_poliza = "Nueva Poliza"

     def ir_a_reclamaciones():
          st.session_state.menu = "Reclamaciones"
          st.session_state.menu_selection = "Reclamaciones"
          st.session_state.active_tab_reclamacion = "Nueva Reclamación"

     def ir_a_reportes():
          st.session_state.menu = "Reportes"
          st.session_state.menu_selection = "Reportes"

     with col1:
         st.button("➕ Registrar Cliente", use_container_width=True, type="secondary", on_click=ir_a_clientes)

     with col2:
         st.button("➕ Emitir Póliza", use_container_width=True, type="secondary", on_click=ir_a_polizas)

     with col3:
         st.button("➕ Crear Reclamación", use_container_width=True, type="secondary", on_click=ir_a_reclamaciones)

     with col4:
         st.button("📊 Generar Reportes", use_container_width=True, type="primary", on_click=ir_a_reportes)

     st.divider()

     # Información de la agencia
     with Database() as db:
          agencia = db.fetch_one("SELECT nombre, telefono, email FROM agencia WHERE idagencia = 1;")

     if agencia:
          with st.container(border=True):
               st.markdown("🏢 **Información de la Agencia**")
               col1_ag, col2_ag, col3_ag = st.columns(3)
               with col1_ag:
                    st.markdown(f"**Nombre:** {agencia['nombre']}")
               with col2_ag:
                    st.markdown(f"**Teléfono:** {agencia['telefono']}")
               with col3_ag:
                    st.markdown(f"**Email:** {agencia['email']}")
     else:
          st.info("ℹ️ Complete la ficha de la agencia en la sección de Reportes.")

     # Últimas actividades
     st.divider()
     st.subheader("🔄 Actividades Recientes")

     with Database() as db:
          ultimas_polizas = db.fetch_all(
               """
               SELECT p.idpoliza, c.nombre || ' ' || c.apellidos as cliente,
                    p.fecha_inicio as fechainicio, ep.nombre as estado
               FROM poliza p
               JOIN cliente c ON p.idcliente = c.idcliente
               JOIN estado_poliza ep ON p.idestadopoliza = ep.idestadopoliza
               ORDER BY p.fecha_inicio DESC
               LIMIT 5;
               """
          )

          ultimas_reclamaciones = db.fetch_all(
               """
               SELECT r.idreclamacion, p.idpoliza,
                    c.nombre || ' ' || c.apellidos as cliente,
                    r.fecha_siniestro as fechasiniestro, er.nombre as estado
               FROM reclamacion r
               JOIN poliza p ON r.idpoliza = p.idpoliza
               JOIN cliente c ON p.idcliente = c.idcliente
               JOIN estado_reclamacion er ON r.idestadoreclamacion = er.idestadoreclamacion
               ORDER BY r.fecha_siniestro DESC
               LIMIT 5;
               """
          )

     col_p, col_r = st.columns(2)

     with col_p:
          with st.container(border=True):
               st.markdown("📋 **Últimas pólizas emitidas**")
               st.divider()
               if ultimas_polizas:
                    for pol in ultimas_polizas:
                        color = "#43A047" if pol['estado'] == 'Activa' else "#FB8C00" if pol['estado'] == 'Pendiente' else "#E53935"
                        # Si es string, parsear o formatear la fecha
                        fecha_str = pol['fechainicio'].strftime('%d/%m/%Y') if hasattr(pol['fechainicio'], 'strftime') else str(pol['fechainicio'])
                        st.markdown(f"🔹 **#{pol['idpoliza']}** — {pol['cliente']}<br><small>Inicio: {fecha_str} | Estado: <span style='color:{color}; font-weight:bold;'>{pol['estado']}</span></small>", unsafe_allow_html=True)
                        st.divider()
               else:
                    st.info("No hay pólizas registradas.")

     with col_r:
          with st.container(border=True):
               st.markdown("⚠️ **Últimos siniestros reportados**")
               st.divider()
               if ultimas_reclamaciones:
                    for rec in ultimas_reclamaciones:
                        color = "#FB8C00" if rec['estado'] == 'En Proceso' else "#43A047" if rec['estado'] == 'Pagada' else "#E53935"
                        fecha_str = rec['fechasiniestro'].strftime('%d/%m/%Y') if hasattr(rec['fechasiniestro'], 'strftime') else str(rec['fechasiniestro'])
                        st.markdown(f"🔸 **#{rec['idreclamacion']}** (Póliza #{rec['idpoliza']}) — {rec['cliente']}<br><small>Fecha: {fecha_str} | Estado: <span style='color:{color}; font-weight:bold;'>{rec['estado']}</span></small>", unsafe_allow_html=True)
                        st.divider()
               else:
                    st.info("No hay reclamaciones registradas.")