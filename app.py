import streamlit as st
import pandas as pd
from ui.ui_cliente import pagina_clientes
from ui.principal import pagina_principal
from ui.reaseguradoras import pagina_reaseguradoras
from ui.polizas import pagina_polizas
from ui.reclamaciones import pagina_reclamaciones
from ui.ui_catalogos import pagina_catalogos

with st.sidebar:
    st.header("Gestión de Seguros")
    st.divider()
    menu = st.radio(" ",["🏠 Principal", "👤 Clientes", "📋 Pólizas", "📝 Reclamaciones", "🏢 Reaseguradoras", "📊 Reportes", "🗂️ Catálogos"],label_visibility="collapsed")
    st.divider()
   
if menu == "🏠 Principal":
   pagina_principal()

elif menu == "👤 Clientes":
    pagina_clientes()

elif menu == "📋 Pólizas":
    pagina_polizas()

elif menu == "📝 Reclamaciones":
    pagina_reclamaciones()


elif menu == "🏢 Reaseguradoras":
   pagina_reaseguradoras()

elif menu == "📊 Reportes":
    st.title("📊 Reportes")
    st.info("PITOCA.")

elif menu == "🗂️ Catálogos":
    pagina_catalogos()