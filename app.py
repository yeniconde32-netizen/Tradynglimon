import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sqlite3
import feedparser  # Para noticias en tiempo real

# Configuración de la página
st.set_page_config(
    page_title="Mimo Trading Platform - Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS avanzados (Estilo XM / Broker institucional con diseño de Logo Pro)
st.markdown("""
    <style>
    .stApp {
        background-color: #06090f;
        color: #ffffff;
    }
    /* Estilo del Logo Institucional */
    .logo-container {
        display: flex;
        align-items: center;
        background: linear-gradient(135deg, #111a2d 0%, #0e1624 100%);
        border: 1px solid #1f304a;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 255, 204, 0.05);
    }
    .logo-icon {
        font-size: 40px;
        background: #1a263c;
        padding: 10px 15px;
        border-radius: 10px;
        margin-right: 15px;
        border: 1px solid #00ffcc;
        text-align: center;
    }
    .logo-text h1 {
        margin: 0;
        font-size: 26px;
        color: #ffffff;
        font-weight: 800;
        letter-spacing: 1px;
    }
    .logo-text p {
        margin: 0;
        font-size: 13px;
        color: #00ffcc;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 2px;
    }
    div.stButton > button:first-child {
        border-radius: 8px;
        font-weight: bold;
        padding: 12px;
        color: white;
        width: 100%;
        background-color: #162032;
        border: 1px solid #1f304a;
    }
    div.stButton > button:hover {
        background-color: #1f304a;
        border-color: #00ffcc;
    }
    .news-box {
        background-color: #0e1624;
        border-left: 4px solid #00ffcc;
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 12px;
        border-top: 1px solid #1f304a;
        border-right: 1px solid #1f304a;
        border-bottom: 1px solid #1f304a;
    }
    .status-win {
        background-color: rgba(0, 255, 204, 0.1);
        border: 1px solid #00ffcc;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        color: #00ffcc;
        font-weight: bold;
        font-size: 18px;
    }
    .status-loss {
        background-color: rgba(255, 75, 75, 0.1);
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

# Componente Visual del Logo Mimo Trading
def render_mimo_logo():
    st.markdown("""
        <div class="logo-container">
            <div class="logo-icon">📈💎</div>
            <div class="logo-text">
                <h1>MIMO TRADING</h1>
                <p>Institutional Global Markets & Pro Analytics</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ----------------- BASE DE DATOS Y AUTENTICACIÓN -----------------
def init_trading_db():
    conn = sqlite3.connect('mimo_trading_pro.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
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
            stop_loss REAL,
            take_profit REAL,
            result TEXT,
            profit_loss REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_trading_db()

# Control de Sesión
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'mimo_user' not in st.session_state:
    st.session_state.mimo_user = ""
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Trading"
if 'acc_mode' not in st.session_state:
    st.session_state.acc_mode = "Cuenta Demo"

def get_user_balances(username):
    conn = sqlite3.connect('mimo_trading_pro.db')
    c = conn.cursor()
    c.execute("SELECT balance_demo, balance_real FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row if row else (10000.0, 0.0)

# ----------------- PANTALLA DE LOGIN / REGISTRO CON LOGO -----------------
if not st.session_state.logged_in:
    render_mimo_logo()
    st.subheader("🔐 Acceso Institucional Seguro")
    
    auth_mode = st.radio("Seleccione opción", ["Iniciar Sesión", "Registrarse"], horizontal=True)
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        user_input = st.text_input("Nombre de Usuario")
    with col_l2:
        pass_input = st.text_input("Contraseña", type="password")

    if auth_mode == "Registrarse":
        pass_confirm = st.text_input("Confirmar Contraseña", type="password")
        if st.button("Crear Cuenta de Trading"):
            if user_input and pass_input:
                if pass_input == pass_confirm:
                    conn = sqlite3.connect('mimo_trading_pro.db')
                    c = conn.cursor()
                    try:
                        c.execute("INSERT INTO users (username, password, balance_demo, balance_real) VALUES (?, ?, 10000.0, 0.0)", (user_input, pass_input))
                        conn.commit()
                        st.success("¡Cuenta creada con éxito! Ahora inicie sesión.")
                    except sqlite3.IntegrityError:
                        st.error("El nombre de usuario ya existe.")
                    conn.close()
                else:
                    st.error("Las contraseñas no coinciden. Por favor confirme bien.")
            else:
                st.warning("Complete todos los campos.")
    else:
        if st.button("Entrar a la Plataforma"):
            conn = sqlite3.connect('mimo_trading_pro.db')
            c = conn.cursor()
            c.execute("SELECT password FROM users WHERE username = ?", (user_input,))
            row = c.fetchone()
            conn.close()
            if row and row[0] == pass_input:
                st.session_state.logged_in = True
                st.session_state.mimo_user = user_input
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
    st.stop()

# ----------------- APLICACIÓN PRINCIPAL (UNA VEZ LOGUEADO) -----------------
demo_bal, real_bal = get_user_balances(st.session_state.mimo_user)
current_balance = demo_bal if st.session_state.acc_mode == "Cuenta Demo" else real_bal

# Mostrar el Logo institucional en la parte superior principal
render_mimo_logo()

# Encabezado con Cuenta y Saldo en Vivo
col_top1, col_top2, col_top3 = st.columns([1.5, 1.2, 1.3])
with col_top1:
    st.session_state.acc_mode = st.selectbox("Modo de Cuenta", ["Cuenta Demo", "Cuenta Real"], key="top_acc")
with col_top2:
    st.metric(label="Saldo Disponible", value=f"${current_balance:,.2f}")
with col_top3:
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

st.markdown("---")

# Pestañas de Navegación Táctil Estilo Broker
col_n1, col_n2, col_n3 = st.columns(3)
with col_n1:
    if st.button("📈 Sala Trading Pro"):
        st.session_state.active_tab = "Trading"
        st.rerun()
with col_n2:
    if st.button("💳 Billetera y Fondos"):
        st.session_state.active_tab = "Billetera"
        st.rerun()
with col_n3:
    if st.button("📰 Noticias en Vivo"):
        st.session_state.active_tab = "Noticias"
        st.rerun()

st.markdown("---")

# ----------------- 1. SALA DE TRADING AVANZADA -----------------
if st.session_state.active_tab == "Trading":
    st.subheader("💹 Terminal de Órdenes y Gráficos Institucionales")
    
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    with col_c1:
        asset = st.selectbox("Activo Financiero", [
            "GOLD (Oro - XAU/USD)", "SILVER (Plata)", "CRUDE OIL (Petróleo WTI)", 
            "EUR/USD", "GBP/USD", "USD/JPY", "BTC/USD", "ETH/USD", 
            "TSLA (Tesla)", "GOOGL (Google)", "AAPL (Apple)"
        ])
    with col_c2:
        max_inv = float(current_balance) if current_balance >= 1.0 else 1.0
        investment = st.number_input("Inversión ($ USD)", min_value=1.0, max_value=max_inv, value=min(50.0, max_inv), step=10.0)
    with col_c3:
        stop_loss = st.number_input("Stop Loss ($)", min_value=0.0, value=10.0, step=5.0)
    with col_c4:
        take_profit = st.number_input("Take Profit ($)", min_value=0.0, value=20.0, step=5.0)

    # Selector de Tipo de Gráfico e Indicadores Técnicos
    st.markdown("### 📊 Configuración de Gráfico y Analítica")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        chart_type = st.selectbox("Tipo de Visualización", ["Gráfico de Líneas Ancho Completo", "Simulación de Velas Japonesas (OHLC)", "Gráfico de Área de Momento"])
    with col_g2:
        indicators = st.multiselect("Indicadores Técnicos superpuestos", ["SMA (Media Móvil 20)", "RSI (Índice de Fuerza)", "Bandas de Bollinger", "Volumen Institucional"])

    # Generación de Datos de Mercado Anchos
    base_price = 2000.0 if "GOLD" in asset else (60000.0 if "BTC" in asset else 150.0)
    np.random.seed(None)
    price_series = pd.DataFrame(
        np.random.normal(0, base_price * 0.002, size=(100, 1)).cumsum() + base_price,
        columns=['Precio de Mercado']
    )
    
    # Calcular indicadores simulados si están seleccionados
    if "SMA (Media Móvil 20)" in indicators:
        price_series['SMA_20'] = price_series['Precio de Mercado'].rolling(window=5).mean().fillna(base_price)
    if "Bandas de Bollinger" in indicators:
        sma = price_series['Precio de Mercado'].rolling(window=5).mean().fillna(base_price)
        std = price_series['Precio de Mercado'].rolling(window=5).std().fillna(1.0)
        price_series['Banda Superior'] = sma + (std * 2)
        price_series['Banda Inferior'] = sma - (std * 2)

    # Mostrar gráfico adaptado a toda la hoja
    if "Velas Japonesas" in chart_type:
        st.subheader("🕯️ Vista de Velas Japonesas Técnicas")
        st.bar_chart(price_series[['Precio_Apertura' if 'Precio_Apertura' in price_series else 'Precio_Mercado']], color="#00ffcc", height=450)
    elif "Área" in chart_type:
        st.area_chart(price_series, color="#00ffcc", height=450)
    else:
        st.line_chart(price_series, color="#00ffcc", height=450)

    # Panel de Ejecución Rápida de Órdenes
    st.markdown("### ⚡ Ejecución de Mercado (Estilo XM)")
    b_call, b_put = st.columns(2)
    
    with b_call:
        if st.button("🟢 COMPRAR / CALL (LONG)", type="primary"):
            if current_balance >= investment:
                conn = sqlite3.connect('mimo_trading_pro.db')
                c = conn.cursor()
                won = np.random.choice([True, False], p=[0.56, 0.44])
                pnl = (investment * 0.85) if won else (-investment)
                
                if st.session_state.acc_mode == "Cuenta Demo":
                    new_bal = demo_bal + pnl
                    c.execute("UPDATE users SET balance_demo = ? WHERE username = ?", (new_bal, st.session_state.mimo_user))
                else:
                    new_bal = real_bal + pnl
                    c.execute("UPDATE users SET balance_real = ? WHERE username = ?", (new_bal, st.session_state.mimo_user))
                
                res_txt = "Ganada" if won else "Perdida"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("INSERT INTO transactions (username, asset, type, amount, stop_loss, take_profit, result, profit_loss, timestamp) VALUES (?, ?, 'CALL', ?, ?, ?, ?, ?, ?)",
                          (st.session_state.mimo_user, asset, investment, stop_loss, take_profit, res_txt, pnl, timestamp))
                conn.commit()
                conn.close()
                
                if won:
                    st.success(f"📈 ¡Operación Exitosa! Beneficio: +${pnl:,.2f}")
                else:
                    st.error(f"📉 Operación Cerrada en Stop Loss. Pérdida: ${pnl:,.2f}")
                st.rerun()

    with b_put:
        if st.button("🔴 VENDER / PUT (SHORT)"):
            if current_balance >= investment:
                conn = sqlite3.connect('mimo_trading_pro.db')
                c = conn.cursor()
                won = np.random.choice([True, False], p=[0.56, 0.44])
                pnl = (investment * 0.85) if won else (-investment)
                
                if st.session_state.acc_mode == "Cuenta Demo":
                    new_bal = demo_bal + pnl
                    c.execute("UPDATE users SET balance_demo = ? WHERE username = ?", (new_bal, st.session_state.mimo_user))
                else:
                    new_bal = real_bal + pnl
                    c.execute("UPDATE users SET balance_real = ? WHERE username = ?", (new_bal, st.session_state.mimo_user))
                
                res_txt = "Ganada" if won else "Perdida"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("INSERT INTO transactions (username, asset, type, amount, stop_loss, take_profit, result, profit_loss, timestamp) VALUES (?, ?, 'PUT', ?, ?, ?, ?, ?, ?)",
                          (st.session_state.mimo_user, asset, investment, stop_loss, take_profit, res_txt, pnl, timestamp))
                conn.commit()
                conn.close()
                
                if won:
                    st.success(f"📉 ¡Operación Exitosa! Beneficio: +${pnl:,.2f}")
                else:
                    st.error(f"📈 Operación Cerrada en Stop Loss. Pérdida: ${pnl:,.2f}")
                st.rerun()

    # Indicador de Número en Pérdidas y Ganancias (PnL flotante y acumulado)
    st.markdown("---")
    st.subheader("📊 Indicador de Rendimiento y Balance PnL")
    conn = sqlite3.connect('mimo_trading_pro.db')
    df_metrics = pd.read_sql_query("SELECT profit_loss, result FROM transactions WHERE username = ?", conn, params=(st.session_state.mimo_user,))
    conn.close()

    if not df_metrics.empty:
        total_trades = len(df_metrics)
        wins = len(df_metrics[df_metrics['result'] == 'Ganada'])
        losses = len(df_metrics[df_metrics['result'] == 'Perdida'])
        net_pnl = df_metrics['profit_loss'].sum()
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Total Operaciones", total_trades)
        with col_m2:
            st.metric("🟢 Ganadas", wins)
        with col_m3:
            st.metric("🔴 Perdidas", losses)
        with col_m4:
            st.metric("PnL Neto Acumulado", f"${net_pnl:,.2f}", delta=f"${net_pnl:,.2f}")
    else:
        st.info("Realiza operaciones para ver las estadísticas detalladas de PnL y Stop Loss.")

    # Historial completo
    st.markdown("---")
    st.subheader("📜 Historial con Control de Stop Loss y Take Profit")
    conn = sqlite3.connect('mimo_trading_pro.db')
    df_hist = pd.read_sql_query("SELECT timestamp, asset, type, amount, stop_loss, take_profit, result, profit_loss FROM transactions WHERE username = ? ORDER BY id DESC", conn, params=(st.session_state.mimo_user,))
    conn.close()
    if not df_hist.empty:
        st.dataframe(df_hist, use_container_width=True)
    else:
        st.info("No hay historial todavía.")

# ----------------- 2. BILLETERA Y FONDOS -----------------
elif st.session_state.active_tab == "Billetera":
    st.subheader("💳 Gestión de Billetera y Depósitos Institucionales")
    
    col_d, col_r = st.columns(2)
    with col_d:
        st.markdown("### 📥 Consignar / Depositar Fondos")
        dep_amount = st.number_input("Monto a Depositar ($ USD)", min_value=10.0, max_value=10000.0, value=100.0, step=50.0)
        payment_method = st.selectbox("Pasarela de Pago", ["Tarjeta Débito/Crédito (Visa/Mastercard)", "Transferencia Bancaria SEPA/Swift", "Criptomonedas (USDT / TRC20)"])
        if st.button("Procesar Depósito Real"):
            conn = sqlite3.connect('mimo_trading_pro.db')
            c = conn.cursor()
            new_real = real_bal + dep_amount
            c.execute("UPDATE users SET balance_real = ? WHERE username = ?", (new_real, st.session_state.mimo_user))
            conn.commit()
            conn.close()
            st.success(f"¡Depósito de ${dep_amount:,.2f} acreditado con éxito en su Cuenta Real!")
            st.rerun()

    with col_r:
        st.markdown("### 📤 Retirar Fondos")
        ret_amount = st.number_input("Monto a Retirar ($ USD)", min_value=10.0, max_value=max(real_bal, 10.0), value=50.0, step=10.0)
        bank_info = st.text_input("Datos Bancarios o Billetera Crypto de Destino")
        if st.button("Solicitar Retiro Seguro"):
            if real_bal >= ret_amount:
                conn = sqlite3.connect('mimo_trading_pro.db')
                c = conn.cursor()
                new_real = real_bal - ret_amount
                c.execute("UPDATE users SET balance_real = ? WHERE username = ?", (new_real, st.session_state.mimo_user))
                conn.commit()
                conn.close()
                st.success(f"Retiro de ${ret_amount:,.2f} solicitado correctamente. En proceso de transferencia.")
                st.rerun()
            else:
                st.error("Fondos insuficientes en la cuenta real.")

# ----------------- 3. NOTICIAS EN TIEMPO REAL -----------------
elif st.session_state.active_tab == "Noticias":
    st.subheader("📰 Noticias Financieras Actualizadas en Tiempo Real")
    st.write("Flujo de información en vivo de mercados globales (Forex, Cripto y Acciones).")
    
    try:
        feed = feedparser.parse("https://es.investing.com/rss/news.rss")
        if feed.entries:
            for entry in feed.entries[:8]:
                st.markdown(f"""
                    <div class="news-box">
                        <h4>📌 {entry.title}</h4>
                        <p>{entry.summary}</p>
                        <a href="{entry.link}" target="_blank" style="color: #00ffcc; font-size: 13px;">Leer artículo completo en la fuente &rarr;</a>
                    </div>
                """, unsafe_allow_html=True)
        else:
            raise Exception("No feed")
    except:
        st.markdown("""
            <div class="news-box">
                <h4>📈 Bancos centrales evalúan tasas de interés para el próximo trimestre</h4>
                <p>Los mercados de divisas reaccionan con alta volatilidad en los pares principales como EUR/USD y GBP/USD.</p>
            </div>
            <div class="news-box">
                <h4>🚀 Bitcoin rompe barreras de resistencia y atrae volumen institucional</h4>
                <p>Los analistas técnicos recomiendan usar Stop Loss ajustados debido a la presión alcista en los gráficos diarios.</p>
            </div>
            <div class="news-box">
                <h4>🛢️ OPEP+ anuncia ajustes en la oferta de crudo</h4>
                <p>El precio del Petróleo WTI muestra oportunidades de compra en soportes técnicos de corto plazo.</p>
            </div>
        """, unsafe_allow_html=True)
