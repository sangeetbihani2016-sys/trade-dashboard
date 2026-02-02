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
    "Industrial Metals": { "Copper": "HG=F", "Aluminum": "ALI=F", "Zinc": "ZNC=F", "Nickel": "VALE", "Lithium": "LIT", "Steel": "SLX" },
    "Precious Metals": { "Gold": "GC=F", "Silver": "SI=F", "Platinum": "PL=F", "Palladium": "PA=F" },
    "Agriculture": { "Wheat": "ZW=F", "Corn": "ZC=F", "Soybean": "ZS=F", "Sugar": "SB=F", "Coffee": "KC=F", "Cocoa": "CC=F", "Cotton": "CT=F" },
    "Forex": { "USD/EUR": "EUR=X", "USD/JPY": "JPY=X", "USD/INR": "INR=X", "USD/CNY": "CNY=X" }
}

# FULL Sourcing Intelligence Database
SOURCING_DB = {
    # --- METALS ---
    "Copper": [
        {"Country": "Chile", "Tag": "Volume Leader", "Note": "World's largest reserves."},
        {"Country": "Peru", "Tag": "Low Cost", "Note": "Growing output, competitive labor."},
        {"Country": "China", "Tag": "Refining", "Note": "Top importer & refiner."},
        {"Country": "USA", "Tag": "Domestic", "Note": "Stable supply, premium pricing."}
    ],
    "Aluminum": [
        {"Country": "China", "Tag": "Dominant", "Note": "Produces ~58% of global supply."},
        {"Country": "India", "Tag": "Emerging", "Note": "High-quality primary aluminum exports."},
        {"Country": "Russia", "Tag": "Volume", "Note": "RUSAL is a major non-China producer."},
        {"Country": "Canada", "Tag": "Green", "Note": "Hydro-powered smelting (Quebec)."}
    ],
    "Zinc": [
        {"Country": "China", "Tag": "Top Producer", "Note": "35% of global mine production."},
        {"Country": "Australia", "Tag": "Reserves", "Note": "Largest global reserves."},
        {"Country": "Peru", "Tag": "Latin Hub", "Note": "Major open-pit mines (Antamina)."},
        {"Country": "India", "Tag": "Smelting", "Note": "Rampura Agucha is a key mine."}
    ],
    "Nickel": [
        {"Country": "Indonesia", "Tag": "King", "Note": "Controls market via export bans/smelting."},
        {"Country": "Philippines", "Tag": "Ore", "Note": "Major supplier to Chinese smelters."},
        {"Country": "Russia", "Tag": "High Grade", "Note": "Norilsk Nickel produces Class 1 nickel."},
        {"Country": "Canada", "Tag": "North Am", "Note": "Sudbury basin production."}
    ],
    "Steel": [
        {"Country": "China", "Tag": "Massive", "Note": "Exports >85M tons annually."},
        {"Country": "India", "Tag": "Growth", "Note": "Low-cost, expanding capacity."},
        {"Country": "Japan", "Tag": "High Tech", "Note": "Specialized automotive/industrial steel."},
        {"Country": "Turkey", "Tag": "Rebar", "Note": "Key supplier to EU/MENA construction."}
    ],
    "Lithium": [
        {"Country": "Australia", "Tag": "Hard Rock", "Note": "Spodumene ore, shipped to China."},
        {"Country": "Chile", "Tag": "Brine", "Note": "Lowest cost production (Atacama)."},
        {"Country": "China", "Tag": "Processing", "Note": "Controls 60%+ of refining capacity."},
        {"Country": "Argentina", "Tag": "New Projects", "Note": "Fastest growing brine projects."}
    ],
    "Gold": [
        {"Country": "China", "Tag": "Top Producer", "Note": "Largest output, mostly domestic use."},
        {"Country": "Australia", "Tag": "Reliable", "Note": "Massive open-pit mines."},
        {"Country": "Russia", "Tag": "Sanctioned", "Note": "Huge reserves, complex logistics."},
        {"Country": "Canada", "Tag": "ESG Safe", "Note": "Conflict-free sourcing."}
    ],
    "Silver": [
        {"Country": "Mexico", "Tag": "#1 Producer", "Note": "Fresnillo is the world's primary hub."},
        {"Country": "Peru", "Tag": "Volume", "Note": "Major copper/silver byproduct mines."},
        {"Country": "China", "Tag": "Refining", "Note": "Major industrial consumer & refiner."},
        {"Country": "Poland", "Tag": "Europe", "Note": "KGHM is a key EU supplier."}
    ],
    "Platinum": [
        {"Country": "South Africa", "Tag": "Dominant", "Note": "Produces ~70% of world supply."},
        {"Country": "Russia", "Tag": "#2 Producer", "Note": "Norilsk Nickel byproduct."},
        {"Country": "Zimbabwe", "Tag": "Reserves", "Note": "Great Dyke geological complex."},
        {"Country": "USA", "Tag": "recycling", "Note": "Stillwater mine & catalytic recycling."}
    ],
    "Palladium": [
        {"Country": "Russia", "Tag": "#1 Producer", "Note": "Controls ~40% of supply (Norilsk)."},
        {"Country": "South Africa", "Tag": "Major", "Note": "Deep level mines, labor volatility risk."},
        {"Country": "Canada", "Tag": "Stable", "Note": "Byproduct of nickel mining."},
        {"Country": "USA", "Tag": "Domestic", "Note": "Stillwater mine in Montana."}
    ],
    # --- AGRICULTURE ---
    "Corn": [
        {"Country": "USA", "Tag": "Top Exporter", "Note": "Global price setter (Chicago Board)."},
        {"Country": "Brazil", "Tag": "Safrinha", "Note": "Massive second-crop harvest."},
        {"Country": "Argentina", "Tag": "Value", "Note": "Competitive, but export tax risks."},
        {"Country": "Ukraine", "Tag": "Black Sea", "Note": "Logistics key for EU/China supply."}
    ],
    "Soybean": [
        {"Country": "Brazil", "Tag": "#1 Global", "Note": "Dominates export market (>50% share)."},
        {"Country": "USA", "Tag": "Reliable", "Note": "Key supplier during Brazil's off-season."},
        {"Country": "Argentina", "Tag": "Meal/Oil", "Note": "Top exporter of processed soy meal."},
        {"Country": "Paraguay", "Tag": "Regional", "Note": "Key river-based logistics."}
    ],
    "Sugar": [
        {"Country": "Brazil", "Tag": "Ethanol Flex", "Note": "Can switch cane to Sugar or Ethanol."},
        {"Country": "India", "Tag": "Swing", "Note": "Exports depend on domestic monsoon."},
        {"Country": "Thailand", "Tag": "Asia Hub", "Note": "Key supplier to Indonesia/China."},
        {"Country": "France", "Tag": "Beet Sugar", "Note": "Top EU white sugar exporter."}
    ],
    "Coffee": [
        {"Country": "Brazil", "Tag": "Arabica", "Note": "The 'Saudi Arabia' of coffee."},
        {"Country": "Vietnam", "Tag": "Robusta", "Note": "Dominates instant coffee market."},
        {"Country": "Colombia", "Tag": "Washed", "Note": "High quality mild Arabica."},
        {"Country": "Indonesia", "Tag": "Variety", "Note": "Sumatra/Java profiles."}
    ],
    "Cocoa": [
        {"Country": "Ivory Coast", "Tag": "The Giant", "Note": "Produces ~40% of world cocoa."},
        {"Country": "Ghana", "Tag": "Quality", "Note": "Govt controlled board (Cocobod)."},
        {"Country": "Ecuador", "Tag": "Fine Flavor", "Note": "Leader in Arriba/Nacional beans."},
        {"Country": "Indonesia", "Tag": "Processing", "Note": "Grinding hub for Asia."}
    ],
    "Cotton": [
        {"Country": "USA", "Tag": "Quality", "Note": "Standard for machine spinning."},
        {"Country": "India", "Tag": "Volume", "Note": "Massive acreage, variable yields."},
        {"Country": "Brazil", "Tag": "Mechanized", "Note": "High quality rain-fed cotton."},
        {"Country": "China", "Tag": "Consumer", "Note": "Huge production, but huge consumption."}
    ],
    # --- FOREX ---
    "Forex": [
        {"Country": "London", "Tag": "Hub", "Note": "43% of daily global Forex turnover."},
        {"Country": "New York", "Tag": "USD Home", "Note": "Primary liquidity for USD pairs."},
        {"Country": "Singapore", "Tag": "Asia", "Note": "Key hub for Asian session trading."},
        {"Country": "Tokyo", "Tag": "JPY", "Note": "Major flows during Asian morning."}
    ]
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
st.sidebar.markdown("## 📊 CHART TYPE")
chart_style = st.sidebar.radio("STYLE", ["Line", "Candle"], index=0, horizontal=True)

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

# --- LAYOUT ---
col_main, col_source = st.columns([3, 1])

with col_main:
    # Asset Selection
    c1, c2 = st.columns(2)
    sel_cat = c1.selectbox("SECTOR", list(ASSETS.keys()))
    sel_asset = c2.selectbox("ASSET", list(ASSETS[sel_cat].keys()))
    sel_ticker = ASSETS[sel_cat][sel_asset]

    # Chart Logic
    df_chart = market_data[sel_ticker] if isinstance(market_data.columns, pd.MultiIndex) else market_data
    
    # 1. CLEAN THE DATA (Fixes 'Wonky' Charts)
    if not df_chart.empty and 'Close' in df_chart:
        df_clean = df_chart.dropna(subset=['Close']) # Drop empty days (holidays/weekends)
        
        fig = go.Figure()

        if chart_style == "Candle":
            fig.add_trace(go.Candlestick(
                x=df_clean.index, open=df_clean['Open'], high=df_clean['High'],
                low=df_clean['Low'], close=df_clean['Close'], name=sel_asset,
                increasing_line_color='#00C853', decreasing_line_color='#FF3D00'
            ))
        else:
            fig.add_trace(go.Scatter(
                x=df_clean.index, y=df_clean['Close'], mode='lines', name=sel_asset,
                line=dict(color='#00E5FF', width=1.5)
            ))
            fig.add_trace(go.Scatter(
                x=df_clean.index, y=df_clean['Close'], fill='tozeroy', 
                fillcolor='rgba(0, 229, 255, 0.05)', line=dict(width=0), showlegend=False
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
        
        # Current Price
        cur_price = df_clean['Close'].iloc[-1]
        st.markdown(f"<h2 style='text-align: right; color: #00E5FF;'>${cur_price:,.2f}</h2>", unsafe_allow_html=True)
    else:
        st.error("Data Unavailable")

with col_source:
    st.markdown("#### 📦 SOURCING INTEL")
    
    # Intelligent Database Lookup
    source_list = SOURCING_DB.get(sel_asset)
    
    # Fallback for Forex or missing items
    if not source_list and sel_cat == "Forex":
        source_list = SOURCING_DB["Forex"]
    
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
        st.info("Sourcing data updating...")

# --- MARKET SCANNER ---
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
