# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Seguros La Confianza",
    page_icon="💼",
    layout="wide"
)

def aplicar_estilos_tablas():
    st.markdown("""
    <style>
    .table-container {
        overflow-x: auto;
        margin-bottom: 1.5rem;
        border: 1px solid #D2DCB6;
        border-radius: 6px;
        background-color: #F1F3E0;
    }
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.95rem;
        color: #1E251C;
        margin: 0 !important;
    }
    .custom-table th {
        background-color: #D2DCB6;
        color: #1E251C;
        padding: 12px 16px;
        text-align: left;
        border-bottom: 2px solid #778873;
        font-weight: 600;
        white-space: nowrap;
    }
    .custom-table td {
        padding: 10px 16px;
        border-bottom: 1px solid #D2DCB6;
        white-space: nowrap;
    }
    .custom-table tr:hover td {
        background-color: #E6EAD0;
    }
    .custom-table tr:last-child td {
        border-bottom: none;
    }
    </style>
    """, unsafe_allow_html=True)

# Monkey-patch para que todas las tablas usen el nuevo estilo HTML nativo
_original_dataframe = st.dataframe
def _custom_dataframe(data, *args, **kwargs):
    if not isinstance(data, pd.DataFrame):
        try:
            data = pd.DataFrame(data)
        except Exception:
            return _original_dataframe(data, *args, **kwargs)
    html = data.to_html(index=False, classes="custom-table", escape=False)
    st.markdown(f'<div class="table-container">{html}</div>', unsafe_allow_html=True)
st.dataframe = _custom_dataframe

# Monkey-patch para alertas globales (info, warning, success, error)
def _custom_alert(body, color_bg, color_border, color_text, icon=None):
    icon_str = f"{icon} " if icon else ""
    st.markdown(f"""
<div style="background-color: {color_bg}; border-left: 5px solid {color_border}; padding: 12px 16px; border-radius: 4px; color: {color_text}; margin-bottom: 1rem; font-size: 0.95rem;">

{icon_str}{body}

</div>
""", unsafe_allow_html=True)

_original_info = st.info
_original_warning = st.warning
_original_success = st.success
_original_error = st.error

st.info = lambda body, icon=None, *args, **kwargs: _custom_alert(body, "#C3D5D1", "#7FA6A0", "#2A4440", icon)
st.warning = lambda body, icon=None, *args, **kwargs: _custom_alert(body, "#EAE3C8", "#D4A373", "#5C4A2E", icon)
st.success = lambda body, icon=None, *args, **kwargs: _custom_alert(body, "#CDE0C9", "#8DB586", "#2B4527", icon)
st.error = lambda body, icon=None, *args, **kwargs: _custom_alert(body, "#E8C5C1", "#B5655B", "#5C2B27", icon)

# Aplicar los estilos inmediatamente
aplicar_estilos_tablas()
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
