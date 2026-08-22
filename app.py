
# Actualizando Trading Limón con Metales y Petróleo
with open("app.py", "w", encoding="utf-8") as f:
    f.write('''import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.set_page_config(page_title="Trading Limón", page_icon="🍋", layout="centered")

st.title("🍋 Trading Limón - Versión Global")
st.write("Plataforma profesional de trading con Acciones y Materias Primas en vivo.")

# Inicializar estado financiero y portafolio global
if 'efectivo' not in st.session_state:
    st.session_state.efectivo = 20000.0
if 'portafolio' not in st.session_state:
    st.session_state.portafolio = {
        "AAPL": {"acciones": 2, "tipo": "Acción"},
        "TSLA": {"acciones": 2, "tipo": "Acción"},
        "ORO (GC=F)": {"acciones": 1, "tipo": "Metal"},
        "PLATA (SI=F)": {"acciones": 5, "tipo": "Metal"},
        "PETRÓLEO (CL=F)": {"acciones": 3, "tipo": "Energía"}
    }
if 'historial' not in st.session_state:
    st.session_state.historial = [
        {"tipo": "COMPRA", "activo": "AAPL", "cant": 2, "fecha": "2026-08-20"},
        {"tipo": "COMPRA", "activo": "ORO (GC=F)", "cant": 1, "fecha": "2026-08-21"}
    ]

# Diccionario de activos y sus símbolos reales
tickers_mercado = {
    "Apple (AAPL)": "AAPL",
    "Tesla (TSLA)": "TSLA",
    "Microsoft (MSFT)": "MSFT",
    "Oro (GC=F)": "GC=F",
    "Plata (SI=F)": "SI=F",
    "Petróleo Crudo (CL=F)": "CL=F"
}

# Función para obtener precios reales del mercado
@st.cache_data(ttl=60)
def obtener_precio_actual(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="1d")
        if not df.empty:
            return round(df['Close'].iloc[-1], 2)
    except:
        pass
    return 100.0

# Obtener precios en vivo de todo el catálogo
precios_actuales = {}
for nombre, simbolo in tickers_mercado.items():
    precios_actuales[nombre] = obtener_precio_actual(simbolo)

# Panel Lateral con los Precios en Vivo
st.sidebar.header("📈 Cotizaciones en Vivo")
for nombre, precio in precios_actuales.items():
    st.sidebar.write(f"• **{nombre}**: ${precio:,.2f}")

st.sidebar.markdown("---")
st.sidebar.metric(label="Efectivo Líquido", value=f"${st.session_state.efectivo:,.2f}")

# Sección de Operaciones
st.subheader("⚡ Ejecutar Operación Global")

activo_elegido = st.selectbox("Selecciona un Activo:", list(tickers_mercado.keys()))
simbolo_activo = tickers_mercado[activo_elegido]
precio_unitario = precios_actuales[activo_elegido]

st.info(f"Precio actual de **{activo_elegido}**: **${precio_unitario:,.2f}** por unidad.")

cantidad = st.number_input("Cantidad a operar:", min_value=1, max_value=100, value=1)
costo_total = cantidad * precio_unitario

col1, col2 = st.columns(2)

with col1:
    if st.button("🟢 Comprar"):
        if st.session_state.efectivo >= costo_total:
            st.session_state.efectivo -= costo_total
            if activo_elegido in st.session_state.portafolio:
                st.session_state.portafolio[activo_elegido]["acciones"] += cantidad
            else:
                st.session_state.portafolio[activo_elegido] = {"acciones": cantidad, "tipo": "Global"}

            st.session_state.historial.append({
                "tipo": "COMPRA", "activo": activo_elegido,
                "cant": cantidad, "fecha": str(datetime.date.today())
            })
            st.success(f"¡Compra exitosa de {cantidad} unidad(es) de {activo_elegido}!")
            st.rerun()
        else:
            st.error("No tienes suficiente efectivo disponible.")

with col2:
    if st.button("🔴 Vender"):
        if activo_elegido in st.session_state.portafolio and st.session_state.portafolio[activo_elegido]["acciones"] >= cantidad:
            st.session_state.efectivo += costo_total
            st.session_state.portafolio[activo_elegido]["acciones"] -= cantidad

            st.session_state.historial.append({
                "tipo": "VENTA", "activo": activo_elegido,
                "cant": cantidad, "fecha": str(datetime.date.today())
            })
            st.success(f"¡Venta exitosa de {cantidad} unidad(es) de {activo_elegido}!")
            st.rerun()
        else:
            st.warning("No posees suficientes unidades de este activo para vender.")

# Tabla del Portafolio Actualizado
st.subheader("💼 Tu Portafolio Global")
datos_port = []
for activo, info in st.session_state.portafolio.items():
    cant = info["acciones"]
    simbolo = tickers_mercado.get(activo, "AAPL")
    precio_m = obtener_precio_actual(simbolo)
    total_val = cant * precio_m
    datos_port.append({
        "Activo": activo,
        "Unidades": cant,
        "Precio Actual": f"${precio_m:,.2f}",
        "Valor Total": f"${total_val:,.2f}"
    })
st.table(pd.DataFrame(datos_port))

# Historial
st.subheader("📜 Historial de Operaciones")
if st.session_state.historial:
    st.table(pd.DataFrame(st.session_state.historial))
else:
    st.write("Sin transacciones registradas.")
''')
print("¡Trading Limón actualizado con Oro, Plata y Petróleo!")
