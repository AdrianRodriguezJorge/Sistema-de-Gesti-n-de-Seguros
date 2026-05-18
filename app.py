import streamlit as st

from db.queries_agencia import CrudAgencia
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

with st.sidebar:
    st.header("Gestion de Seguros")
    agencia = CrudAgencia().obtener(1)
    if agencia:
        st.text(f"{agencia.nombre}")
    st.divider()
    st.subheader("Menu:")
    menu = st.radio(
        "Seleccione una opción:",
        ["Agencia", "Reaseguradoras", "Clientes", "Pólizas", "Reclamaciones", "Reportes", "Catálogos"],
        label_visibility="collapsed"
    )
st.divider()

mostrar_alertas()
st.divider()

if menu == "Agencia":
    pagina_agencia()
elif menu == "Clientes":
    pagina_clientes()
elif menu == "Pólizas":
    pagina_polizas()
elif menu == "Reclamaciones":
    pagina_reclamaciones()
elif menu == "Reaseguradoras":
    pagina_reaseguradoras()
elif menu == "Reportes":
    pagina_reportes()
elif menu == "Catálogos":
    pagina_catalogos()
