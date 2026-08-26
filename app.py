import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. CONFIGURACIÓN E INYECCIÓN EN EL HEAD PARA ADSENSE
# ---------------------------------------------------------
st.set_page_config(
    page_title="Trading Limón 🍋",
    page_icon="🍋",
    layout="wide"
)

# Inyección forzada en el <head> principal para saltar el iframe de Streamlit
head_injector = """
<script>
    var meta = parent.document.createElement('meta');
    meta.name = "google-adsense-account";
    meta.content = "ca-pub-7138404391058836";
    parent.document.getElementsByTagName('head')[0].appendChild(meta);

    var script = parent.document.createElement('script');
    script.async = true;
    script.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7138404391058836";
    script.setAttribute("crossorigin", "anonymous");
    parent.document.getElementsByTagName('head')[0].appendChild(script);
</script>
"""
components.html(head_injector, height=0, width=0)

# ---------------------------------------------------------
# 2. GESTIÓN DE ESTADO (SESSION STATE)
# ---------------------------------------------------------
if "saldo_usd" not in st.session_state:
    st.session_state.saldo_usd = 1000.0
if "saldo_real" not in st.session_state:
    st.session_state.saldo_real = 0.00
if "precio_entrada" not in st.session_state:
    st.session_state.precio_entrada = 0.0
if "posicion_activa" not in st.session_state:
    st.session_state.posicion_activa = False
if "tipo_posicion" not in st.session_state:
    st.session_state.tipo_posicion = None

# ---------------------------------------------------------
# 3. BARRA LATERAL: RETIROS Y MONETIZACIÓN
# ---------------------------------------------------------
st.sidebar.title("🍋 Trading Limón")
st.sidebar.metric("Saldo Demo (USD)", f"${st.session_state.saldo_usd:,.2f}")
st.sidebar.metric("💵 Saldo Real Acumulado", f"${st.session_state.saldo_real:,.2f}")

st.sidebar.markdown("---")
st.sidebar.header("🚀 Ganar Dinero con Anuncios/Videos")
st.sidebar.caption("Mira contenido patrocinado para ganar saldo real convertible y operar o retirar.")

if st.sidebar.button("📺 Ver anuncio (+$0.05 a saldo real)", use_container_width=True):
    st.session_state.saldo_real += 0.05
    st.sidebar.success("¡Recompensa acreditada! +$0.05 USD a tu saldo real.")

if st.sidebar.button("✔️ Completa oferta (+$2.00 a saldo real)", use_container_width=True):
    st.session_state.saldo_real += 2.00
    st.sidebar.success("¡Oferta completada! +$2.00 USD añadidos.")

if st.sidebar.button("▶️ Ver Video Tutorial (+$0.10 real)", use_container_width=True):
    st.session_state.saldo_real += 0.10
    st.sidebar.success("¡Video visto! +$0.10 USD añadidos.")

st.sidebar.markdown("---")
st.sidebar.header("💱 Convertidor & Retiro Real")

tasa_cop = 3900.0
tasa_eur = 0.92

moneda_retiro = st.sidebar.selectbox("Moneda de retiro:", ["COP (Pesos Colombianos)", "USD (Dólares)", "EUR (Euros)"])
metodo_retiro = st.sidebar.selectbox("Método de pago:", ["Nequi", "Daviplata", "PSE", "PayPal"])

if "COP" in moneda_retiro:
    monto_convertido = st.session_state.saldo_real * tasa_cop
    simbolo = "COP $"
elif "EUR" in moneda_retiro:
    monto_convertido = st.session_state.saldo_real * tasa_eur
    simbolo = "€"
else:
    monto_convertido = st.session_state.saldo_real
    simbolo = "USD $"

st.sidebar.info(f"**Valor estimado a retirar:**\n\n### {simbolo} {monto_convertido:,.2f}")

