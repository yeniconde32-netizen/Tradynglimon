import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
import streamlit.components.v1 as components

# Configuración de página
st.set_page_config(page_title="Trading Limón 🍋", page_icon="🍋", layout="wide")

# -------------------------------------------------------------------
# CONFIGURACIÓN DE ADSENSE (Reemplaza con tus IDs reales)
# -------------------------------------------------------------------
ADSENSE_ID = "ca-pub-XXXXXXXXXXXXXXXX"      # Tu ID de AdSense (Publisher ID)
SLOT_SIDEBAR = "1234567890"                 # ID del anuncio de la barra lateral
SLOT_RECOMPENSAS = "9876543210"              # ID del anuncio de la sección recompensas

# Metaetiqueta global para verificación de sitio en AdSense
components.html(f'<meta name="google-adsense-account" content="{ADSENSE_ID}"/>', height=0)

# Inicialización de Estados
if "saldo" not in st.session_state:
    st.session_state.saldo = 100.0
if "historial" not in st.session_state:
    st.session_state.historial = []

# Menú Lateral
st.sidebar.title("🍋 Trading Limón")
st.sidebar.caption("Plataforma Natural & Orgánica de Trading")

opcion = st.sidebar.radio(
    "Navegación", 
    ["📈 Tablero / Trading", "📺 Ganar Recompensas", "💰 Billetera y Retiros"]
)

# Anuncio en la barra lateral
st.sidebar.markdown("---")
st.sidebar.caption("📢 Publicidad")
codigo_adsense_sidebar = f"""
<div style="text-align:center;">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}" crossorigin="anonymous"></script>
    <ins class="adsbygoogle" style="display:block" data-ad-client="{ADSENSE_ID}" data-ad-slot="{SLOT_SIDEBAR}" data-ad-format="auto" data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
</div>
"""
with st.sidebar:
    components.html(codigo_adsense_sidebar, height=250)

