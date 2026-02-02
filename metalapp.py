import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Global Trade Terminal", layout="wide")

# --- PROFESSIONAL STYLING ---
st.markdown("""
    <style>
    /* Main Background & Font */
    .stApp {
        background-color: #0b0e11;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Metrics Styling */
    div[data-testid="stMetricValue"] {
        font-family: 'Roboto Mono', monospace;
        font-size: 20px;
        font-weight: 500;
        color: #E6EDF3;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 12px;
        color: #8B949E;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #12151a;
        border-right: 1px solid #25282e;
    }
    
    /* Hide Streamlit default menu & footer ONLY (Keep header visible for the arrow) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* We REMOVED 'header {visibility: hidden;}' so you can see the sidebar arrow again */
    </style>
    """, unsafe_allow_html=True)

# --- ASSET CONFIGURATION ---
ASSETS = {
    "Industrial Metals": {
        "Copper": "HG=F",
        "Aluminum": "ALI=F",
        "Zinc": "ZNC=F",
        "Nickel (Proxy)": "VALE",
        "Lithium (ETF)": "LIT",
        "Steel (ETF)": "SLX"
    },
    "Precious Metals": {
        "Gold": "GC=F",
        "Silver": "SI=F",
        "Platinum": "PL=F",
        "Palladium": "PA=F"
    },
    "Agriculture": {
        "Wheat": "ZW=F",
        "Corn": "ZC=F",
        "Soybean": "ZS=F",
        "Sugar": "SB=F",
        "Coffee": "KC=F",
        "Cocoa": "CC=F",
        "Cotton": "CT=F"
    },
    "Forex": {
        "USD/EUR": "EUR=X",
        "USD/JPY": "JPY=X",
        "USD/INR": "INR=X",
        "USD/CNY": "CNY=X",
        "USD/THB": "THB=X"
    }
}

MACRO_VITALS = {
    "Brent Crude": "BZ=F",
    "Natural Gas": "NG=F",
    "Dollar Index": "DX=F",
    "Volatility": "^VIX"
}

# --- DATA ENGINE ---
@st.cache_data(ttl=300)
def get_batch_data(tickers, period):
    if not tickers:
        return pd.DataFrame()
    return yf.download(tickers, period=period, group_by='ticker', progress=False, threads=True)

# --- SIDEBAR ---
st.sidebar.markdown("## ⚙️ SETTINGS")
timeframe = st.sidebar.selectbox("RANGE", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "ytd"], index=3)

st.sidebar.markdown("---")
st.sidebar.markdown("## 🌐 MACRO")

# Fetch Sidebar Data
vitals_data = get_batch_data(list(MACRO_VITALS.values()), timeframe)

def display_sidebar_metric(label, ticker):
    try:
        if isinstance(vitals_data.columns, pd.MultiIndex):
            df = vitals_data[ticker]
        else:
            df = vitals_data
        
        if df.empty or 'Close' not in df:
            return

        current = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        delta = ((current - prev) / prev) * 100
        
        # Color logic: Green for up, Red for down
        st.sidebar.metric(label, f"{current:,.2f}", f"{delta:+.2f}%")
    except:
        pass

for name, tick in MACRO_VITALS.items():
    display_sidebar_metric(name, tick)

# --- MAIN DASHBOARD ---
st.markdown("<h3 style='text-align: left; color: white;'>GLOBAL TRADE TERMINAL</h3>", unsafe_allow_html=True)


# 1. MARKET DATA PREP
all_asset_tickers = [t for cat in ASSETS.values() for t in cat.values()]
market_data = get_batch_data(all_asset_tickers, timeframe)

