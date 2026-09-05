import streamlit as st
import pandas as pd
import numpy as np
import time

# Configuración de la página
st.set_page_config(
    page_title="Mimo Trading Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS estilo IQ Option (Modo oscuro financiero)
st.markdown("""
    <style>
    .main {
        background-color: #121824;
        color: #ffffff;
    }
    .metric-card {
        background-color: #1e2636;
        border: 1px solid #2a3447;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- INICIALIZAR ESTADO DE LA CUENTA -----------------
if 'balance' not in st.session_state:
    st.session_state.balance = 10000.0  # Saldo inicial de prueba (Demo)
if 'account_type' not in st.session_state:
    st.session_state.account_type = "Cuenta Demo"
if 'history' not in st.session_state:
    st.session_state.history = []

# ----------------- BARRA LATERAL (PANEL DE CONTROL) -----------------
st.sidebar.title("📊 Mimo Trading")
st.sidebar.markdown(f"**Tipo de Cuenta:** `{st.session_state.account_type}`")

# Selector de cuenta Demo / Real
acc_choice = st.sidebar.selectbox("Cambiar Modo", ["Cuenta Demo ($10,000)", "Cuenta Real"])
if "Demo" in acc_choice:
    st.session_state.account_type = "Cuenta Demo"
else:
    st.session_state.account_type = "Cuenta Real (Simulada)"

st.sidebar.markdown("---")
st.sidebar.metric(label="Saldo Disponible", value=f"${st.session_state.balance:,.2f}")

# Selector de Activo / Bolsa
asset = st.sidebar.selectbox("Activo Financiero", [
    "EUR/USD (Divisas)", 
    "BTC/USD (Cripto)", 
    "ETH/USD (Cripto)", 
    "Apple Inc. (Acciones)", 
    "Tesla (Acciones)"
])

# Monto de la inversión
investment = st.sidebar.number_input("Monto de Inversión ($)", min_value=1.0, max_value=st.session_state.balance, value=50.0, step=10.0)

# Tiempo de expiración
expiration = st.sidebar.selectbox("Tiempo de Expiración", ["1 Minuto", "5 Minutos", "15 Minutos"])

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ Panel de Operaciones")
col_call, col_put = st.sidebar.columns(2)

# ----------------- PANTALLA PRINCIPAL -----------------
st.title(f"💹 Panel de Mercado: {asset}")
st.write("Gr oficial de comportamiento de precios en tiempo real para operaciones binarias y de activos.")

# Simulación de datos de mercado (Gráfico de líneas/velas simulado)
chart_data = pd.DataFrame(
    np.random.randn(30, 1).cumsum() + 100,
    columns=['Precio']
)

# Mostrar Gráfico interactivo en tiempo real
st.line_chart(chart_data, color="#00ffcc", height=400)

# ----------------- LÓGICA DE COMPRA / VENTA (CALL / PUT) -----------------
with col_call:
    if st.button("🟢 CALL (Sube)", type="primary"):
        if st.session_state.balance >= investment:
            st.session_state.balance -= investment
            # Simulamos un resultado rápido (50% probabilidad de ganar o perder para pruebas)
            resultado = np.random.choice(["Ganada", Pérdida := "Perdida"], p=[0.5, 0.5])
            ganancia = investment * 1.85 if resultado == "Ganada" else 0
            
            if resultado == "Ganada":
                st.session_state.balance += ganancia
                st.sidebar.success(f"¡Operación CALL Exitosa! +${ganancia - investment:,.2f}")
            else:
                st.sidebar.error(f"Operación CALL Perdida. -${investment:,.2f}")
                
            st.session_state.history.insert(0, {"Activo": asset, "Tipo": "CALL", "Monto": investment, "Resultado": resultado})
            st.rerun()
        else:
            st.sidebar.warning("Saldo insuficiente.")

with col_put:
    if st.button("🔴 PUT (Baja)", type="secondary"):
        if st.session_state.balance >= investment:
            st.session_state.balance -= investment
            resultado = np.random.choice(["Ganada", "Perdida"], p=[0.5, 0.5])
            ganancia = investment * 1.85 if resultado == "Ganada" else 0
            
            if resultado == "Ganada":
                st.session_state.balance += ganancia
                st.sidebar.success(f"¡Operación PUT Exitosa! +${ganancia - investment:,.2f}")
            else:
                st.sidebar.error(f"Operación PUT Perdida. -${investment:,.2f}")
                
            st.session_state.history.insert(0, {"Activo": asset, "Tipo": "PUT", "Monto": investment, "Resultado": resultado})
            st.rerun()
        else:
            st.sidebar.warning("Saldo insuficiente.")

# ----------------- HISTORIAL DE TRANSACCIONES -----------------
st.markdown("---")
st.subheader("📜 Historial de Transacciones Recientes")
if len(st.session_state.history) > 0:
    df_history = pd.DataFrame(st.session_state.history)
    st.dataframe(df_history, use_container_width=True)
else:
    st.info("Aún no hay operaciones registradas en esta sesión. ¡Realiza tu primera orden en el panel izquierdo!")
