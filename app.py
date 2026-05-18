# -*- coding: utf-8 -*-
import streamlit as st

st.set_page_config(
    page_title="Seguros La Confianza",
    page_icon="💼",
    layout="wide"
)
from db.queries_agencia import CrudAgencia
from ui.ui_principal import pagina_principal
from ui.ui_agencia import pagina_agencia
from ui.ui_cliente import pagina_clientes
from ui.ui_reaseguradoras import pagina_reaseguradoras
from ui.ui_polizas import pagina_polizas
from ui.ui_reclamaciones import pagina_reclamaciones
from ui.ui_catalogos import pagina_catalogos
from ui.ui_reportes import pagina_reportes
from db.validaciones import obtener_resumen_alertas

def mostrar_alertas():
    with st.spinner("Verificando alertas..."):
        alertas = obtener_resumen_alertas(30)
    
    if alertas["total_polizas_vencer"] > 0:
        st.warning(f"Hay {alertas['total_polizas_vencer']} pólizas próximas a vencer")
    if alertas["total_reclamaciones_pendientes"] > 0:
        st.info(f"Hay {alertas['total_reclamaciones_pendientes']} reclamaciones pendientes")

editing_active = st.session_state.get('editing_active', False)

# Inicializar la opción activa del menú en la sesión
if "menu" not in st.session_state:
    st.session_state.menu = "Inicio"

if "menu_selection" not in st.session_state:
    st.session_state.menu_selection = "Inicio"

if "prev_menu" not in st.session_state:
    st.session_state.prev_menu = st.session_state.menu

if st.session_state.prev_menu != st.session_state.menu:
    st.session_state.prev_menu = st.session_state.menu
    st.markdown(
        """
        <img src="x" onerror="
            var main = window.parent.document.querySelector('.main');
            if (main) { main.scrollTo(0,0); }
            window.scrollTo(0,0);
            if (window.parent) { window.parent.scrollTo(0,0); }
        " style="display:none;">
        """,
        unsafe_allow_html=True
    )

with st.sidebar:
    st.header("Gestión de Seguros")
    agencia = CrudAgencia().obtener(1)
    if agencia:
        st.markdown(f"🏢 **{agencia.nombre}**")
    st.divider()
    st.subheader("Menú:")
    
    opciones = ["Inicio", "Agencia", "Reaseguradoras", "Clientes", "Pólizas", "Reclamaciones", "Reportes", "Catálogos"]
    

    
    menu = st.radio(
        "Seleccione una opción:",
        opciones,
        key="menu_selection",
        label_visibility="collapsed",
        disabled=editing_active
    )
    # Sincronizar el estado del menú
    st.session_state.menu = menu
    
    if editing_active:
        st.warning("⚠️ Edición activa. Guarde o cancele para cambiar de opción.")

st.divider()
mostrar_alertas()
st.divider()

if st.session_state.menu == "Inicio":
    pagina_principal()
elif st.session_state.menu == "Agencia":
    pagina_agencia()
elif st.session_state.menu == "Clientes":
    pagina_clientes()
elif st.session_state.menu == "Pólizas":
    pagina_polizas()
elif st.session_state.menu == "Reclamaciones":
    pagina_reclamaciones()
elif st.session_state.menu == "Reaseguradoras":
    pagina_reaseguradoras()
elif st.session_state.menu == "Reportes":
    pagina_reportes()
elif st.session_state.menu == "Catálogos":
    pagina_catalogos()
