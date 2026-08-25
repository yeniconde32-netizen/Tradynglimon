import streamlit as st
import pandas as pd
import numpy as np
import datetime

st.set_page_config(page_title="Trading Limón 🍋", page_icon="🍋", layout="wide")

if "saldo" not in st.session_state:
    st.session_state.saldo = 100.0

st.sidebar.title("🍋 Trading Limón")
st.sidebar.caption("Plataforma Natural & Orgánica de Trading")
opcion = st.sidebar.radio("Navegación", ["📈 Tablero / Trading", "💰 Billetera & Recompensas", "🏆 Torneo Semanal"])

if opcion == "📈 Tablero / Trading":
    st.header("📈 Tablero de Análisis e Indicadores")
    col1, col2 = st.columns([3, 1])
    with col1:
        np.random.seed(42)
        fechas = pd.date_range(end=datetime.datetime.now(), periods=50, freq="h")
        precios = 100 + np.random.randn(50).cumsum()
        df = pd.DataFrame({"Fecha": fechas, "Precio": precios})
        df["SMA_10"] = df["Precio"].rolling(window=10).mean()
        
        delta = df["Precio"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        st.line_chart(df.set_index("Fecha")[["Precio", "SMA_10"]])
        st.caption("Indicador: Media Móvil Simple (SMA 10)")
        
        with st.expander("Ver Indicador RSI"):
            st.line_chart(df.set_index("Fecha")["RSI"])

    with col2:
        st.metric("Saldo Disponible", f"${st.session_state.saldo:.2f}")
        st.subheader("Operar")
        monto = st.number_input("Monto ($)", min_value=1.0, max_value=st.session_state.saldo, value=10.0)
        tipo = st.selectbox("Dirección", ["COMPRA 🟢", "VENTA 🔴"])
        if st.button("Ejecutar Orden"):
            st.success(f"Orden de {tipo} por ${monto} ejecutada exitosamente.")

elif opcion == "💰 Billetera & Recompensas":
    st.header("💰 Billetera y Retiros")
    st.metric(label="Saldo en Cuenta", value=f"${st.session_state.saldo:.2f}")
    st.markdown("---")
    st.subheader("📺 Ganar saldo viendo videos")
    st.write("Mira un video publicitario corto para recibir **+$5.00** a tu cuenta.")
    if st.button("▶️ Ver Video Publicitario"):
        st.session_state.saldo += 5.0
        st.success("¡Has visto el video! Se añadieron +$5.00 a tu saldo.")
        st.rerun()

    st.markdown("---")
    st.subheader("💳 Retirar Fondos")
    metodo = st.selectbox("Método de Pago", ["Nequi", "Daviplata", "PSE", "PayPal"])
    monto_retiro = st.number_input("Monto a retirar ($)", min_value=10.0, max_value=st.session_state.saldo)
    cuenta = st.text_input("Número de cuenta / Correo receptor")
    if st.button("Solicitar Retiro"):
        if st.session_state.saldo >= monto_retiro:
            st.session_state.saldo -= monto_retiro
            st.success(f"Solicitud de retiro de ${monto_retiro} vía {metodo} enviada.")
            st.rerun()
        else:
            st.error("Saldo insuficiente.")

elif opcion == "🏆 Torneo Semanal":
    st.header("🏆 Torneo Semanal de Traders")
    hoy = datetime.datetime.now()
    dias_restantes = 6 - hoy.weekday()
    st.info(f"⏳ **Tiempo restante para el cierre:** {dias_restantes} días, 12 horas")
    st.subheader("🎁 Tabla de Premios")
    premios_data = {
        "Puesto": ["🥇 1er Lugar", "🥈 2do Lugar", "🥉 3er Lugar"],
        "Premio": ["$150.00 USD", "$75.00 USD", "$25.00 USD"]
    }
    st.table(pd.DataFrame(premios_data))