max_retiro = max(float(st.session_state.saldo_real), 0.0)
monto_a_retirar = st.sidebar.number_input(
    "Monto a retirar (USD):", 
    min_value=0.0, 
    max_value=max_retiro if max_retiro > 0.0 else 100.0, 
    value=0.0,
    step=1.0
)
numero_cuenta = st.sidebar.text_input("Número de cuenta / Teléfono / Correo:")

if st.sidebar.button("Solicitar Retiro Real", use_container_width=True):
    if st.session_state.saldo_real < monto_a_retirar or monto_a_retirar <= 0:
        st.sidebar.error("Ingresa un monto válido y asegúrate de tener saldo suficiente.")
    elif numero_cuenta.strip() == "":
        st.sidebar.error("Ingresa los datos del método de pago.")
    else:
        st.session_state.saldo_real -= monto_a_retirar
        st.sidebar.success(f"¡Solicitud enviada! Se procesará el envío de {simbolo} {(monto_a_retirar * (tasa_cop if 'COP' in moneda_retiro else (tasa_eur if 'EUR' in moneda_retiro else 1.0))):,.2f} vía {metodo_retiro} a {numero_cuenta}.")

# ---------------------------------------------------------
# 4. GRÁFICOS INTERACTIVOS (VELAS & INDICADOR P&L)
# ---------------------------------------------------------
st.title("📈 Plataforma Trading Limón")

ticker_symbol = st.selectbox("Selecciona un activo:", ["BTC-USD", "ETH-USD", "AAPL", "NVDA", "TSLA"])
periodo = st.select_slider("Temporalidad:", options=["1d", "5d", "1mo", "3mo", "1y"], value="1mo")

data = yf.download(tickers=ticker_symbol, period=periodo, interval="1d")

if not data.empty:
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)

    precio_actual = float(data["Close"].iloc[-1])

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'],
        low=data['Low'], close=data['Close'], name="Velas"
    ))

    if st.session_state.posicion_activa:
        precio_ent = st.session_state.precio_entrada
        pnl = precio_actual - precio_ent if st.session_state.tipo_posicion == "COMPRA" else precio_ent - precio_actual
        color_pnl = "#26a69a" if pnl >= 0 else "#ef5350"
        texto_estado = f"GANANCIA: +${pnl:.2f}" if pnl >= 0 else f"PÉRDIDA: -${abs(pnl):.2f}"

        fig.add_hline(y=precio_ent, line_dash="dash", line_color="gold", annotation_text=f"Entrada: ${precio_ent:.2f}")
        fig.add_hrect(
            y0=precio_ent, y1=precio_actual, fillcolor=color_pnl, opacity=0.25, line_width=0,
            annotation_text=f" {texto_estado} ({st.session_state.tipo_posicion})"
        )

    fig.update_layout(
        title=f"Gráfico — {ticker_symbol} (Precio Actual: ${precio_actual:,.2f})",
        yaxis_title="Precio (USD)", xaxis_title="Fecha", template="plotly_dark", height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🟢 Abrir COMPRA", use_container_width=True):
            st.session_state.posicion_activa = True
            st.session_state.precio_entrada = precio_actual
            st.session_state.tipo_posicion = "COMPRA"
            st.success(f"COMPRA abierta en ${precio_actual:,.2f}")
    with col2:
        if st.button("🔴 Abrir VENTA", use_container_width=True):
            st.session_state.posicion_activa = True
            st.session_state.precio_entrada = precio_actual
            st.session_state.tipo_posicion = "VENTA"
            st.success(f"VENTA abierta en ${precio_actual:,.2f}")
    with col3:
        if st.button("⚪ Cerrar Posición", use_container_width=True):
            if st.session_state.posicion_activa:
                pnl_final = precio_actual - st.session_state.precio_entrada if st.session_state.tipo_posicion == "COMPRA" else st.session_state.precio_entrada - precio_actual
                st.session_state.saldo_usd += pnl_final
                st.session_state.posicion_activa = False
                st.info(f"Posición cerrada. P&L: ${pnl_final:,.2f}")
                st.rerun()