# -------------------------------------------------------------------
# SECCIÓN 1: TABLERO DE TRADING CON VELAS Y MERCADOS
# -------------------------------------------------------------------
if opcion == "📈 Tablero / Trading":
    st.title("📈 Tablero de Trading en Tiempo Real")
    
    col_saldo, col_pnl = st.columns(2)
    col_saldo.metric("Saldo Disponible", f"${st.session_state.saldo:.2f} USD")
    
    # Selección de Mercados y Activos
    mercado = st.selectbox("Selecciona el Mercado", ["Acciones Globales", "Materias Primas (Commodities)"])
    
    activos = {
        "Acciones Globales": {"Apple": "AAPL", "Tesla": "TSLA", "Amazon": "AMZN", "Google": "GOOGL"},
        "Materias Primas (Commodities)": {"Oro": "GC=F", "Plata": "SI=F", "Petróleo Brent": "BZ=F", "Petróleo WTI": "CL=F"}
    }
    
    simbolo_nombre = st.selectbox("Activo a Operar", list(activos[mercado].keys()))
    ticker_simbolo = activos[mercado][simbolo_nombre]
    
    # Obtención de datos reales con yfinance
    df = yf.download(ticker_simbolo, period="1mo", interval="1d")
    
    if not df.empty:
        # Aplanar columnas MultiIndex de yfinance si existen
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        open_series = df['Open'].squeeze()
        high_series = df['High'].squeeze()
        low_series = df['Low'].squeeze()
        close_series = df['Close'].squeeze()
        
        # Gráfico interactivo de Velas (Candlestick)
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=open_series,
            high=high_series,
            low=low_series,
            close=close_series,
            name=simbolo_nombre
        )])
        fig.update_layout(title=f"Gráfico de Velas Japonesas - {simbolo_nombre}", xaxis_title="Fecha", yaxis_title="Precio (USD)", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
        # Extracción segura del precio actual en formato numérico flotante
        val_close = close_series.iloc[-1]
        precio_actual = float(val_close.item() if hasattr(val_close, 'item') else val_close)
        st.write(f"**Precio actual del activo:** ${precio_actual:.2f} USD")
    else:
        precio_actual = 100.0
        st.warning("No se pudieron cargar los datos del mercado en vivo. Usando precio simulado.")

    st.markdown("---")
    st.subheader("⚡ Operación Rápida")
    
    col_tipo, col_monto = st.columns(2)
    tipo_op = col_tipo.radio("Dirección", ["Compra (ALTA)", "Venta (BAJA)"])
    monto_op = col_monto.number_input("Monto a invertir ($)", min_value=1.0, max_value=st.session_state.saldo, value=10.0)
    
    if st.button("Ejecutar Operación"):
        if monto_op <= st.session_state.saldo:
            resultado_pct = np.random.choice([0.85, -1.0], p=[0.55, 0.45])
            pnl = monto_op * resultado_pct
            st.session_state.saldo += pnl
            
            estado = "Ganancia 🚀" if pnl > 0 else "Pérdida 📉"
            st.session_state.historial.append({
                "Fecha": pd.Timestamp.now().strftime("%H:%M:%S"),
                "Activo": simbolo_nombre,
                "Tipo": tipo_op,
                "Monto": f"${monto_op:.2f}",
                "Resultado": estado,
                "PnL": f"${pnl:.2f}"
            })
            
            if pnl > 0:
                st.success(f"¡Operación Exitosa! Ganaste ${pnl:.2f} USD")
            else:
                st.error(f"Operación Cerrada. Pérdida de ${abs(pnl):.2f} USD")
            st.rerun()
        else:
            st.warning("Saldo insuficiente para esta operación.")

# -------------------------------------------------------------------
# SECCIÓN 2: GANAR VIENDO VIDEOS (ADSENSE / RECOMPENSAS)
# -------------------------------------------------------------------
elif opcion == "📺 Ganar Recompensas":
    st.title("📺 Zona de Recompensas")
    st.write("Mira anuncios o videos publicitarios para recargar saldo a tu cuenta y seguir operando.")
    
    st.info("💡 Haz clic en el anuncio interactivo para iniciar la recompensa.")
    
    # Bloque de anuncio principal de AdSense
    codigo_adsense_recompensas = f"""
    <div style="text-align:center; padding: 20px; border: 2px dashed #4CAF50;">
        <h4>Anuncio Patrocinado</h4>
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}" crossorigin="anonymous"></script>
        <ins class="adsbygoogle" style="display:block" data-ad-client="{ADSENSE_ID}" data-ad-slot="{SLOT_RECOMPENSAS}" data-ad-format="auto" data-full-width-responsive="true"></ins>
        <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
    </div>
    """
    components.html(codigo_adsense_recompensas, height=220)
    
    if st.button("🎁 Reclamar Recompensa (+$5.00 USD)"):
        st.session_state.saldo += 5.0
        st.balloons()
        st.success("¡Has recibido $5.00 USD en tu saldo!")
        st.rerun()

# -------------------------------------------------------------------
# SECCIÓN 3: BILLETERA Y RETIROS (NEQUI, DAVIPLATA, PSE, PAYPAL)
# -------------------------------------------------------------------
elif opcion == "💰 Billetera y Retiros":
    st.title("💰 Tu Billetera")
    st.metric("Saldo Total", f"${st.session_state.saldo:.2f} USD")
    
    st.markdown("---")
    st.subheader("💸 Solicitar Retiro de Fondos")
    
    metodo = st.selectbox("Selecciona la plataforma de pago", ["Nequi", "DaviPlata", "PSE", "PayPal"])
    monto_retiro = st.number_input("Monto a retirar ($)", min_value=5.0, max_value=st.session_state.saldo, value=10.0)
    
    if metodo in ["Nequi", "DaviPlata"]:
        cuenta = st.text_input("Número de Teléfono Registrado")
    elif metodo == "PayPal":
        cuenta = st.text_input("Correo electrónico de PayPal")
    else:
        cuenta = st.text_input("Número de Documento / Cuenta Bancaria")
        
    if st.button("Confirmar Retiro"):
        if cuenta:
            if monto_retiro <= st.session_state.saldo:
                st.session_state.saldo -= monto_retiro
                st.success(f"Solicitud enviada con éxito. Se procesará el pago de ${monto_retiro:.2f} USD a tu cuenta de {metodo} ({cuenta}).")
                st.rerun()
            else:
                st.warning("Fondos insuficientes para retirar este monto.")
        else:
            st.error("Por favor completa los datos de tu cuenta para el retiro.")

    st.markdown("---")
    st.subheader("📜 Historial de Operaciones")
    if st.session_state.historial:
        st.table(pd.DataFrame(st.session_state.historial))
    else:
        st.write("Aún no has realizado operaciones en esta sesión.")
