import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Global Trade Terminal", layout="wide")

# --- PROFESSIONAL STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; font-family: 'Inter', sans-serif; }
    div[data-testid="stMetricValue"] { font-family: 'Roboto Mono', monospace; font-size: 20px; color: #E6EDF3; }
    div[data-testid="stMetricLabel"] { font-size: 12px; color: #8B949E; letter-spacing: 1px; }
    section[data-testid="stSidebar"] { background-color: #12151a; border-right: 1px solid #25282e; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Sourcing Card Style */
    .sourcing-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .sourcing-header { color: #58a6ff; font-weight: bold; font-size: 14px; margin-bottom: 8px; }
    .sourcing-row { display: flex; justify-content: space-between; font-size: 13px; color: #c9d1d9; border-bottom: 1px solid #21262d; padding: 6px 0; }
    .sourcing-row:last-child { border-bottom: none; }
    .sourcing-tag { background-color: #238636; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- ASSET & SOURCING DATA ---
ASSETS = {
    "Industrial Metals": { "Copper": "HG=F", "Aluminum": "ALI=F", "Zinc": "ZNC=F", "Nickel (Proxy)": "VALE", "Lithium (ETF)": "LIT", "Steel (ETF)": "SLX" },
    "Precious Metals": { "Gold": "GC=F", "Silver": "SI=F", "Platinum": "PL=F", "Palladium": "PA=F" },
    "Agriculture": { "Wheat": "ZW=F", "Corn": "ZC=F", "Soybean": "ZS=F", "Sugar": "SB=F", "Coffee": "KC=F", "Cocoa": "CC=F", "Cotton": "CT=F" },
    "Forex": { "USD/EUR": "EUR=X", "USD/JPY": "JPY=X", "USD/INR": "INR=X", "USD/CNY": "CNY=X" }
}

# Static "Knowledge Base" for Sourcing (Simulated Intelligence)
SOURCING_DB = {
    "Copper": [
        {"Country": "Chile", "Tag": "Volume Leader", "Note": "World's largest reserves, reliable sea freight."},
        {"Country": "Peru", "Tag": "Low Cost", "Note": "Growing output, competitive labor costs."},
        {"Country": "DRC", "Tag": "High Grade", "Note": "High-grade ore, but higher political risk."},
        {"Country": "China", "Tag": "Refining", "Note": "Top importer & refiner, key for processed wire."},
        {"Country": "USA", "Tag": "Domestic", "Note": "Stable supply, premium pricing."}
    ],
    "Gold": [
        {"Country": "China", "Tag": "Top Producer", "Note": "Largest global output, mostly consumed domestically."},
        {"Country": "Australia", "Tag": "Reliable", "Note": "Massive open-pit mines, easy export regulations."},
        {"Country": "Russia", "Tag": "Sanction Risk", "Note": "Huge reserves, but payment/logistics complex."},
        {"Country": "Canada", "Tag": "ESG Safe", "Note": "High ethical standards, conflict-free sourcing."},
        {"Country": "USA", "Tag": "Nevada Hub", "Note": "Deep liquidity, secure logistics."}
    ],
    "Wheat": [
        {"Country": "Russia", "Tag": "Cheapest", "Note": "Dominates export market with low-cost grain."},
        {"Country": "EU (France)", "Tag": "Quality", "Note": "High protein content, reliable shipping lanes."},
        {"Country": "Australia", "Tag": "Asian Access", "Note": "Key supplier for SE Asia markets."},
        {"Country": "Canada", "Tag": "Premium", "Note": "Best for high-quality baking flour."},
        {"Country": "USA", "Tag": "Backup", "Note": "Strong logistics, acts as global buffer."}
    ],
    "Lithium (ETF)": [
        {"Country": "Australia", "Tag": "Hard Rock", "Note": "Spodumene ore, shipped to China for processing."},
        {"Country": "Chile", "Tag": "Brine/Low Cost", "Note": "Lowest cost production (Salar de Atacama)."},
        {"Country": "China", "Tag": "Refining King", "Note": "Controls 60%+ of global battery-grade processing."},
        {"Country": "Argentina", "Tag": "Emerging", "Note": "Fastest growing brine projects."},
        {"Country": "Zimbabwe", "Tag": "Frontier", "Note": "New massive hard rock discoveries."}
    ]
    # (Fallback logic handles missing items)
}

MACRO_VITALS = { "Brent Crude": "BZ=F", "Natural Gas": "NG=F", "Dollar Index": "DX=F", "Volatility": "^VIX" }

# --- DATA ENGINE ---
@st.cache_data(ttl=300)
def get_batch_data(tickers, period):
    if not tickers: return pd.DataFrame()
    return yf.download(tickers, period=period, group_by='ticker', progress=False, threads=True)

# --- SIDEBAR ---
st.sidebar.markdown("## ⚙️ CONTROLS")
timeframe = st.sidebar.selectbox("RANGE", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "ytd"], index=3)

st.sidebar.markdown("---")
st.sidebar.markdown("## 📊 CHART SETTINGS")
chart_style = st.sidebar.radio("CHART TYPE", ["Line", "Candle"], index=0, horizontal=True)
show_ma = st.sidebar.checkbox("Show Moving Avg", value=True)
ma_period = st.sidebar.slider("MA Period", 10, 200, 50, 10)

st.sidebar.markdown("---")
st.sidebar.markdown("## 🌐 MACRO")
vitals_data = get_batch_data(list(MACRO_VITALS.values()), timeframe)

for name, tick in MACRO_VITALS.items():
    try:
        df = vitals_data[tick] if isinstance(vitals_data.columns, pd.MultiIndex) else vitals_data
        if not df.empty and 'Close' in df:
            df_clean = df['Close'].dropna()
            if len(df_clean) >= 2:
                cur, prev = df_clean.iloc[-1], df_clean.iloc[-2]
                st.sidebar.metric(name, f"{cur:,.2f}", f"{((cur-prev)/prev)*100:+.2f}%")
    except: pass

# --- MAIN DASHBOARD ---
st.markdown("<h3 style='color: white;'>GLOBAL TRADE TERMINAL</h3>", unsafe_allow_html=True)

all_asset_tickers = [t for cat in ASSETS.values() for t in cat.values()]
market_data = get_batch_data(all_asset_tickers, timeframe)

# --- LAYOUT: Controls (Top), Chart (Left), Sourcing (Right) ---
col_main, col_source = st.columns([3, 1])

with col_main:
    # Asset Selection
    c1, c2 = st.columns(2)
    sel_cat = c1.selectbox("SECTOR", list(ASSETS.keys()))
    sel_asset = c2.selectbox("ASSET", list(ASSETS[sel_cat].keys()))
    sel_ticker = ASSETS[sel_cat][sel_asset]

    # Chart Logic
    df_chart = market_data[sel_ticker] if isinstance(market_data.columns, pd.MultiIndex) else market_data
    
    if not df_chart.empty and 'Close' in df_chart:
        fig = go.Figure()

        # 1. Main Price Trace
        if chart_style == "Candle":
            fig.add_trace(go.Candlestick(
                x=df_chart.index, open=df_chart['Open'], high=df_chart['High'],
                low=df_chart['Low'], close=df_chart['Close'], name=sel_asset,
                increasing_line_color='#00C853', decreasing_line_color='#FF3D00'
            ))
        else:
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['Close'], mode='lines', name=sel_asset,
                line=dict(color='#00E5FF', width=1.5)
            ))
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['Close'], fill='tozeroy', 
                fillcolor='rgba(0, 229, 255, 0.05)', line=dict(width=0), showlegend=False
            ))

        # 2. Moving Average
        if show_ma and len(df_chart) > ma_period:
            df_chart[f'SMA{ma_period}'] = df_chart['Close'].rolling(window=ma_period).mean()
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart[f'SMA{ma_period}'], 
                name=f"MA ({ma_period})", line=dict(color='#FFAB40', width=1)
            ))

        fig.update_layout(
            template="plotly_dark", height=500, margin=dict(l=0, r=10, t=30, b=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            hovermode="x unified",
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', side='right'),
            legend=dict(orientation="h", y=1.02, x=0, bgcolor='rgba(0,0,0,0)')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Current Price Display
        cur_price = df_chart['Close'].iloc[-1]
        st.markdown(f"<h2 style='text-align: right; color: #00E5FF;'>${cur_price:,.2f}</h2>", unsafe_allow_html=True)
    else:
        st.error("Data Unavailable")

with col_source:
    st.markdown("#### 📦 SOURCING INTEL")
    
    # Check if we have specific sourcing data, else generic
    source_list = SOURCING_DB.get(sel_asset)
    
    if source_list:
        st.markdown(f"<div style='font-size: 12px; color: #8b949e; margin-bottom: 10px;'>Top strategic hubs for {sel_asset}</div>", unsafe_allow_html=True)
        for item in source_list:
            st.markdown(f"""
            <div class="sourcing-card">
                <div class="sourcing-header">{item['Country']} <span class="sourcing-tag">{item['Tag']}</span></div>
                <div style="font-size: 12px; color: #c9d1d9;">{item['Note']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Fallback for assets without specific notes
        st.info(f"Sourcing intelligence not yet indexed for {sel_asset}.")
        st.markdown(f"""
        <div class="sourcing-card">
            <div class="sourcing-header">Global Spot Market</div>
            <div style="font-size: 12px; color: #c9d1d9;">Most liquid sourcing is via major exchanges (LME, COMEX, CBOT).</div>
        </div>
        """, unsafe_allow_html=True)

# --- MARKET SCANNER (Bottom) ---
st.markdown("---")
st.markdown("#### MARKET SCANNER")

overview_data = []
for category, items in ASSETS.items():
    for name, ticker in items.items():
        try:
            df = market_data[ticker] if isinstance(market_data.columns, pd.MultiIndex) else market_data
            df_clean = df['Close'].dropna()
            if len(df_clean) >= 2:
                overview_data.append({
                    "Sector": category, "Instrument": name, 
                    "Price": df_clean.iloc[-1], "Change %": ((df_clean.iloc[-1]-df_clean.iloc[-2])/df_clean.iloc[-2])*100
                })
        except: continue

if overview_data:
    st.dataframe(
        pd.DataFrame(overview_data).style.format({"Price": "{:,.2f}", "Change %": "{:+.2f}%"})
        .applymap(lambda v: f'color: {"#00C853" if v>0 else "#FF3D00"}', subset=['Change %']),
        use_container_width=True, hide_index=True
    )
