import streamlit as st
from datetime import date

from db.conexionDB import Database


def pagina_principal():
     st.title("🏠 Sistema de Gestión de Seguros")
     st.caption(f"Fecha: {date.today().strftime('%d/%m/%Y')}")

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

          # Total de reclamaciones pendientes
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
               SELECT COALESCE(SUM(montopagado), 0) as total
               FROM pago
               WHERE EXTRACT(YEAR FROM fechapago) = EXTRACT(YEAR FROM CURRENT_DATE)
                    AND EXTRACT(MONTH FROM fechapago) = EXTRACT(MONTH FROM CURRENT_DATE);
               """
          )
          ingresos_mes = ingresos_mes["total"] if ingresos_mes else 0

     # Mostrar métricas en 4 columnas
     col1, col2, col3, col4 = st.columns(4)

     with col1:
          st.metric("👥 Clientes registrados", total_clientes)

     with col2:
          st.metric("📋 Pólizas activas", polizas_activas)

     with col3:
          st.metric("⏳ Reclamaciones pendientes", reclamaciones_pendientes)

     with col4:
          st.metric("💰 Ingresos del mes", f"${ingresos_mes:,.2f}")

     st.divider()

     # Accesos rápidos
     st.subheader("🚀 Accesos rápidos")

     col1, col2, col3, col4 = st.columns(4)

     with col1:
          if st.button("➕ Nuevo Cliente", use_container_width=True):
               st.session_state.menu = "👤 Clientes"
               st.rerun()

     with col2:
          if st.button("📋 Nueva Póliza", use_container_width=True):
               st.session_state.menu = "📋 Pólizas"
               st.rerun()

     with col3:
          if st.button("📝 Nueva Reclamación", use_container_width=True):
               st.session_state.menu = "📝 Reclamaciones"
               st.rerun()

     with col4:
          if st.button("📊 Ver Reportes", use_container_width=True):
               st.session_state.menu = "📊 Reportes"
               st.rerun()

     st.divider()

     # Información de la agencia
     st.subheader("🏢 Información de la agencia")

     with Database() as db:
          agencia = db.fetch_one("SELECT nombre, telefono, email FROM agencia WHERE idagencia = 1;")

     if agencia:
          col1, col2, col3 = st.columns(3)
          with col1:
               st.markdown(f"**Nombre:** {agencia['nombre']}")
          with col2:
               st.markdown(f"**Teléfono:** {agencia['telefono']}")
          with col3:
               st.markdown(f"**Email:** {agencia['email']}")
     else:
          st.info("ℹ️ Complete la ficha de la agencia en la sección de Reportes.")

     # Últimas actividades
     st.divider()
     st.subheader("📋 Últimas actividades")

     with Database() as db:
          ultimas_polizas = db.fetch_all(
               """
               SELECT p.idpoliza, c.nombre || ' ' || c.apellidos as cliente,
                    p.fechainicio, ep.nombre as estado
               FROM poliza p
               JOIN cliente c ON p.idcliente = c.idcliente
               JOIN estado_poliza ep ON p.idestadopoliza = ep.idestadopoliza
               ORDER BY p.fechainicio DESC
               LIMIT 5;
               """
          )

          ultimas_reclamaciones = db.fetch_all(
               """
               SELECT r.idreclamacion, p.idpoliza,
                    c.nombre || ' ' || c.apellidos as cliente,
                    r.fechasiniestro, er.nombre as estado
               FROM reclamacion r
               JOIN poliza p ON r.idpoliza = p.idpoliza
               JOIN cliente c ON p.idcliente = c.idcliente
               JOIN estado_reclamacion er ON r.idestadoreclamacion = er.idestadoreclamacion
               ORDER BY r.fechasiniestro DESC
               LIMIT 5;
               """
          )

     col1, col2 = st.columns(2)

     with col1:
          st.markdown("#### 📋 Últimas pólizas")
          if ultimas_polizas:
               for pol in ultimas_polizas:
                   st.markdown(f"- **{pol['idpoliza']}** - {pol['cliente']} - *{pol['estado']}*")
          else:
               st.info("No hay pólizas registradas.")

     with col2:
          st.markdown("#### 📝 Últimas reclamaciones")
          if ultimas_reclamaciones:
               for rec in ultimas_reclamaciones:
                 st.markdown(f"- **{rec['idreclamacion']}** - {rec['cliente']} - *{rec['estado']}*")
          else:
               st.info("No hay reclamaciones registradas.")