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
    initial_sidebar_state="collapsed"
)

# Estilos CSS avanzados (Modo oscuro financiero impecable y botones modernos)
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e14;
        color: #ffffff;
    }
    .metric-container {
        background-color: #161f30;
        border: 1px solid #2a3447;
        padding: 10px 15px;
        border-radius: 8px;
        display: inline-block;
        margin-bottom: 10px;
    }
    /* Botones principales de pestañas */
    div.stButton > button:first-child {
        border-radius: 8px;
        font-weight: bold;
        padding: 12px;
        color: white;
        width: 100%;
        background-color: #1a2233;
        border: 1px solid #2a3447;
    }
    div.stButton > button:hover {
        background-color: #2a3447;
        border-color: #00ffcc;
    }
    .news-box {
        background-color: #161f30;
        border-left: 4px solid #ff4b4b;
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    .status-win {
        background-color: rgba(0, 255, 204, 0.15);
        border: 1px solid #00ffcc;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        color: #00ffcc;
        font-weight: bold;
        font-size: 18px;
    }
    .status-loss {
        background-color: rgba(255, 75, 75, 0.15);
        border: 1px solid #ff4b4b;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        color: #ff4b4b;
        font-weight: bold;
        font-size: 18px;
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

if 'mimo_user' not in st.session_state:
    st.session_state.mimo_user = "TraderPro"

if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Trading"

if 'acc_mode' not in st.session_state:
    st.session_state.acc_mode = "Cuenta Demo"

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
current_balance = demo_bal if st.session_state.acc_mode == "Cuenta Demo" else real_bal

# ----------------- ENCABEZADO Y CONTROL DE CUENTA VISIBLE -----------------
st.title("💎 Mimo Trading Platform")

col_top1, col_top2 = st.columns([2, 1])
with col_top1:
    st.session_state.acc_mode = st.selectbox("Modo de Cuenta Activa", ["Cuenta Demo", "Cuenta Real"], key="selectbox_acc")
with col_top2:
    st.metric(label=f"Saldo Disponible", value=f"${current_balance:,.2f}")

st.markdown("---")

# ----------------- NAVEGACIÓN SUPERIOR TÁCTIL (Pestañas limpias) -----------------
col_n1, col_n2, col_n3 = st.columns(3)
with col_n1:
    if st.button("📈 Sala Trading"):
        st.session_state.active_tab = "Trading"
        st.rerun()
with col_n2:
    if st.button("💳 Billetera / Fondos"):
        st.session_state.active_tab = "Billetera"
        st.rerun()
with col_n3:
    if st.button("📰 Noticias y Gráficos"):
        st.session_state.active_tab = "Noticias"
        st.rerun()

st.markdown("---")

# ----------------- 1. PANEL DE OPERACIONES (TRADING) -----------------
if st.session_state.active_tab == "Trading":
    st.subheader("💹 Sala de Operaciones - Mercados Globales")
    
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
    with col_ctrl1:
        asset = st.selectbox("Seleccionar Activo / Bolsa", [
            "GOLD (Oro - XAU/USD)", 
            "SILVER (Plata - XAG/USD)", 
            "CRUDE OIL (Petróleo WTI)", 
            "BRENT OIL (Petróleo Brent)",
            "EUR/USD (Euro / Dólar)", 
            "GBP/USD (Libra / Dólar)", 
            "USD/JPY (Dólar / Yen)", 
            "AUD/USD (Dólar Australiano)",
            "BTC/USD (Bitcoin)", 
            "ETH/USD (Ethereum)", 
            "SOL/USD (Solana)", 
            "BNB/USD (Binance Coin)",
            "GOOGL (Google / Alphabet)", 
            "TSLA (Tesla Inc.)", 
            "AAPL (Apple Inc.)", 
            "AMZN (Amazon)", 
            "MSFT (Microsoft)"
        ])
    with col_ctrl2:
        max_inv = float(current_balance) if current_balance >= 1.0 else 1.0
        investment = st.number_input("Monto de Inversión ($)", min_value=1.0, max_value=max_inv, value=min(50.0, max_inv), step=10.0)
    with col_ctrl3:
        expiration = st.selectbox("Tiempo de Expiración", ["30 Segundos", "1 Minuto", "5 Minutos", "15 Minutos"])

    # Botones de Ejecución Rápida
    st.markdown("### ⚡ Ejecución Rápida de Órdenes")
    c_call, c_put = st.columns(2)
    
    with c_call:
        if st.button("🟢 CALL (COMPRAR / SUBIR)", type="primary"):
            if current_balance >= investment:
                conn = sqlite3.connect('mimo_trading.db')
                c = conn.cursor()
                won = np.random.choice([True, False], p=[0.55, 0.45])
                profit = investment * 1.85 if won else 0
                
                if st.session_state.acc_mode == "Cuenta Demo":
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
                st.warning("Fondos insuficientes.")

    with c_put:
        if st.button("🔴 PUT (VENDER / BAJAR)"):
            if current_balance >= investment:
                conn = sqlite3.connect('mimo_trading.db')
                c = conn.cursor()
                won = np.random.choice([True, False], p=[0.55, 0.45])
                profit = investment * 1.85 if won else 0
                
                if st.session_state.acc_mode == "Cuenta Demo":
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
                st.warning("Fondos insuficientes.")

    # Gráfico Dinámico
    st.markdown(f"**Gráfico de Precios en Vivo: {asset} (Temporalidad: {expiration})**")
    base_price = 150.0 if "Tesla" in asset or "Google" in asset else 105.0
    chart_data = pd.DataFrame(
        np.random.normal(0, 1.5, size=(50, 1)).cumsum() + base_price,
        columns=['Precio de Mercado']
    )
    st.line_chart(chart_data, color="#00ffcc", height=340)

    # Indicador de Estado en Vivo (Ganando / Perdiendo)
    st.markdown("### 📊 Estado de Posición Actual en Tiempo Real")
    conn = sqlite3.connect('mimo_trading.db')
    c = conn.cursor()
    c.execute("SELECT type, amount, result FROM transactions WHERE username = ? ORDER BY id DESC LIMIT 1", (st.session_state.mimo_user,))
    last_trade = c.fetchone()
    conn.close()

    if last_trade:
        t_type, t_amt, t_res = last_trade
        if t_res == "Ganada":
            st.markdown(f"""
                <div class="status-win">
                    🟢 ¡ESTADO: GANANDO POSICIÓN! (+{t_type} en {asset})<br>
                    <span style="font-size: 14px; color: #ffffff;">La línea de tendencia favorece tu operación activa. Margen en verde.</span>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="status-loss">
                    🔴 ¡ESTADO: PERDIENDO POSICIÓN! (-{t_type} en {asset})<br>
                    <span style="font-size: 14px; color: #ffffff;">El mercado se movió en contra de tu orden. Margen en rojo.</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Realiza una orden CALL o PUT para activar el indicador visual de ganancia/pérdida en tiempo real.")

    # Historial de transacciones
    st.markdown("---")
    st.subheader("📜 Historial de Operaciones Financieras")
    conn = sqlite3.connect('mimo_trading.db')
    df_hist = pd.read_sql_query("SELECT timestamp, asset, type, amount, result FROM transactions WHERE username = ? ORDER BY id DESC", conn, params=(st.session_state.mimo_user,))
    conn.close()
    if not df_hist.empty:
        st.dataframe(df_hist, use_container_width=True)
    else:
        st.info("Aún no tienes operaciones registradas en esta sesión.")

# ----------------- 2. DEPÓSITOS Y RETIROS (BILLETERA) -----------------
elif st.session_state.active_tab == "Billetera":
    st.subheader("💳 Gestión de Billetera y Fondos Reales")
    st.write("Administra los fondos de tu cuenta real y retira tus ganancias de manera segura.")
    
    col_dep, col_ret = st.columns(2)
    
    with col_dep:
        st.markdown("### 📥 Depositar Fondos")
        dep_amount = st.number_input("Monto a Depositar ($ USD)", min_value=10.0, max_value=5000.0, value=100.0, step=10.0, key="dep_input")
        gateway = st.selectbox("Método de Pago", ["Tarjeta Débito/Crédito (Stripe)", "PayPal", "Criptomonedas (USDT)"], key="gate_input")
        if st.button("Confirmar Depósito Real"):
            conn = sqlite3.connect('mimo_trading.db')
            c = conn.cursor()
            new_real = real_bal + dep_amount
            c.execute("UPDATE users SET balance_real = ? WHERE username = ?", (new_real, st.session_state.mimo_user))
            conn.commit()
            conn.close()
            st.success(f"¡Depósito exitoso de ${dep_amount:,.2f}! Fondos acreditados en Cuenta Real.")
            st.rerun()

    with col_ret:
        st.markdown("### 📤 Retirar Ganancias")
        max_ret = float(real_bal) if real_bal >= 10.0 else 10.0
        val_ret = 50.0 if real_bal >= 50.0 else max_ret
        ret_amount = st.number_input("Monto a Retirar ($ USD)", min_value=10.0, max_value=max_ret, value=val_ret, step=10.0, key="ret_input")
        dest = st.text_input("Cuenta Bancaria / Dirección de Retiro", key="dest_input")
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
                st.error("Saldo real insuficiente para realizar este retiro.")

# ----------------- 3. EDUCACIÓN Y NOTICIAS -----------------
elif st.session_state.active_tab == "Noticias":
    st.subheader("🎓 Centro Técnico y Noticias de Mercados")
    st.write("Análisis profesionales de gráficos, movimientos de precios y gestión de riesgo.")
    
    st.markdown("""
        <div class="news-box">
            <h4>📈 Oro (GOLD) alcanza máximos históricos por alta demanda institucional</h4>
            <p>Los gráficos de 1 hora muestran ruptura de resistencia clave. Los traders vigilan de cerca los rebotes en soportes técnicos.</p>
        </div>
        <div class="news-box">
            <h4>🛢️ Petróleo WTI reacciona ante recortes imprevistos de producción</h4>
            <p>La volatilidad en materias primas genera oportunidades ideales para operaciones rápidas en temporalidades de 1 a 5 minutos.</p>
        </div>
        <div class="news-box">
            <h4>💻 Acciones de Google (GOOGL) y Tesla (TSLA) bajo lupa técnica</h4>
            <p>Patrones de velas envolventes alcistas detectados en la apertura de la bolsa de Nueva York.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("💡 Consejo de trader: Estudia los patrones de velas y soportes antes de ejecutar operaciones con dinero real en la plataforma.")