overview_data = []
for category, items in ASSETS.items():
    for name, ticker in items.items():
        try:
            if isinstance(market_data.columns, pd.MultiIndex):
                df = market_data[ticker]
            else:
                df = market_data
            
            # --- THE FIX: Clean the data first ---
            # 1. Drop any rows where the 'Close' price is missing (NaN)
            df_clean = df['Close'].dropna()
            
            # 2. Make sure we have at least 2 days of data to compare
            if len(df_clean) >= 2:
                cur = df_clean.iloc[-1]
                prev = df_clean.iloc[-2]
                chg = ((cur - prev) / prev) * 100
                
                overview_data.append({
                    "Sector": category,
                    "Instrument": name,
                    "Price": cur,
                    "Change %": chg
                })
        except Exception as e:
            continue

df_overview = pd.DataFrame(overview_data)

# 2. CHARTING SECTION
col_controls, col_chart = st.columns([1, 4])

with col_controls:
    st.markdown("#### ANALYZE")
    sel_cat = st.selectbox("SECTOR", list(ASSETS.keys()))
    sel_asset = st.selectbox("ASSET", list(ASSETS[sel_cat].keys()))
    sel_ticker = ASSETS[sel_cat][sel_asset]

    # Quick Stats in the control panel
    if not df_overview.empty:
        row = df_overview[df_overview['Instrument'] == sel_asset]
        if not row.empty:
            st.markdown("---")
            st.metric("Current Price", f"{row['Price'].values[0]:,.2f}", f"{row['Change %'].values[0]:.2f}%")

with col_chart:
    # Get Data
    if isinstance(market_data.columns, pd.MultiIndex):
        df_chart = market_data[sel_ticker]
    else:
        df_chart = market_data

    if not df_chart.empty and 'Close' in df_chart:
        fig = go.Figure()

        # LOGIC: Candle for short term, Line for long term
        if timeframe in ['1mo', '3mo']:
            # Sleek Candlestick
            fig.add_trace(go.Candlestick(
                x=df_chart.index,
                open=df_chart['Open'], high=df_chart['High'],
                low=df_chart['Low'], close=df_chart['Close'],
                name=sel_asset,
                increasing_line_color='#00C853', increasing_fillcolor='#00C853', # Material Green
                decreasing_line_color='#FF3D00', decreasing_fillcolor='#FF3D00'  # Material Red
            ))
        else:
            # Razor Sharp Line
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['Close'], 
                mode='lines', name=sel_asset,
                line=dict(color='#00E5FF', width=1.5) # Cyan, thin line
            ))
            # VERY subtle glow/fill (opacity 0.05 is the key to avoiding "chunkiness")
            fig.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart['Close'],
                fill='tozeroy', fillcolor='rgba(0, 229, 255, 0.05)',
                line=dict(width=0), showlegend=False, hoverinfo='skip'
            ))

        # Add Moving Average (Thin orange line)
        if len(df_chart) > 50:
            df_chart['SMA50'] = df_chart['Close'].rolling(window=50).mean()
            fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['SMA50'], name="Trend (50d)", 
                                     line=dict(color='#FFAB40', width=1, dash='dash')))

        # PROFESSIONAL LAYOUT TWEAKS
        fig.update_layout(
            template="plotly_dark",
            height=500, # Controlled height
            margin=dict(l=0, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)', # Transparent background
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode="x unified",
            xaxis=dict(
                showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.05)', # Faint grid
                showline=False,
                zeroline=False
            ),
            yaxis=dict(
                showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.05)', # Faint grid
                showline=False,
                zeroline=False,
                side='right' # Price scale on right (Bloomberg style)
            ),
            legend=dict(orientation="h", y=1.02, x=0, bgcolor='rgba(0,0,0,0)')
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Loading chart data...")

# 3. COMPACT DATA GRID
st.markdown("---")
st.markdown("#### MARKET SCANNER")

if not df_overview.empty:
    # Styling the dataframe to be dark and sleek
    def highlight_change(val):
        color = '#00C853' if val > 0 else '#FF3D00'
        return f'color: {color}'

    st.dataframe(
        df_overview.style.format({
            "Price": "{:,.2f}", 
            "Change %": "{:+.2f}%"
        }).applymap(highlight_change, subset=['Change %']),
        use_container_width=True,
        hide_index=True
    )
