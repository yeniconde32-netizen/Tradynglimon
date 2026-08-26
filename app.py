import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA E INYECCIÓN DE GOOGLE ADSENSE
# ---------------------------------------------------------
st.set_page_config(
    page_title="Trading Limón 🍋",
    page_icon="🍋",
    layout="wide"
)

# Código de script de Google AdSense capturado de tu panel
adsense_script = """
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7138404391058836"
     crossorigin="anonymous"></script>
"""
# Inyección invisible en la aplicación para verificación y anuncios
components.html(adsense_script, height=0, width=0)

# ---------------------------------------------------------
# 2. GESTIÓN DE ESTADO (SESSION STATE)
# ---------------------------------------------------------
if "saldo_usd" not in st.session_state:
    st.session_state.saldo_usd = 1000.0  # Saldo demo inicial
if "precio_entrada" not in st.session_state:
    st.session_state.precio_entrada = 0.0
if "posicion_activa" not in st.session_state:
    st.session_state.posicion_activa = False
if "tipo_posicion" not in st.session_state:
    st.session_state.tipo_posicion = None  # "COMPRA" o "VENTA"

# ---------------------------------------------------------
# 3. BARRA LATERAL (SIDEBAR): CONVERTIDOR Y RETIROS REALES
# ---------------------------------------------------------
st.sidebar.title("🍋 Trading Limón Panel")
st.sidebar.metric(label="Saldo Disponible (USD)", value=f"${st.session_state.saldo_usd:,.2f}")

st.sidebar.markdown("---")
st.sidebar.header("💱 Convertidor & Retiro Real")

# Tasas de cambio aproximadas (puedes ajustarlas o conectar con API)
tasa_cop = 3900.0  # 1 USD = 3,900 COP
tasa_eur = 0.92    # 1 USD = 0.92 EUR

moneda_retiro = st.sidebar.selectbox("Selecciona moneda de retiro:", ["COP (Pesos Colombianos)", "USD (Dólares)", "EUR (Euros)"])
metodo_retiro = st.sidebar.selectbox("Método de pago:", ["Nequi", "Daviplata", "PSE", "PayPal"])

# Cálculo de conversión en tiempo real
if "COP" in moneda_retiro:
    monto_convertido = st.session_state.saldo_usd * tasa_cop
    simbolo = "COP $"
elif "EUR" in moneda_retiro:
    monto_convertido = st.session_state.saldo_usd * tasa_eur
    simbolo = "€"
else:
    monto_convertido = st.session_state.saldo_usd
    simbolo = "USD $"

st.sidebar.info(f"**Valor estimado a retirar:**\n\n### {simbolo} {monto_convertido:,.2f}")

monto_a_retirar = st.sidebar.number_input("Monto a retirar (USD):", min_value=10.0, max_value=float(st.session_state.saldo_usd), value=50.0)
numero_cuenta = st.sidebar.text_input("Número de cuenta / Teléfono / Correo:")

if st.sidebar.button("Solicitar Retiro Real"):
    if numero_cuenta.strip() == "":
        st.sidebar.error("Por favor ingresa los datos de destino para el retiro.")
    else:
        st.session_state.saldo_usd -= monto_a_retirar
        st.sidebar.success(f"¡Solicitud enviada! Enviaremos {simbolo} {(monto_a_retirar * (tasa_cop if 'COP' in moneda_retiro else (tasa_eur if 'EUR' in moneda_retiro else 1.0))):,.2f} vía {metodo_retiro} a {numero_cuenta}.")

# ---------------------------------------------------------
# 4. GRÁFICOS INTERACTIVOS CON MARCADOR DE PÉRDIAS / GANANCIAS
# ---------------------------------------------------------
st.title("📈 Plataforma Trading Limón")

ticker_symbol = st.selectbox("Selecciona un activo para operar:", ["BTC-USD", "ETH-USD", "AAPL", "NVDA", "TSLA"], index=0)
periodo = st.select_slider("Temporalidad:", options=["1d", "5d", "1mo", "3mo", "1y"], value="1mo")

# Obtener datos de yfinance
data = yf.download(tickers=ticker_symbol, period=periodo, interval="1d")

if not data.empty:
    # Ajuste de columnas en caso de MultiIndex de pandas
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)

    precio_actual = float(data["Close"].iloc[-1])

    # Creación del gráfico con Plotly
    fig = go.Figure()

    # Velas japonesas
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Velas"
    ))

    # --- MARCADOR DE PÉRDIAS O GANANCIAS EN EL GRÁFICO ---
    if st.session_state.posicion_activa:
        precio_ent = st.session_state.precio_entrada
        pnl = precio_actual - precio_ent if st.session_state.tipo_posicion == "COMPRA" else precio_ent - precio_actual
        
        # Asignación de color: Verde (Favor / Ganancia), Rojo (En contra / Pérdida)
        color_pnl = "#26a69a" if pnl >= 0 else "#ef5350"
        texto_estado = f"GANANCIA: +${pnl:.2f}" if pnl >= 0 else f"PÉRDIDA: -${abs(pnl):.2f}"

        # Línea horizontal del precio de entrada
        fig.add_hline(
            y=precio_ent, 
            line_dash="dash", 
            line_color="gold", 
            annotation_text=f"Entrada: ${precio_ent:.2f}",
            annotation_position="top left"
        )

        # Región sombreada de P&L
        fig.add_hrect(
            y0=precio_ent, 
            y1=precio_actual,
            fillcolor=color_pnl, 
            opacity=0.25,
            line_width=0,
            annotation_text=f"  {texto_estado} ({st.session_state.tipo_posicion})",
            annotation_position="top right"
        )

    fig.update_layout(
        title=f"Gráfico de Velas — {ticker_symbol} (Precio Actual: ${precio_actual:,.2f})",
        yaxis_title="Precio (USD)",
        xaxis_title="Fecha",
        template="plotly_dark",
        height=550
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------------
    # 5. PANEL DE OPERACIONES (COMPRA / VENTA)
    # ---------------------------------------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🟢 Abrir COMPRA", use_container_width=True):
            st.session_state.posicion_activa = True
            st.session_state.precio_entrada = precio_actual
            st.session_state.tipo_posicion = "COMPRA"
            st.success(f"Posición de COMPRA abierta a ${precio_actual:,.2f}")

    with col2:
        if st.button("🔴 Abrir VENTA", use_container_width=True):
            st.session_state.posicion_activa = True
            st.session_state.precio_entrada = precio_actual
            st.session_state.tipo_posicion = "VENTA"
            st.success(f"Posición de VENTA abierta a ${precio_actual:,.2f}")

    with col3:
        if st.button("⚪ Cerrar Posición", use_container_width=True):
            if st.session_state.posicion_activa:
                pnl_final = precio_actual - st.session_state.precio_entrada if st.session_state.tipo_posicion == "COMPRA" else st.session_state.precio_entrada - precio_actual
                st.session_state.saldo_usd += pnl_final
                st.session_state.posicion_activa = False
                st.session_state.precio_entrada = 0.0
                st.session_state.tipo_posicion = None
                st.info(f"Posición cerrada. Resultado P&L: ${pnl_final:,.2f}")
                st.rerun()
            else:
                st.warning("No tienes ninguna posición abierta.")

else:
    st.error("No se pudieron cargar los datos del activo seleccionado.")
