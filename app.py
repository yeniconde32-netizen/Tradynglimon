import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Trading Limón", page_icon="🍋", layout="wide")

st.title("🍋 Trading Limón - Plataforma de Trading y Portafolio")
st.write("Bienvenido a tu plataforma profesional de trading para acciones y materias primas.")

# Inicializar estado financiero y portafolio en la sesión
if 'efectivo' not in st.session_state:
    st.session_state.efectivo = 20000.0

if 'portafolio' not in st.session_state:
    st.session_state.portafolio = {
        "AAPL": {"acciones": 2, "tipo": "Acción"},
        "GC=F": {"acciones": 1, "tipo": "Materia Prima"}
    }

# Panel Lateral de Control
st.sidebar.header("Panel de Control")
opcion = st.sidebar.selectbox("Selecciona una opción", ["Mercados y Precios", "Mi Portafolio", "Comprar / Vender"])

# 1. Mercados y Precios
if opcion == "Mercados y Precios":
    st.subheader("Cotizaciones en Vivo")
    simbolos = {"Acciones de Apple (AAPL)": "AAPL", "Oro (GC=F)": "GC=F", "Petróleo Crudo (CL=F)": "CL=F"}
    
    for nombre, ticker in simbolos.items():
        try:
            datos = yf.Ticker(ticker)
            precio_actual = datos.history(period="1d")['Close'].iloc[-1]
            st.metric(label=nombre, value=f"${precio_actual:,.2f} USD")
        except Exception:
            st.warning(f"No se pudo cargar el precio para {nombre}")

# 2. Mi Portafolio
elif opcion == "Mi Portafolio":
    st.subheader("Resumen de tu Cuenta")
    st.write(f"**Efectivo disponible:** ${st.session_state.efectivo:,.2f} USD")
    
    st.subheader("Tus Activos Actuales")
    if st.session_state.portafolio:
        datos_tabla = []
        for ticker, info in st.session_state.portafolio.items():
            try:
                p_act = yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1]
                val_total = p_act * info["acciones"]
                datos_tabla.append({
                    "Ticker": ticker,
                    "Tipo": info["tipo"],
                    "Cantidad": info["acciones"],
                    "Precio Actual": f"${p_act:,.2f}",
                    "Valor Total": f"${val_total:,.2f}"
                })
            except Exception:
                pass
        if datos_tabla:
            st.table(pd.DataFrame(datos_tabla))
    else:
        st.info("Aún no tienes activos en tu portafolio.")

# 3. Comprar / Vender
elif opcion == "Comprar / Vender":
    st.subheader("Ejecutar Operación")
    ticker_op = st.selectbox("Selecciona el Activo", ["AAPL", "GC=F", "CL=F"])
    cantidad_op = st.number_input("Cantidad de unidades", min_value=1, value=1)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Comprar"):
            try:
                p_compra = yf.Ticker(ticker_op).history(period="1d")['Close'].iloc[-1]
                costo_total = p_compra * cantidad_op
                if st.session_state.efectivo >= costo_total:
                    st.session_state.efectivo -= costo_total
                    if ticker_op in st.session_state.portafolio:
                        st.session_state.portafolio[ticker_op]["acciones"] += cantidad_op
                    else:
                        tipo = "Materia Prima" if ticker_op in ["GC=F", "CL=F"] else "Acción"
                        st.session_state.portafolio[ticker_op] = {"acciones": cantidad_op, "tipo": tipo}
                    st.success(f"¡Compra exitosa de {cantidad_op} unidades de {ticker_op}!")
                else:
                    st.error("No tienes suficiente efectivo disponible.")
            except Exception as e:
                st.error(f"Error al ejecutar la compra: {e}")
