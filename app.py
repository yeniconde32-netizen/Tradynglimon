import streamlit as st
import pandas as pd
import numpy as np
import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="Trading Limón 🍋", page_icon="🍋", layout="wide")

# Metaetiqueta de verificación AdSense
components.html('<meta name="google-adsense-account" content="ca-pub-713840439..."/>')

if "saldo" not in st.session_state:
    st.session_state.saldo = 100.0

st.sidebar.title("🍋 Trading Limón")
st.sidebar.caption("Plataforma Natural & Orgánica de Trading")
opcion = st.sidebar.radio("Navegación", ["📈 Tablero / Trading", "💰 Billetera"])

# Anuncio Lateral
st.sidebar.markdown("---")
st.sidebar.caption("📢 Publicidad")
codigo_adsense_sidebar = """
<div style="text-align:center;">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX"
         crossorigin="anonymous"></script>
    <ins class="adsbygoogle"
         style="display:block"
         data-ad-client="ca-pub-XXXXXXXXXXXXXXXX"
         data-ad-slot="1234567890"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>
         (adsbygoogle = window.adsbygoogle || []).push({});
    </script>
</div>
"""
components.html(codigo_adsense_sidebar, height=300)
