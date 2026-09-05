import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sqlite3

# Configuración de la página
st.set_page_config(
    page_title="Mimo Trading Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS avanzados (Modo oscuro financiero estilo IQ Option)
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e14;
        color: #ffffff;
    }
    section[data-testid="stSidebar"] {
        background-color: #121824;
        color: #ffffff;
    }
    .metric-card {
        background-color: #1a2233;
        border: 1px solid #2a3447;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    div.stButton > button:first-child {
        border-radius: 8px;
        font-weight: bold;
        padding: 12px;
        color: white;
        width: 100%;
    }
    .news-box {
        background-color: #161f30;
        border-left: 4px solid #00ffcc;
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- INICIALIZAR BASE DE DATOS Y USUARIOS -----------------
def init_trading_db():
    conn = sqlite3.connect('mimo_trading.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            balance_demo REAL DEFAULT 10000.0,
            balance_real REAL DEFAULT 0.0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            asset TEXT,
            type TEXT,
            amount REAL,
            result TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_trading_db()

# Control de sesión de usuario
if 'mimo_user' not in st.session_state:
    st.session_state.mimo_user = "TraderPro"

# Asegurar que el usuario existe en la BD
def get_user_balances(username):
    conn = sqlite3.connect('mimo_trading.db')
    c = conn.cursor()
    c.execute("SELECT balance_demo, balance_real FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO users (username, balance_demo, balance_real) VALUES (?, 10000.0, 0.0)", (username,))
        conn.commit()
        row = (10000.0, 0.0)
    conn.close()
    return row

demo_bal, real_bal = get_user_balances(st.session_state.mimo_user)

# ----------------- BARRA LATERAL (NAVEGACIÓN Y DEPÓSITOS) -----------------
st.sidebar.title("💎 Mimo Trading")
menu = st.sidebar.radio("Secciones", ["Panel de Operaciones (Trading)", "Depositos y Retiros (Real)", "Educación y Noticias"])

st.sidebar.markdown("---")
acc_mode = st.sidebar.selectbox("Modo de Cuenta", ["Cuenta Demo", "Cuenta Real"])

current_balance = demo_bal if acc_mode == "Cuenta Demo" else real_bal
st.sidebar.metric(label=f"Saldo en {acc_mode}", value=f"${current_balance:,.2f}")

# ----------------- 1. PANEL DE OPERACIONES (TRADING) -----------------
if menu == "Panel de Operaciones (Trading)":
    st.title("💹 Mimo Trading Room - Alta Precisión")
    
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
    with col_ctrl1:
        asset = st.selectbox("Activo / Bolsa", ["EUR/USD (Divisas Forex)", "BTC/USD (Criptomonedas)", "AAPL (Acciones Apple)", "TSLA (Acciones Tesla)"])
    with col_ctrl2:
        investment = st.number_input("Monto de Inversión ($)", min_value=1.0, max_value=float(current_balance) if current_balance > 0 else 1.0, value=50.0, step=10.0)
    with col_ctrl3:
        expiration = st.selectbox("Tiempo de Expiración", ["30 Segundos", "1 Minuto", "5 Minutos"])

    # Gráfico de comportamiento en vivo
    chart_data = pd.DataFrame(
        np.random.randn(40, 1).cumsum() + 105,
        columns=['Precio en Vivo']
    )
    
    st.line_chart(chart_data, color="#00ffcc", height=350)
    
    # Botones de Operación Rápida CALL / PUT con indicador dinámico
    st.markdown("### ⚡ Ejecución Rápida")
    c_call, c_put = st.columns(2)
    
    with c_call:
        if st.button("🟢 CALL (COMPRAR / SUBIR)", type="primary"):
            if current_balance >= investment:
                # Actualizar saldo en base de datos
                conn = sqlite3.connect('mimo_trading.db')
                c = conn.cursor()
                won = np.random.choice([True, False], p=[0.55, 0.45]) # Probabilidad realista
                profit = investment * 1.85 if won else 0
                
                if acc_mode == "Cuenta Demo":
                    new_bal = demo_bal - investment + profit
                    c.execute("UPDATE users SET balance_demo = ? WHERE username = ?", (new_bal, st.session_state.mimo_user))
                else:
                    new_bal = real_bal - investment + profit
                    c.execute("UPDATE users SET balance_real = ? WHERE username = ?", (new_bal, st.session_state.mimo_user))
                
                res_txt = "Ganada" if won else "Perdida"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("INSERT INTO transactions (username, asset, type, amount, result, timestamp) VALUES (?, ?, 'CALL', ?, ?, ?)",
                          (st.session_state.mimo_user, asset, investment, res_txt, timestamp))
                conn.commit()
                conn.close()
                
                if won:
                    st.success(f"📈 ¡Operación CALL Ganada! +${profit - investment:,.2f}")
                else:
                    st.error(f"📉 Operación CALL Perdida. -${investment:,.2f}")
                st.rerun()
            else:
                st.warning("Fondos insuficientes para esta operación.")

    with c_put:
        if st.button("🔴 PUT (VENDER / BAJAR)", type="secondary"):
            if current_balance >= investment:
                conn = sqlite3.connect('mimo_trading.db')
                c = conn.cursor()
                won = np.random.choice([True, False], p=[0.55, 0.45])
                profit = investment * 1.85 if won else 0
                
                if acc_mode == "Cuenta Demo":
                    new_bal = demo_bal - investment + profit
                    c.execute("UPDATE users SET balance_demo = ? WHERE username = ?", (new_bal, st.session_state.mimo_user))
                else:
                    new_bal = real_bal - investment + profit
                    c.execute("UPDATE users SET balance_real = ? WHERE username = ?", (new_bal, st.session_state.mimo_user))
                
                res_txt = "Ganada" if won else "Perdida"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("INSERT INTO transactions (username, asset, type, amount, result, timestamp) VALUES (?, ?, 'PUT', ?, ?, ?)",
                          (st.session_state.mimo_user, asset, investment, res_txt, timestamp))
                conn.commit()
                conn.close()
                
                if won:
                    st.success(f"📉 ¡Operación PUT Ganada! +${profit - investment:,.2f}")
                else:
                    st.error(f"📈 Operación PUT Perdida. -${investment:,.2f}")
                st.rerun()
            else:
                st.warning("Fondos insuficientes para esta operación.")

    # Historial de transacciones del usuario
    st.markdown("---")
    st.subheader("📜 Historial de Operaciones Financieras")
    conn = sqlite3.connect('mimo_trading.db')
    df_hist = pd.read_sql_query("SELECT timestamp, asset, type, amount, result FROM transactions WHERE username = ? ORDER BY id DESC", conn, params=(st.session_state.mimo_user,))
    conn.close()
    if not df_hist.empty:
        st.dataframe(df_hist, use_container_width=True)
    else:
        st.info("Aún no tienes operaciones registradas.")

# ----------------- 2. DEPÓSITOS Y RETIROS (REAL) -----------------
elif menu == "Depositos y Retiros (Real)":
    st.title("💳 Gestión de Billetera y Fondos Reales")
    st.write("Gestiona tus recargas de capital y retira tus ganancias de forma segura.")
    
    col_dep, col_ret = st.columns(2)
    
    with col_dep:
        st.subheader("📥 Depositar Fondos")
        dep_amount = st.number_input("Monto a Depositar ($ USD)", min_value=10.0, max_value=5000.0, value=100.0, step=10.0)
        gateway = st.selectbox("Método de Pago", ["Tarjeta Débito/Crédito (Stripe)", "PayPal", "Criptomonedas (USDT)"])
        if st.button("Confirmar Depósito Real"):
            conn = sqlite3.connect('mimo_trading.db')
            c = conn.cursor()
            new_real = real_bal + dep_amount
            c.execute("UPDATE users SET balance_real = ? WHERE username = ?", (new_real, st.session_state.mimo_user))
            conn.commit()
            conn.close()
            st.success(f"¡Depósito exitoso de ${dep_amount:,.2f}! Tus fondos ya están disponibles en Cuenta Real.")
            st.rerun()

    with col_ret:
        st.subheader("📤 Retirar Ganancias")
        ret_amount = st.number_input("Monto a Retirar ($ USD)", min_value=10.0, max_value=float(real_bal) if real_bal > 0 else 10.0, value=50.0, step=10.0)
        dest = st.text_input("Cuenta Bancaria / Dirección de Retiro")
        if st.button("Solicitar Retiro"):
            if real_bal >= ret_amount:
                conn = sqlite3.connect('mimo_trading.db')
                c = conn.cursor()
                new_real = real_bal - ret_amount
                c.execute("UPDATE users SET balance_real = ? WHERE username = ?", (new_real, st.session_state.mimo_user))
                conn.commit()
                conn.close()
                st.success(f"Solicitud de retiro de ${ret_amount:,.2f} procesada con éxito.")
                st.rerun()
            else:
                st.error("No tienes suficiente saldo real disponible para este retiro.")

# ----------------- 3. EDUCACIÓN Y NOTICIAS -----------------
elif menu == "Educación y Noticias":
    st.title("🎓 Centro Educativo y Noticias de Mercados")
    st.write("Aprende las estrategias clave de los traders profesionales y mantente al tanto de las noticias globales.")
    
    st.subheader("📰 Últimas Noticias del Mercado")
    st.markdown("""
        <div class="news-box">
            <h4>💡 EUR/USD reacciona a los datos de inflación de la Eurozona</h4>
            <p>Los analistas recomiendan cautela en los pares de divisas europeos durante la sesión de la tarde debido a variaciones imprevistas en los tipos de interés.</p>
        </div>
        <div class="news-box">
            <h4>🚀 Bitcoin (BTC) rompe resistencia clave superando niveles históricos</h4>
            <p>La alta volatilidad en criptomonedas abre oportunidades ideales para operaciones de corto plazo (1 a 5 minutos).</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🎥 Videos Educativos Recomendados")
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.write("**1. Cómo leer Velas Japonesas**")
        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") # Video instructivo de ejemplo
    with col_v2:
        st.write("**2. Gestión de Riesgo para Principiantes**")
        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
