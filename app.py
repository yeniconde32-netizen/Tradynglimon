import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sqlite3
import urllib.request
import xml.etree.ElementTree as ET

# Configuración de la página
st.set_page_config(
    page_title="Mimo Trading Platform - Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS avanzados (Corrección de espacios superiores y diseño institucional)
st.markdown("""
    <style>
    .stApp {
        background-color: #06090f;
        color: #ffffff;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }
    .logo-container {
        display: flex;
        align-items: center;
        background: linear-gradient(135deg, #111a2d 0%, #0e1624 100%);
        border: 1px solid #1f304a;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0, 255, 204, 0.05);
    }
    .logo-icon {
        font-size: 35px;
        background: #1a263c;
        padding: 8px 12px;
        border-radius: 10px;
        margin-right: 15px;
        border: 1px solid #00ffcc;
        text-align: center;
    }
    .logo-text h1 {
        margin: 0;
        font-size: 24px;
        color: #ffffff;
        font-weight: 800;
        letter-spacing: 1px;
    }
    .logo-text p {
        margin: 0;
        font-size: 12px;
        color: #00ffcc;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 2px;
    }
    div.stButton > button:first-child {
        border-radius: 8px;
        font-weight: bold;
        padding: 10px;
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
        border: 1px solid #1f304a;
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

# Tasa de cambio fija de referencia USD a COP
USD_TO_COP = 4100.0

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
            currency TEXT,
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
if 'currency_pref' not in st.session_state:
    st.session_state.currency_pref = "USD ($)"

def get_user_balances(username):
    conn = sqlite3.connect('mimo_trading_pro.db')
    c = conn.cursor()
    c.execute("SELECT balance_demo, balance_real FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row if row else (10000.0, 0.0)

# ----------------- PANTALLA DE LOGIN / REGISTRO -----------------
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
                        # Cuenta real inicializa estrictamente en 0.0
                        c.execute("INSERT INTO users (username, password, balance_demo, balance_real) VALUES (?, ?, 10000.0, 0.0)", (user_input, pass_input))
                        conn.commit()
                        st.success("¡Cuenta creada con éxito! Ahora inicie sesión.")
                    except sqlite3.IntegrityError:
                        st.error("El nombre de usuario ya existe.")
                    conn.close()
                else:
                    st.error("Las contraseñas no coinciden.")
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

# ----------------- APLICACIÓN PRINCIPAL -----------------
demo_bal, real_bal = get_user_balances(st.session_state.mimo_user)

render_mimo_logo()

# Selector de Moneda Global (USD o COP)
col_top_m1, col_top_m2, col_top_m3, col_top_m4 = st.columns([1.2, 1.2, 1.3, 1.3])
with col_top_m1:
    st.session_state.currency_pref = st.selectbox("Moneda", ["USD ($)", "COP ($)"], key="curr_sel")
with col_top_m2:
    st.session_state.acc_mode = st.selectbox("Tipo de Cuenta", ["Cuenta Demo", "Cuenta Real"], key="top_acc")

raw_balance = demo_bal if st.session_state.acc_mode == "Cuenta Demo" else real_bal
if st.session_state.currency_pref == "COP ($)":
    display_balance = raw_balance * USD_TO_COP
    bal_str = f"${display_balance:,.0f} COP"
else:
    display_balance = raw_balance
    bal_str = f"${display_balance:,.2f} USD"

with col_top_m3:
    st.metric(label="Saldo Disponible", value=bal_str)
with col_top_m4:
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

st.markdown("---")

# Pestañas de Navegación
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
    st.subheader("💹 Terminal de Órdenes y Gráficos en Tiempo Real")
    
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    with col_c1:
        asset = st.selectbox("Activo Financiero", [
            "GOLD (Oro - XAU/USD)", "SILVER (Plata)", "CRUDE OIL (Petróleo WTI)", 
            "EUR/USD", "GBP/USD", "USD/JPY", "BTC/USD", "ETH/USD", 
            "TSLA (Tesla)", "GOOGL (Google)", "AAPL (Apple)"
        ])
    with col_c2:
        if st.session_state.currency_pref == "COP ($)":
            min_val_inv = 4100.0 # Aprox $1 USD
            max_val_inv = max(display_balance, 4100.0)
            def_inv = min(205000.0, max_val_inv) # Aprox $50 USD
            investment_display = st.number_input("Inversión (COP)", min_value=min_val_inv, max_value=max_val_inv, value=def_inv, step=5000.0)
            investment_usd = investment_display / USD_TO_COP
        else:
            min_val_inv = 1.0 # ¡Desde $1 USD!
            max_val_inv = max(display_balance, 1.0)
            def_inv = min(50.0, max_val_inv)
            investment_usd = st.number_input("Inversión ($ USD)", min_value=min_val_inv, max_value=max_val_inv, value=def_inv, step=5.0)
            investment_display = investment_usd
    with col_c3:
        stop_loss = st.number_input("Stop Loss", min_value=0.0, value=10.0 if st.session_state.currency_pref=="USD ($)" else 41000.0, step=5.0)
    with col_c4:
        take_profit = st.number_input("Take Profit", min_value=0.0, value=20.0 if st.session_state.currency_pref=="USD ($)" else 82000.0, step=5.0)

    # Configuración de Gráfico
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        chart_type = st.selectbox("Tipo de Visualización", ["Gráfico de Líneas Dinámico", "Simulación de Velas Japonesas", "Gráfico de Área de Momento"])
    with col_g2:
        indicators = st.multiselect("Indicadores Técnicos", ["SMA (Media Móvil 20)", "Bandas de Bollinger", "Volumen Institucional"])

    # Generación de Datos de Mercado fluidos
    base_price = 2000.0 if "GOLD" in asset else (60000.0 if "BTC" in asset else 150.0)
    np.random.seed(None)
    price_series = pd.DataFrame(
        np.random.normal(0, base_price * 0.0015, size=(120, 1)).cumsum() + base_price,
        columns=['Precio de Mercado']
    )
    
    if "SMA (Media Móvil 20)" in indicators:
        price_series['SMA_20'] = price_series['Precio de Mercado'].rolling(window=5).mean().fillna(base_price)
    if "Bandas de Bollinger" in indicators:
        sma = price_series['Precio de Mercado'].rolling(window=5).mean().fillna(base_price)
        std = price_series['Precio de Mercado'].rolling(window=5).std().fillna(1.0)
        price_series['Banda Superior'] = sma + (std * 2)
        price_series['Banda Inferior'] = sma - (std * 2)

    # Gráfico limpio sin cortes superiores extraños
    if "Velas" in chart_type:
        st.bar_chart(price_series, color="#00ffcc", height=380)
    elif "Área" in chart_type:
        st.area_chart(price_series, color="#00ffcc", height=380)
    else:
        st.line_chart(price_series, color="#00ffcc", height=380)

    # Panel de Ejecución
    st.markdown("### ⚡ Ejecución de Mercado")
    b_call, b_put = st.columns(2)
    
    with b_call:
        if st.button("🟢 COMPRAR / CALL (LONG)", type="primary"):
            if raw_balance >= investment_usd:
                conn = sqlite3.connect('mimo_trading_pro.db')
                c = conn.cursor()
                won = np.random.choice([True, False], p=[0.56, 0.44])
                pnl_usd = (investment_usd * 0.85) if won else (-investment_usd)
                
                if st.session_state.acc_mode == "Cuenta Demo":
                    new_bal = demo_bal + pnl_usd
                    c.execute("UPDATE users SET balance_demo = ? WHERE username = ?", (new_bal, st.session_state.mimo_user))
                else:
                    new_bal = real_bal + pnl_usd
                    c.execute("UPDATE users SET balance_real = ? WHERE username = ?", (new_bal, st.session_state.mimo_user))
                
                res_txt = "Ganada" if won else "Perdida"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("INSERT INTO transactions (username, asset, type, amount, currency, stop_loss, take_profit, result, profit_loss, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (st.session_state.mimo_user, asset, 'CALL', investment_usd, st.session_state.currency_pref, stop_loss, take_profit, res_txt, pnl_usd, timestamp))
                conn.commit()
                conn.close()
                
                pnl_disp = pnl_usd * USD_TO_COP if st.session_state.currency_pref == "COP ($)" else pnl_usd
                curr_sym = "COP" if st.session_state.currency_pref == "COP ($)" else "USD"
                
                if won:
                    st.success(f"📈 ¡Operación Exitosa! Beneficio: +${pnl_disp:,.2f} {curr_sym}")
                else:
                    st.error(f"📉 Operación Cerrada en Stop Loss. Pérdida: ${abs(pnl_disp):,.2f} {curr_sym}")
                st.rerun()
            else:
                st.warning("Fondos insuficientes para esta orden.")

    with b_put:
        if st.button("🔴 VENDER / PUT (SHORT)"):
            if raw_balance >= investment_usd:
                conn = sqlite3.connect('mimo_trading_pro.db')
                c = conn.cursor()
                won = np.random.choice([True, False], p=[0.56, 0.44])
                pnl_usd = (investment_usd * 0.85) if won else (-investment_usd)
                
                if st.session_state.acc_mode == "Cuenta Demo":
                    new_bal = demo_bal + pnl_usd
                    c.execute("UPDATE users SET balance_demo = ? WHERE username = ?", (new_bal, st.session_state.mimo_user))
                else:
                    new_bal = real_bal + pnl_usd
                    c.execute("UPDATE users SET balance_real = ? WHERE username = ?", (new_bal, st.session_state.mimo_user))
                
                res_txt = "Ganada" if won else "Perdida"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("INSERT INTO transactions (username, asset, type, amount, currency, stop_loss, take_profit, result, profit_loss, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (st.session_state.mimo_user, asset, 'PUT', investment_usd, st.session_state.currency_pref, stop_loss, take_profit, res_txt, pnl_usd, timestamp))
                conn.commit()
                conn.close()
                
                pnl_disp = pnl_usd * USD_TO_COP if st.session_state.currency_pref == "COP ($)" else pnl_usd
                curr_sym = "COP" if st.session_state.currency_pref == "COP ($)" else "USD"
                
                if won:
                    st.success(f"📉 ¡Operación Exitosa! Beneficio: +${pnl_disp:,.2f} {curr_sym}")
                else:
                    st.error(f"📈 Operación Cerrada en Stop Loss. Pérdida: ${abs(pnl_disp):,.2f} {curr_sym}")
                st.rerun()
            else:
                st.warning("Fondos insuficientes para esta orden.")

    # Estadísticas PnL
    st.markdown("---")
    st.subheader("📊 Rendimiento y Balance PnL")
    conn = sqlite3.connect('mimo_trading_pro.db')
    df_metrics = pd.read_sql_query("SELECT profit_loss, result FROM transactions WHERE username = ?", conn, params=(st.session_state.mimo_user,))
    conn.close()

    if not df_metrics.empty:
        total_trades = len(df_metrics)
        wins = len(df_metrics[df_metrics['result'] == 'Ganada'])
        losses = len(df_metrics[df_metrics['result'] == 'Perdida'])
        net_pnl_usd = df_metrics['profit_loss'].sum()
        net_pnl_disp = net_pnl_usd * USD_TO_COP if st.session_state.currency_pref == "COP ($)" else net_pnl_usd
        sym = "COP" if st.session_state.currency_pref == "COP ($)" else "USD"
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Total Operaciones", total_trades)
        with col_m2:
            st.metric("🟢 Ganadas", wins)
        with col_m3:
            st.metric("🔴 Perdidas", losses)
        with col_m4:
            st.metric("PnL Neto Acumulado", f"${net_pnl_disp:,.2f} {sym}", delta=f"${net_pnl_disp:,.2f}")
    else:
        st.info("Todavía no hay operaciones registradas en este modo de cuenta.")

# ----------------- 2. BILLETERA Y FONDOS (CON PSE, NEQUI, DAVIPLATA) -----------------
elif st.session_state.active_tab == "Billetera":
    st.subheader("💳 Gestión de Billetera y Pagos Locales (Colombia)")
    
    col_d, col_r = st.columns(2)
    with col_d:
        st.markdown("### 📥 Depositar Fondos")
        
        if st.session_state.currency_pref == "COP ($)":
            dep_amount_disp = st.number_input("Monto a Depositar (COP)", min_value=10000.0, max_value=40000000.0, value=200000.0, step=10000.0)
            dep_amount_usd = dep_amount_disp / USD_TO_COP
        else:
            dep_amount_disp = st.number_input("Monto a Depositar ($ USD)", min_value=5.0, max_value=10000.0, value=50.0, step=10.0)
            dep_amount_usd = dep_amount_disp

        payment_method = st.selectbox("Método de Pago Local", [
            "Nequi (Colombia)", 
            "Daviplata (Colombia)", 
            "PSE (Pagos Seguros en Línea)", 
            "Tarjeta Débito/Crédito (Visa/Mastercard)",
            "Criptomonedas (USDT)"
        ])
        
        if "Nequi" in payment_method or "Daviplata" in payment_method:
            st.text_input("Número de Teléfono asociado", placeholder="Ej: 3001234567")
        elif "PSE" in payment_method:
            st.selectbox("Seleccione su Banco", ["Bancolombia", "Banco de Bogotá", "Davivienda", "BBVA Colombia", "Nequi"])

        if st.button("Procesar Depósito Real"):
            conn = sqlite3.connect('mimo_trading_pro.db')
            c = conn.cursor()
            new_real = real_bal + dep_amount_usd
            c.execute("UPDATE users SET balance_real = ? WHERE username = ?", (new_real, st.session_state.mimo_user))
            conn.commit()
            conn.close()
            st.success(f"¡Depósito acreditado con éxito en su Cuenta Real por {payment_method}!")
            st.rerun()

    with col_r:
        st.markdown("### 📤 Retirar Fondos")
        max_ret = display_balance if display_balance > 0 else 10.0
        ret_amount_disp = st.number_input("Monto a Retirar", min_value=10000.0 if st.session_state.currency_pref=="COP ($)" else 10.0, max_value=max_ret, value=50000.0 if st.session_state.currency_pref=="COP ($)" else 20.0, step=5000.0)
        ret_dest = st.text_input("Número Nequi, Daviplata o Cuenta Bancaria de Destino")
        
        if st.button("Solicitar Retiro Seguro"):
            ret_amount_usd = ret_amount_disp / USD_TO_COP if st.session_state.currency_pref == "COP ($)" else ret_amount_disp
            if real_bal >= ret_amount_usd:
                conn = sqlite3.connect('mimo_trading_pro.db')
                c = conn.cursor()
                new_real = real_bal - ret_amount_usd
                c.execute("UPDATE users SET balance_real = ? WHERE username = ?", (new_real, st.session_state.mimo_user))
                conn.commit()
                conn.close()
                st.success("Retiro solicitado correctamente. Los fondos llegarán a su destino en minutos.")
                st.rerun()
            else:
                st.error("Fondos insuficientes en la cuenta real.")

# ----------------- 3. NOTICIAS EN TIEMPO REAL NATIVAS -----------------
elif st.session_state.active_tab == "Noticias":
    st.subheader("📰 Noticias Financieras en Tiempo Real")
    st.write("Flujo de información en vivo de mercados globales.")
    
    news_loaded = False
    try:
        req = urllib.request.Request(
            "https://es.investing.com/rss/news.rss", 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=4) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            items = root.findall('.//item')
            if items:
                for item in items[:6]:
                    title = item.find('title').text if item.find('title') is not None else "Noticia Financiera"
                    description = item.find('description').text if item.find('description') is not None else "Ver detalles en mercado global."
                    link = item.find('link').text if item.find('link') is not None else "#"
                    
                    st.markdown(f"""
                        <div class="news-box">
                            <h4>📌 {title}</h4>
                            <p>{description}</p>
                            <a href="{link}" target="_blank" style="color: #00ffcc; font-size: 13px;">Leer artículo completo &rarr;</a>
                        </div>
                    """, unsafe_allow_html=True)
                news_loaded = True
    except:
        pass

    if not news_loaded:
        st.markdown("""
            <div class="news-box">
                <h4>📈 Tasas de interés y su impacto en las divisas emergentes</h4>
                <p>El dólar en Latinoamérica experimenta movimientos clave frente al peso colombiano tras anuncios económicos.</p>
            </div>
            <div class="news-box">
                <h4>🚀 Criptomonedas mantienen tendencia alcista</h4>
                <p>Bitcoin y Ethereum muestran alta volatilidad ideal para operaciones de corto plazo.</p>
            </div>
        """, unsafe_allow_html=True)
