import streamlit as st

from ui.principal import pagina_principal
from ui.ui_cliente import pagina_clientes
from ui.polizas import pagina_polizas
from ui.reclamaciones import pagina_reclamaciones
from ui.reaseguradoras import pagina_reaseguradoras
from ui.reportes import pagina_reportes
from ui.ui_catalogos import pagina_catalogos


# Inicializar session_state para el menú
if "menu" not in st.session_state:
    st.session_state.menu = "🏠 Principal"


with st.sidebar:
    st.header("📌 Gestión de Seguros")
    st.divider()

    # Usar session_state para mantener la selección
    menu_seleccionado = st.radio(
        " ",
        options=[
            "🏠 Principal",
            "👤 Clientes",
            "📋 Pólizas",
            "📝 Reclamaciones",
            "🏢 Reaseguradoras",
            "📊 Reportes",
            "🗂️ Catálogos"
        ],
        label_visibility="collapsed",
        index=["🏠 Principal", "👤 Clientes", "📋 Pólizas", "📝 Reclamaciones", "🏢 Reaseguradoras", "📊 Reportes", "🗂️ Catálogos"].index(st.session_state.menu)
    )

    # Actualizar session_state
    st.session_state.menu = menu_seleccionado

    st.divider()
    st.caption("© 2026 - Sistema de Gestión de Seguros")


# Renderizar la página seleccionada
if st.session_state.menu == "🏠 Principal":
    pagina_principal()

elif st.session_state.menu == "👤 Clientes":
    pagina_clientes()

elif st.session_state.menu == "📋 Pólizas":
    pagina_polizas()

elif st.session_state.menu == "📝 Reclamaciones":
    pagina_reclamaciones()

elif st.session_state.menu == "🏢 Reaseguradoras":
    pagina_reaseguradoras()

elif st.session_state.menu == "📊 Reportes":
    pagina_reportes()

elif st.session_state.menu == "🗂️ Catálogos":
    pagina_catalogos()