import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from curl_cffi import requests as curl_requests
import html as _html

_yf_session = curl_requests.Session(impersonate="chrome")

st.set_page_config(
    page_title="Stock Research",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

    /* ── Reset & Base ── */
    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
        background-color: #0e1117 !important;
        color: #e0e0e0 !important;
    }
    #MainMenu, footer { visibility: hidden; }
    header { visibility: hidden; }

    /* Force every Streamlit layer to the same background */
    [data-testid="stApp"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    .stApp, .main, .main > div {
        background-color: #0e1117 !important;
        background: #0e1117 !important;
    }

    /* ── Main container ── */
    .block-container {
        padding: 1.8rem 2.2rem 2rem;
        max-width: 1300px;
        background: #0e1117;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #0e1117 !important;
        border-right: 1px solid #1e1e1e !important;
    }
    [data-testid="stSidebar"] * { color: #c0c0c0 !important; }
    [data-testid="stSidebar"] .stTextInput input {
        background: #0e1117 !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 3px !important;
        color: #f0c040 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 13px !important;
    }
    [data-testid="stSidebar"] .stTextInput input:focus {
        border-color: #f0c040 !important;
        box-shadow: 0 0 0 1px #f0c04040 !important;
    }
    [data-testid="stSidebar"] .stSelectbox select,
    [data-testid="stSidebar"] [data-baseweb="select"] {
        background: #1e1e1e !important;
        border: 1px solid #2a2a2a !important;
        color: #c0c0c0 !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] * {
        background: #1e1e1e !important;
        color: #c0c0c0 !important;
    }
    /* Dropdown popover */
    [data-baseweb="popover"], [data-baseweb="popover"] * {
        background: #1e1e1e !important;
        color: #c0c0c0 !important;
    }
    [data-baseweb="menu"] { background: #1e1e1e !important; border: 1px solid #2a2a2a !important; }
    [data-baseweb="menu"] li { color: #c0c0c0 !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 12px !important; }
    [data-baseweb="menu"] li:hover { background: #2a2a2a !important; color: #f0c040 !important; }
    [data-baseweb="option"] { background: #1e1e1e !important; color: #c0c0c0 !important; }
    [aria-selected="true"][data-baseweb="option"] { background: #2a2a2a !important; color: #f0c040 !important; }

    /* ── Buttons ── */
    .stButton button {
        border-radius: 2px !important;
        border: 1px solid #2a2a2a !important;
        font-size: 11px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        padding: 5px 10px !important;
        background: #141414 !important;
        color: #888 !important;
        letter-spacing: 0.03em;
        transition: all 0.15s ease;
        text-transform: uppercase;
    }
    .stButton button:hover {
        background: #1e1e1e !important;
        border-color: #f0c040 !important;
        color: #f0c040 !important;
    }
    .stButton { width: 100%; }

    /* ── Metrics ── */
    [data-testid="metric-container"] {
        background: #111 !important;
        border: 1px solid #1e1e1e !important;
        border-radius: 2px !important;
        padding: 14px 16px !important;
        position: relative;
    }
    [data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 2px; height: 100%;
        background: #f0c040;
        opacity: 0.6;
    }
    [data-testid="metric-container"] label {
        font-size: 9px !important;
        color: #555 !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 20px !important;
        font-weight: 500 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        color: #f0f0f0 !important;
    }
    [data-testid="stMetricDelta"] {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0 !important;
        border-bottom: 1px solid #1e1e1e !important;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 11px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        padding: 10px 20px !important;
        background: transparent !important;
        border: none !important;
        color: #444 !important;
        outline: none !important;
    }
    .stTabs [data-baseweb="tab"]:hover { color: #888 !important; background: transparent !important; }
    .stTabs [aria-selected="true"] {
        color: #f0c040 !important;
        font-weight: 500 !important;
        border-bottom: 1px solid #f0c040 !important;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 1.4rem !important; }

    /* ── DataFrames ── */
    [data-testid="stDataFrame"] {
        border-radius: 2px !important;
        border: 1px solid #1e1e1e !important;
        overflow: hidden !important;
    }
    [data-testid="stDataFrame"] * {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 12px !important;
    }

    /* ── Sliders ── */
    [data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stThumbValue"] {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
        color: #e05555 !important;
        background: #111 !important;
    }
    [data-testid="stSlider"] [role="slider"] {
        background: #e05555 !important;
        border: 2px solid #e05555 !important;
    }
    [data-baseweb="slider"] [data-testid="stSlider"] div[style*="background"] {
        background: #f0c040 !important;
    }

    /* ── Radio ── */
    [data-testid="stRadio"] label {
        font-size: 11px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: #888 !important;
    }

    /* ── Info / warning ── */
    [data-testid="stInfo"] {
        background: #111 !important;
        border: 1px solid #1e3a1e !important;
        border-left: 3px solid #2d6a2d !important;
        border-radius: 2px !important;
        color: #888 !important;
        font-size: 12px !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }

    /* ── Caption / small text ── */
    .stCaption, [data-testid="stCaptionContainer"] {
        color: #444 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
    }

    /* ── Progress bar ── */
    [data-testid="stProgressBar"] > div > div {
        background: #f0c040 !important;
    }

    /* ── Divider ── */
    hr { border-color: #1e1e1e !important; }

    /* ── Custom labels ── */
    .section-label {
        font-size: 9px !important;
        font-weight: 600 !important;
        letter-spacing: 0.14em !important;
        text-transform: uppercase !important;
        color: #888 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        margin-bottom: 10px !important;
        border-bottom: 1px solid #0e1117;
        padding-bottom: 6px;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: #0a0a0a; }
    ::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 2px; }
    ::-webkit-scrollbar-thumb:hover { background: #f0c040; }

    /* ── Spinner ── */
    [data-testid="stSpinner"] { color: #f0c040 !important; }
</style>
""", unsafe_allow_html=True)

# JS: restore sidebar toggle hidden by header { visibility: hidden }
st.components.v1.html("""
<script>
function showSidebarToggle() {
    const selectors = [
        '[data-testid="collapsedControl"]',
        '[data-testid="stSidebarCollapsedControl"]',
        'header button',
        'header [role="button"]',
    ];
    let found = false;
    for (const sel of selectors) {
        const els = window.parent.document.querySelectorAll(sel);
        els.forEach(el => {
            el.style.visibility = 'visible';
            el.style.opacity = '1';
            el.style.pointerEvents = 'auto';
            el.style.zIndex = '999999';
            let p = el.parentElement;
            for (let i = 0; i < 5 && p; i++) {
                if (getComputedStyle(p).visibility === 'hidden') p.style.visibility = 'visible';
                p = p.parentElement;
            }
            found = true;
        });
    }
    return found;
}
let attempts = 0;
const interval = setInterval(() => {
    if (showSidebarToggle() || attempts++ > 40) clearInterval(interval);
}, 200);
</script>
""", height=0)


# ── Session state ─────────────────────────────────────────────────────────────
if "ticker" not in st.session_state:
    st.session_state.ticker = "AAPL"


# ── Helpers ───────────────────────────────────────────────────────────────────
def set_ticker(t):
    st.session_state.ticker = t.upper().strip()

def fmt_large(n):
    if n is None or (isinstance(n, float) and pd.isna(n)):
        return "—"
    if abs(n) >= 1e12: return f"${n/1e12:.2f}T"
    if abs(n) >= 1e9:  return f"${n/1e9:.1f}B"
    if abs(n) >= 1e6:  return f"${n/1e6:.1f}M"
    return f"${n:,.0f}"

def fmt_pct(n, mult=100):
    if n is None or (isinstance(n, float) and pd.isna(n)):
        return "—"
    return f"{n * mult:.1f}%"

def safe(info, key, fallback=None):
    v = info.get(key, fallback)
    return v if v not in (None, "N/A", "None", "") else fallback

def pe_label(pe):
    if not pe or pd.isna(pe): return ""
    if pe < 15:  return "LOW"
    if pe < 30:  return "FAIR"
    if pe < 60:  return "PREMIUM"
    return "ELEVATED"

def pe_color(pe):
    if not pe or pd.isna(pe): return "#555"
    if pe < 15:  return "#2d9e5f"
    if pe < 30:  return "#378ADD"
    if pe < 60:  return "#f0c040"
    return "#e05555"

# Plotly dark theme defaults
PLOT_BG   = "rgba(0,0,0,0)"
GRID_COL  = "#0e1117"
TEXT_COL  = "#555"
AMBER     = "#f0c040"
BLUE      = "#4a9edd"
GREEN     = "#2d9e5f"
RED       = "#e05555"
ORANGE    = "#e07a30"

def dark_layout(**kwargs):
    base = dict(
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        font=dict(family="IBM Plex Mono", color="#888", size=11),
        margin=dict(t=30, b=20, l=10, r=10),
        hovermode="x unified",
    )
    base.update(kwargs)
    return base

@st.cache_data(ttl=300, show_spinner=False)
def load_ticker(ticker):
    t = yf.Ticker(ticker, session=_yf_session)
    info       = t.info
    hist       = t.history(period="1y")
    financials = t.financials
    return info, hist, financials

@st.cache_data(ttl=300, show_spinner=False)
def load_hist(ticker, period):
    return yf.Ticker(ticker, session=_yf_session).history(period=period)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:8px 0 16px; border-bottom:1px solid #1e1e1e; margin-bottom:16px;">
        <div style="font-family:'IBM Plex Mono',monospace; font-size:10px; letter-spacing:0.2em;
                    text-transform:uppercase; color:#888; margin-bottom:4px;">Terminal</div>
        <div style="font-family:'IBM Plex Mono',monospace; font-size:18px; font-weight:600;
                    color:#f0c040; letter-spacing:0.05em;">STOCK//RES</div>
    </div>
    """, unsafe_allow_html=True)

    search = st.text_input(
        "TICKER",
        value=st.session_state.ticker,
        placeholder="AAPL · TSLA · BP.L",
        key="search_box",
        label_visibility="visible",
    )
    if st.button("▶  LOAD", use_container_width=True):
        set_ticker(search)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'IBM Plex Mono',monospace; font-size:9px;
                letter-spacing:0.14em; color:#888; text-transform:uppercase;
                border-bottom:1px solid #0e1117; padding-bottom:6px; margin-bottom:10px;">
                Quick access</div>""", unsafe_allow_html=True)

    quick_tickers = ["AAPL","MSFT","NVDA","META","AMZN","TSLA","GOOGL","JPM","AMD","NFLX","DIS","PYPL"]
    cols = st.columns(3)
    for i, q in enumerate(quick_tickers):
        if cols[i % 3].button(q, key=f"btn_{q}", use_container_width=True):
            set_ticker(q)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'IBM Plex Mono',monospace; font-size:9px; color:#444;
                text-align:center; letter-spacing:0.08em;">
                DATA · YAHOO FINANCE &nbsp;·&nbsp; REFRESH 5 MIN</div>""", unsafe_allow_html=True)

# ── Chart period (used in Price Chart tab) ────────────────────────────────────
period_map = {"1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y","2Y":"2y","5Y":"5y"}
ticker = st.session_state.ticker

with st.spinner(f"Fetching {ticker}…"):
    try:
        info, hist, financials = load_ticker(ticker)
    except Exception as e:
        st.error(f"Could not load **{ticker}**: {e}")
        st.stop()

price = safe(info, "currentPrice") or safe(info, "regularMarketPrice")
if not price:
    st.error(f"No data found for **{ticker}**. Check the ticker symbol.")
    st.stop()

name     = safe(info, "longName", ticker)
current  = safe(info, "currentPrice") or safe(info, "regularMarketPrice", 0) or 0
prev     = safe(info, "regularMarketPreviousClose") or safe(info, "previousClose", current) or current
chg_pct  = ((current - prev) / prev * 100) if prev else 0
sector   = safe(info, "sector", "—")
industry = safe(info, "industry", "—")
desc     = safe(info, "longBusinessSummary", "")

chg_sign  = "▲" if chg_pct >= 0 else "▼"
chg_color = GREEN if chg_pct >= 0 else RED


# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="border-bottom:1px solid #1e1e1e; padding-bottom:18px; margin-bottom:20px;">
  <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px;">
    <div>
      <div style="font-family:'IBM Plex Mono',monospace; font-size:9px; letter-spacing:0.16em;
                  text-transform:uppercase; color:#888; margin-bottom:6px;">
        {sector}&nbsp;&nbsp;/&nbsp;&nbsp;{industry}
      </div>
      <div style="font-family:'IBM Plex Sans',sans-serif; font-size:24px; font-weight:600;
                  color:#f0f0f0; margin-bottom:2px; letter-spacing:-0.01em;">
        {name}
        <span style="font-family:'IBM Plex Mono',monospace; font-size:13px; color:#888;
                     font-weight:400; margin-left:8px; letter-spacing:0.05em;">{ticker}</span>
      </div>
    </div>
    <div style="text-align:right;">
      <div style="font-family:'IBM Plex Mono',monospace; font-size:36px; font-weight:600;
                  color:#f0f0f0; letter-spacing:-0.02em; line-height:1;">${price:,.2f}</div>
      <div style="margin-top:4px; display:flex; align-items:center; gap:12px; justify-content:flex-end; flex-wrap:wrap;">
        <span style="font-family:'IBM Plex Mono',monospace; font-size:13px;
                     font-weight:500; color:{chg_color};">{chg_sign} {abs(chg_pct):.2f}%</span>
        <a href="https://finance.yahoo.com/quote/{ticker}/key-statistics/" target="_blank"
           style="font-family:'IBM Plex Mono',monospace; font-size:9px; color:#888;
                  text-decoration:none; border:1px solid #1e1e1e; border-radius:2px;
                  padding:3px 8px; letter-spacing:0.08em; text-transform:uppercase;
                  transition:all 0.15s; white-space:nowrap;">
          YAHOO ↗
        </a>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_ov, tab_fin, tab_chart, tab_compare, tab_proj = st.tabs(
    ["Overview", "Financials", "Price Chart", "Compare", "Projections"]
)


# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab_ov:
    mkt_cap  = safe(info, "marketCap")
    pe       = safe(info, "trailingPE")
    fwd_pe   = safe(info, "forwardPE")
    eps      = safe(info, "trailingEps")
    hi52     = safe(info, "fiftyTwoWeekHigh")
    lo52     = safe(info, "fiftyTwoWeekLow")
    div_yld  = safe(info, "dividendYield", 0) or 0
    beta     = safe(info, "beta")
    vol      = safe(info, "regularMarketVolume")
    avg_vol  = safe(info, "averageVolume")

    # 2-year forward P/E
    fwd_eps      = safe(info, "forwardEps")
    earn_growth  = safe(info, "earningsGrowth") or safe(info, "earningsQuarterlyGrowth")
    fwd2_pe      = None
    fwd2_pe_note = ""
    if fwd_eps and earn_growth and price:
        fwd2_eps = fwd_eps * (1 + earn_growth)
        if fwd2_eps > 0:
            fwd2_pe = price / fwd2_eps
            fwd2_pe_note = f"1yr fwd EPS ${fwd_eps:.2f} × (1 + {earn_growth*100:.1f}%)"
    elif fwd_pe and earn_growth and price:
        implied = price / fwd_pe
        if implied > 0:
            fwd2_eps = implied * (1 + earn_growth)
            if fwd2_eps > 0:
                fwd2_pe = price / fwd2_eps
                fwd2_pe_note = f"Derived from fwd P/E {fwd_pe:.1f}x × growth {earn_growth*100:.1f}%"

    # Tooltip CSS
    st.markdown("""
<style>
.tt-wrap{display:inline-flex;align-items:center;gap:5px;margin-top:-6px;margin-bottom:4px}
.tt-i{display:inline-flex;align-items:center;justify-content:center;
  width:13px;height:13px;border-radius:50%;background:#0e1117;border:1px solid #2a2a2a;
  color:#444;font-size:8px;font-weight:700;cursor:help;position:relative;flex-shrink:0;
  font-family:'IBM Plex Mono',monospace;}
.tt-i .tt-box{visibility:hidden;opacity:0;width:240px;
  background:#141414;border:1px solid #2a2a2a;color:#aaa;font-size:10px;line-height:1.6;
  border-radius:2px;padding:10px 12px;position:absolute;z-index:9999;
  left:18px;top:-4px;transition:opacity 0.12s ease;pointer-events:none;
  font-family:'IBM Plex Mono',monospace;}
.tt-i:hover .tt-box{visibility:visible;opacity:1}
.pe-badge{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:9px;
  letter-spacing:0.1em;padding:2px 6px;border-radius:2px;font-weight:600;}
</style>
""", unsafe_allow_html=True)

    # Row 1: valuation metrics
    c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
    c1.metric("Mkt Cap", fmt_large(mkt_cap))

    pe_display = f"{pe:.1f}x" if pe else "—"
    pe_badge   = pe_label(pe)
    p_color    = pe_color(pe)
    with c2:
        st.metric("P/E TTM", pe_display)
        if pe_badge:
            st.markdown(f"""
<div class="tt-wrap">
  <span class="pe-badge" style="color:{p_color};border:1px solid {p_color}40;background:{p_color}10;">{pe_badge}</span>
  <span class="tt-i">i<span class="tt-box">
    <b style="color:#f0c040">P/E Bands</b><br><br>
    &lt;15 — LOW: below market avg<br>
    15–30 — FAIR: typical S&amp;P range<br>
    30–60 — PREMIUM: growth priced in<br>
    &gt;60 — ELEVATED: rate sensitive<br><br>
    Price ÷ trailing 12-month EPS
  </span></span>
</div>""", unsafe_allow_html=True)

    with c3:
        st.metric("P/E 1Y Fwd", f"{fwd_pe:.1f}x" if fwd_pe else "—")
        st.markdown(f"""
<div class="tt-wrap">
  <span class="tt-i">i<span class="tt-box">
    <b style="color:#f0c040">1-Year Forward P/E</b><br><br>
    Price ÷ analyst consensus EPS for next 12 months.<br><br>
    Lower fwd P/E than TTM = earnings expected to grow.
  </span></span>
</div>""", unsafe_allow_html=True)

    fwd2_display = f"{fwd2_pe:.1f}x" if fwd2_pe else "—"
    with c4:
        st.metric("P/E 2Y Fwd", fwd2_display)
        note = fwd2_pe_note if fwd2_pe_note else "Insufficient data — needs fwd EPS + growth rate."
        st.markdown(f"""
<div class="tt-wrap">
  <span class="tt-i">i<span class="tt-box">
    <b style="color:#f0c040">2-Year Forward P/E</b><br><br>
    {note}<br><br>
    Falling TTM→1Y→2Y P/E = strong earnings growth expected.
  </span></span>
</div>""", unsafe_allow_html=True)

    c5.metric("EPS TTM",   f"${eps:.2f}" if eps else "—")
    c6.metric("Div Yield", f"{div_yld*100:.2f}%" if div_yld else "—")
    c7.metric("Beta",      f"{beta:.2f}" if beta else "—")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Row 2: volume + 52w
    cv1, cv2, cv3, cv4 = st.columns(4)
    cv1.metric("Volume",     fmt_large(vol).replace("$","") if vol else "—")
    cv2.metric("Avg Volume", fmt_large(avg_vol).replace("$","") if avg_vol else "—")
    cv3.metric("52W High",   f"${hi52:,.2f}" if hi52 else "—")
    cv4.metric("52W Low",    f"${lo52:,.2f}" if lo52 else "—")

    # 52-week range bar (custom HTML, cleaner than gauge)
    if hi52 and lo52 and hi52 > lo52:
        pct = (price - lo52) / (hi52 - lo52)
        pct_clamped = max(0, min(1, pct))
        bar_color = GREEN if pct_clamped > 0.66 else (AMBER if pct_clamped > 0.33 else RED)
        st.markdown(f"""
<div style="margin:20px 0 8px;">
  <div style="font-family:'IBM Plex Mono',monospace; font-size:9px; letter-spacing:0.14em;
              text-transform:uppercase; color:#888; margin-bottom:10px;">
    52-week range position — {pct_clamped*100:.1f}%
  </div>
  <div style="display:flex; align-items:center; gap:12px;">
    <span style="font-family:'IBM Plex Mono',monospace; font-size:10px; color:#444; min-width:48px;">${lo52:.0f}</span>
    <div style="flex:1; height:4px; background:#0e1117; border-radius:2px; position:relative;">
      <div style="position:absolute; left:0; top:0; height:100%; width:{pct_clamped*100:.1f}%;
                  background:{bar_color}; border-radius:2px; transition:width 0.3s;"></div>
      <div style="position:absolute; top:-4px; left:{pct_clamped*100:.1f}%;
                  transform:translateX(-50%); width:12px; height:12px; border-radius:50%;
                  background:{bar_color}; border:2px solid #0a0a0a;"></div>
    </div>
    <span style="font-family:'IBM Plex Mono',monospace; font-size:10px; color:#444; min-width:48px; text-align:right;">${hi52:.0f}</span>
  </div>
</div>
""", unsafe_allow_html=True)

    if desc:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown("""<div style="font-family:'IBM Plex Mono',monospace; font-size:9px;
                    letter-spacing:0.14em; color:#888; text-transform:uppercase;
                    border-bottom:1px solid #0e1117; padding-bottom:6px; margin-bottom:10px;">
                    About</div>""", unsafe_allow_html=True)
        st.markdown(f"""<div style="font-family:'IBM Plex Sans',sans-serif; font-size:13px;
                    color:#888; line-height:1.7; max-width:900px;">{_html.escape(desc)}</div>""",
                    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FINANCIALS
# ══════════════════════════════════════════════════════════════════════════════
with tab_fin:
    gm  = safe(info, "grossMargins")
    npm = safe(info, "profitMargins")
    opm = safe(info, "operatingMargins")
    roe = safe(info, "returnOnEquity")
    roa = safe(info, "returnOnAssets")
    de  = safe(info, "debtToEquity")
    ps  = safe(info, "priceToSalesTrailing12Months")
    pb  = safe(info, "priceToBook")
    rev = safe(info, "totalRevenue")
    fcf = safe(info, "freeCashflow")

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Gross Margin", fmt_pct(gm))
    c2.metric("Net Margin",   fmt_pct(npm))
    c3.metric("Op Margin",    fmt_pct(opm))
    c4.metric("ROE",          fmt_pct(roe))
    c5.metric("ROA",          fmt_pct(roa))
    c6.metric("Debt/Equity",  f"{de/100:.2f}" if de else "—")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Revenue TTM", fmt_large(rev))
    c2.metric("Free Cash Flow", fmt_large(fcf))
    c3.metric("P/S",         f"{ps:.1f}x" if ps else "—")
    c4.metric("P/B",         f"{pb:.1f}x" if pb else "—")

    # Margin bars
    if any([gm, npm, opm]):
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown("""<div style="font-family:'IBM Plex Mono',monospace; font-size:9px;
                    letter-spacing:0.14em; color:#888; text-transform:uppercase;
                    border-bottom:1px solid #0e1117; padding-bottom:6px; margin-bottom:14px;">
                    Margins vs S&P 500 average (~11% net)</div>""", unsafe_allow_html=True)
        labels = ["Gross Margin","Op Margin","Net Margin","S&P Avg Net"]
        values = [round((gm or 0)*100,1), round((opm or 0)*100,1), round((npm or 0)*100,1), 11.0]
        colors = [GREEN, BLUE, AMBER, "#888"]
        fig_m = go.Figure()
        for lbl, val, col in zip(labels, values, colors):
            fig_m.add_trace(go.Bar(y=[lbl], x=[val], orientation="h", marker_color=col,
                                   text=[f"{val:.1f}%"], textposition="outside",
                                   textfont=dict(family="IBM Plex Mono", size=11, color="#888"),
                                   name=lbl))
        fig_m.update_layout(**dark_layout(height=190, showlegend=False, barmode="group",
            margin=dict(t=10,b=10,l=10,r=70),
            xaxis=dict(ticksuffix="%", showgrid=True, gridcolor=GRID_COL, range=[0, max(values)*1.35],
                       tickfont=dict(family="IBM Plex Mono", color="#555", size=10)),
            yaxis=dict(tickfont=dict(family="IBM Plex Mono", color="#888", size=11))))
        st.plotly_chart(fig_m, use_container_width=True)

    # Income statement
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'IBM Plex Mono',monospace; font-size:9px;
                letter-spacing:0.14em; color:#888; text-transform:uppercase;
                border-bottom:1px solid #0e1117; padding-bottom:6px; margin-bottom:14px;">
                Annual income statement</div>""", unsafe_allow_html=True)
    want = ["Total Revenue", "Gross Profit", "Operating Income", "Net Income", "EBITDA"]

    try:
        t_obj         = yf.Ticker(ticker, session=_yf_session)
        annual_fin    = t_obj.financials
        quarterly_fin = t_obj.quarterly_financials

        if not annual_fin.empty:
            ann_rows = [r for r in want if r in annual_fin.index]
            annual_cols    = sorted(annual_fin.columns, reverse=True)
            quarterly_cols = sorted(quarterly_fin.columns, reverse=True) if not quarterly_fin.empty else []

            combined_cols = []
            latest_annual_date       = max(annual_cols)
            most_recent_annual_year  = pd.Timestamp(latest_annual_date).year

            recent_qtrs = sorted([q for q in quarterly_cols if pd.Timestamp(q).year > most_recent_annual_year], reverse=True)
            used_qtrs = set()
            for q in recent_qtrs:
                lbl = f"Q{((pd.Timestamp(q).month-1)//3)+1} {pd.Timestamp(q).year}*"
                combined_cols.append((lbl, "quarterly", q))
                used_qtrs.add(q)

            for ann_col in annual_cols:
                year = pd.Timestamp(ann_col).year
                combined_cols.append((str(year), "annual", ann_col))
                if year == most_recent_annual_year:
                    yr_qtrs = sorted([q for q in quarterly_cols if pd.Timestamp(q).year == year and q not in used_qtrs], reverse=True)
                    for q in yr_qtrs:
                        lbl = f"  Q{((pd.Timestamp(q).month-1)//3)+1} {year}"
                        combined_cols.append((lbl, "quarterly", q))
                        used_qtrs.add(q)

            display_rows = {m: [] for m in ann_rows}
            all_labels   = [lbl for lbl, _, _ in combined_cols]
            for lbl, source, col in combined_cols:
                src = annual_fin if source == "annual" else quarterly_fin
                for metric in ann_rows:
                    if metric in src.index and col in src.columns:
                        val = src.loc[metric, col]
                        display_rows[metric].append(fmt_large(val) if pd.notna(val) else "—")
                    else:
                        display_rows[metric].append("—")

            df_display = pd.DataFrame(display_rows, index=all_labels).T
            df_display.index.name = "Metric"
            st.dataframe(df_display, use_container_width=True)
            st.caption("* = quarter not yet in annual total")
        else:
            st.info("No financial data available.")
    except Exception as ex:
        st.warning(f"Could not load detailed financials: {ex}")
        if not financials.empty:
            df = financials.copy()
            df.columns = [str(c)[:4] for c in df.columns]
            df = df.loc[[r for r in want if r in df.index]]
            df = df.map(lambda x: fmt_large(x) if pd.notna(x) else "—")
            st.dataframe(df, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PRICE CHART
# ══════════════════════════════════════════════════════════════════════════════
with tab_chart:
    col_ct, col_per = st.columns([3, 1])
    with col_ct:
        chart_type = st.radio("", ["Line","Candlestick","Area"], horizontal=True, label_visibility="collapsed")
    with col_per:
        period_label = st.selectbox("Window", list(period_map.keys()), index=3, label_visibility="collapsed")
        chart_period = period_map[period_label]

    h = load_hist(ticker, chart_period)

    if h.empty:
        st.warning("No price history available.")
    else:

        fig = go.Figure()
        if chart_type == "Candlestick":
            fig.add_trace(go.Candlestick(
                x=h.index, open=h["Open"], high=h["High"], low=h["Low"], close=h["Close"],
                increasing_line_color=GREEN, decreasing_line_color=RED,
                increasing_fillcolor="rgba(45,158,95,0.27)", decreasing_fillcolor="rgba(224,85,85,0.27)", name=ticker))
        elif chart_type == "Area":
            fig.add_trace(go.Scatter(x=h.index, y=h["Close"], fill="tozeroy",
                fillcolor="rgba(240,192,64,0.09)", line=dict(color=AMBER, width=1.5), name=ticker))
        else:
            fig.add_trace(go.Scatter(x=h.index, y=h["Close"],
                line=dict(color=AMBER, width=1.5), name=ticker))

        fig.add_trace(go.Bar(x=h.index, y=h["Volume"],
            marker_color="rgba(240,192,64,0.13)", name="Volume", yaxis="y2"))

        fig.update_layout(**dark_layout(
            height=480,
            margin=dict(t=20,b=20,l=10,r=10),
            xaxis=dict(showgrid=False, rangeslider=dict(visible=False),
                       tickfont=dict(family="IBM Plex Mono", color="#555", size=10)),
            yaxis=dict(title="", showgrid=True, gridcolor=GRID_COL,
                       tickprefix="$", domain=[0.25,1],
                       tickfont=dict(family="IBM Plex Mono", color="#555", size=10)),
            yaxis2=dict(title="", showgrid=False, domain=[0,0.2]),
            legend=dict(orientation="h", y=1.04, font=dict(family="IBM Plex Mono", size=10)),
        ))
        st.plotly_chart(fig, use_container_width=True)

        ret     = ((h["Close"].iloc[-1] / h["Close"].iloc[0]) - 1) * 100
        vol_std = h["Close"].pct_change().std() * (252**0.5) * 100
        c1,c2,c3,c4 = st.columns(4)
        c1.metric(f"Return", f"{ret:+.1f}%")
        c2.metric("Ann. Volatility", f"{vol_std:.1f}%")
        c3.metric("Period High", f"${h['High'].max():,.2f}")
        c4.metric("Period Low",  f"${h['Low'].min():,.2f}")


# ══════════════════════════════════════════════════════════════════════════════
# COMPARE
# ══════════════════════════════════════════════════════════════════════════════
with tab_compare:
    st.markdown("""<div style="font-family:'IBM Plex Mono',monospace; font-size:9px;
                letter-spacing:0.14em; color:#888; text-transform:uppercase;
                border-bottom:1px solid #0e1117; padding-bottom:6px; margin-bottom:16px;">
                Enter up to 3 tickers to compare side by side</div>""", unsafe_allow_html=True)

    defaults = [ticker, "MSFT", "GOOGL"]
    c1,c2,c3 = st.columns(3)
    t1 = c1.text_input("Ticker 1", value=defaults[0], key="cmp1").upper().strip()
    t2 = c2.text_input("Ticker 2", value=defaults[1], key="cmp2").upper().strip()
    t3 = c3.text_input("Ticker 3", value=defaults[2], key="cmp3").upper().strip()

    if st.button("▶  RUN COMPARISON", use_container_width=True):
        compare_list = [t for t in [t1,t2,t3] if t]
        rows = []
        prog = st.progress(0, text="Fetching…")
        for i, tk in enumerate(compare_list):
            try:
                inf = yf.Ticker(tk, session=_yf_session).info
                rows.append({
                    "Ticker":       tk,
                    "Name":         safe(inf,"longName",tk)[:28],
                    "Price":        f"${safe(inf,'currentPrice',0) or 0:,.2f}",
                    "Mkt Cap":      fmt_large(safe(inf,"marketCap")),
                    "P/E TTM":      f"{safe(inf,'trailingPE',0):.1f}x" if safe(inf,"trailingPE") else "—",
                    "Fwd P/E":      f"{safe(inf,'forwardPE',0):.1f}x" if safe(inf,"forwardPE") else "—",
                    "Gross Margin": fmt_pct(safe(inf,"grossMargins")),
                    "Net Margin":   fmt_pct(safe(inf,"profitMargins")),
                    "ROE":          fmt_pct(safe(inf,"returnOnEquity")),
                    "Revenue TTM":  fmt_large(safe(inf,"totalRevenue")),
                    "Div Yield":    f"{(safe(inf,'dividendYield',0) or 0)*100:.2f}%",
                    "Beta":         f"{safe(inf,'beta',0) or 0:.2f}",
                })
            except Exception:
                rows.append({"Ticker":tk,"Name":"Error loading"})
            prog.progress((i+1)/len(compare_list), text=f"Loaded {tk}")
        prog.empty()

        df_cmp = pd.DataFrame(rows).set_index("Ticker")
        st.dataframe(df_cmp.T, use_container_width=True)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown("""<div style="font-family:'IBM Plex Mono',monospace; font-size:9px;
                    letter-spacing:0.14em; color:#888; text-transform:uppercase;
                    border-bottom:1px solid #0e1117; padding-bottom:6px; margin-bottom:14px;">
                    Price performance — normalised to 100</div>""", unsafe_allow_html=True)

        fig_c = go.Figure()
        c_palette = [AMBER, BLUE, GREEN]
        for tk, color in zip(compare_list, c_palette):
            try:
                hh = load_hist(tk, "1y")
                if not hh.empty:
                    norm = (hh["Close"] / hh["Close"].iloc[0] * 100).round(2)
                    fig_c.add_trace(go.Scatter(x=hh.index, y=norm, name=tk,
                        line=dict(color=color, width=1.5),
                        hovertemplate=f"<b>{tk}</b> %{{y:.1f}}<extra></extra>"))
            except Exception:
                pass
        fig_c.update_layout(**dark_layout(height=360,
            xaxis=dict(showgrid=False, tickfont=dict(family="IBM Plex Mono", color="#555", size=10)),
            yaxis=dict(showgrid=True, gridcolor=GRID_COL, tickfont=dict(family="IBM Plex Mono", color="#555", size=10)),
            legend=dict(orientation="h", y=1.06, font=dict(family="IBM Plex Mono", size=11)),
        ))
        st.plotly_chart(fig_c, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PROJECTIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab_proj:

    rev_ttm       = (safe(info,"totalRevenue",0) or 0) / 1e9
    shares_out    = (safe(info,"sharesOutstanding",1e9) or 1e9) / 1e9
    npm_curr      = (safe(info,"profitMargins",0.15) or 0.15) * 100
    pe_ttm        = safe(info,"trailingPE",25) or 25
    pe_fwd        = safe(info,"forwardPE",pe_ttm) or pe_ttm
    rev_growth_1y = (safe(info,"revenueGrowth",0.08) or 0.08) * 100

    pe_low_suggest  = max(5,  int(round(pe_ttm * 0.8)))
    pe_high_suggest = min(200, int(round(pe_ttm * 1.2)))

    npm_default    = int(min(max(round(npm_curr), 1), 60))
    rev_g_default  = int(min(max(round(rev_growth_1y), 0), 200))
    shares_default = round(float(min(max(shares_out, 0.1), 100)), 1)

    # Tooltip CSS (projections)
    st.markdown("""
<style>
.tip-wrap{display:inline-flex;align-items:center;gap:6px;margin-bottom:4px}
.tip-icon{display:inline-flex;align-items:center;justify-content:center;
  width:14px;height:14px;border-radius:50%;background:#0e1117;border:1px solid #2a2a2a;
  color:#444;font-size:8px;font-weight:700;cursor:help;position:relative;flex-shrink:0;
  font-family:'IBM Plex Mono',monospace;}
.tip-icon .tip-text{visibility:hidden;opacity:0;width:260px;
  background:#141414;border:1px solid #2a2a2a;color:#aaa;font-size:10px;line-height:1.6;
  border-radius:2px;padding:10px 12px;position:absolute;z-index:999;
  left:20px;top:-4px;transition:opacity 0.12s ease;pointer-events:none;
  font-family:'IBM Plex Mono',monospace;}
.tip-icon:hover .tip-text{visibility:visible;opacity:1}
.scenario-header{font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:0.12em;
  text-transform:uppercase;font-weight:600;padding:8px 12px;border-radius:2px;
  margin-bottom:12px;display:inline-block;}
</style>
""", unsafe_allow_html=True)

    def tip(label, tooltip_text):
        st.markdown(f"""
<div class="tip-wrap">
  <span style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#888;">{label}</span>
  <span class="tip-icon">i<span class="tip-text">{tooltip_text}</span></span>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div style="font-family:'IBM Plex Mono',monospace; font-size:11px; color:#555;
                margin-bottom:20px;">Build bear / base / bull scenarios · Anchors from live data</div>""",
                unsafe_allow_html=True)

    col_bear, col_base, col_bull = st.columns(3)

    with col_bear:
        st.markdown(f'<div class="scenario-header" style="color:{RED};border:1px solid {RED}33;background:{RED}08;">▼ BEAR</div>', unsafe_allow_html=True)
        tip("Revenue Growth (%)", "Bear: macro headwinds slow growth well below trend. ~0–2% is a useful floor.")
        bear_rev_g  = st.slider("bear_rev_g", 0, 200, max(0, rev_g_default - 8), 1, label_visibility="collapsed", key=f"{ticker}_b_rg")
        tip("Net Margin (%)", "Bear: margins compress — costs rise, pricing pressure, reinvestment drag.")
        bear_margin = st.slider("bear_margin", 1, 200, max(1, npm_default - 5), 1, label_visibility="collapsed", key=f"{ticker}_b_nm")
        tip("Exit P/E Range", f"Bear P/E range. Low = severe de-rating. TTM is {pe_ttm:.1f}x.")
        bear_pe_lo, bear_pe_hi = st.slider("bear_pe_range", 5, 200,
            (max(5, pe_low_suggest - 5), pe_low_suggest), 1, label_visibility="collapsed", key=f"{ticker}_b_pe")

    with col_base:
        st.markdown(f'<div class="scenario-header" style="color:{BLUE};border:1px solid {BLUE}33;background:{BLUE}08;">◆ BASE</div>', unsafe_allow_html=True)
        tip("Revenue Growth (%)", "Base: recent YoY growth or analyst consensus. Trailing growth shown in snapshot.")
        base_rev_g  = st.slider("base_rev_g", 0, 200, rev_g_default, 1, label_visibility="collapsed", key=f"{ticker}_ba_rg")
        tip("Net Margin (%)", f"Base: hold flat at TTM level ({npm_default}%). Only raise if there's a clear leverage path.")
        base_margin = st.slider("base_margin", 1, 200, npm_default, 1, label_visibility="collapsed", key=f"{ticker}_ba_nm")
        tip("Exit P/E Range", f"Base: anchor to TTM ({pe_ttm:.1f}x) or forward ({pe_fwd:.1f}x). Midpoint used as central estimate.")
        base_pe_lo, base_pe_hi = st.slider("base_pe_range", 5, 200,
            (max(5, int(round(pe_ttm)) - 3), min(200, int(round(pe_ttm)) + 3)), 1, label_visibility="collapsed", key=f"{ticker}_ba_pe")

    with col_bull:
        st.markdown(f'<div class="scenario-header" style="color:{GREEN};border:1px solid {GREEN}33;background:{GREEN}08;">▲ BULL</div>', unsafe_allow_html=True)
        tip("Revenue Growth (%)", "Bull: optimistic but plausible — new markets, product cycles, share gains.")
        bull_rev_g  = st.slider("bull_rev_g", 0, 200, min(200, rev_g_default + 8), 1, label_visibility="collapsed", key=f"{ticker}_bu_rg")
        tip("Net Margin (%)", "Bull: margins expand via operating leverage. Most mature companies top out at 25–40%.")
        bull_margin = st.slider("bull_margin", 1, 200, min(200, npm_default + 5), 1, label_visibility="collapsed", key=f"{ticker}_bu_nm")
        tip("Exit P/E Range", f"Bull: modest to strong re-rating. TTM {pe_ttm:.1f}x, fwd {pe_fwd:.1f}x.")
        bull_pe_lo, bull_pe_hi = st.slider("bull_pe_range", 5, 200,
            (pe_high_suggest, min(200, pe_high_suggest + 5)), 1, label_visibility="collapsed", key=f"{ticker}_bu_pe")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Shared sliders ────────────────────────────────────────────────────────
    sl1, sl2 = st.columns(2)
    with sl1:
        tip("Shares Outstanding (B)", "Diluted shares for EPS calculation. Buybacks reduce this (bullish); stock comp dilutes (bearish).")
        shares_b = st.slider("shares_b", 0.1, 100.0, shares_default, 0.1, label_visibility="collapsed", key=f"{ticker}_shares")
    with sl2:
        tip("Projection Horizon (years)", "3–5 years is the typical range. Beyond 7 years, assumptions dominate entirely.")
        horizon = st.slider("horizon", 1, 10, 5, 1, label_visibility="collapsed", key=f"{ticker}_hz")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'IBM Plex Mono',monospace; font-size:9px;
                letter-spacing:0.14em; color:#888; text-transform:uppercase;
                border-bottom:1px solid #0e1117; padding-bottom:6px; margin-bottom:14px;">
                Live snapshot</div>""", unsafe_allow_html=True)

    shares_display = f"{shares_default:.2f}B" if shares_default < 1 else f"{shares_default:.1f}B"
    sn1, sn2, sn3, sn4, sn5, sn6 = st.columns(6)
    sn1.metric("Revenue TTM",    f"${rev_ttm:.1f}B")
    sn2.metric("Revenue Growth", f"{rev_growth_1y:+.1f}%")
    sn3.metric("Net Margin",     f"{npm_default}%")
    sn4.metric("P/E TTM / Fwd",  f"{pe_ttm:.1f}x / {pe_fwd:.1f}x")
    sn5.metric("Price Today",    f"${price:,.2f}")
    sn6.metric("Shares Out.",    shares_display)

    # ── Compute paths ─────────────────────────────────────────────────────────
    years_range = list(range(0, horizon + 1))

    def price_path(rev_g, margin, pe):
        path = [price]
        for y in range(1, horizon + 1):
            fr  = rev_ttm * ((1 + rev_g/100) ** y)
            eps = (fr * (margin/100) * 1e9) / (shares_b * 1e9)
            path.append(round(eps * pe, 2))
        return path

    bear_pe_mid = (bear_pe_lo + bear_pe_hi) / 2
    base_pe_mid = (base_pe_lo + base_pe_hi) / 2
    bull_pe_mid = (bull_pe_lo + bull_pe_hi) / 2

    bear_path    = price_path(bear_rev_g, bear_margin, bear_pe_mid)
    bear_path_lo = price_path(bear_rev_g, bear_margin, bear_pe_lo)
    bear_path_hi = price_path(bear_rev_g, bear_margin, bear_pe_hi)
    base_path    = price_path(base_rev_g, base_margin, base_pe_mid)
    base_path_lo = price_path(base_rev_g, base_margin, base_pe_lo)
    base_path_hi = price_path(base_rev_g, base_margin, base_pe_hi)
    bull_path    = price_path(bull_rev_g, bull_margin, bull_pe_mid)
    bull_path_lo = price_path(bull_rev_g, bull_margin, bull_pe_lo)
    bull_path_hi = price_path(bull_rev_g, bull_margin, bull_pe_hi)

    # ── Target metrics ─────────────────────────────────────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown(f"""<div style="font-family:'IBM Plex Mono',monospace; font-size:9px;
                letter-spacing:0.14em; color:#888; text-transform:uppercase;
                border-bottom:1px solid #0e1117; padding-bottom:6px; margin-bottom:14px;">
                Year {horizon} price targets & CAGR</div>""", unsafe_allow_html=True)

    mc1, mc2, mc3 = st.columns(3)
    for col, label, path, path_lo, path_hi, col_color in [
        (mc1, "Bear", bear_path, bear_path_lo, bear_path_hi, RED),
        (mc2, "Base", base_path, base_path_lo, base_path_hi, BLUE),
        (mc3, "Bull", bull_path, bull_path_lo, bull_path_hi, GREEN),
    ]:
        tgt  = path[-1]
        cagr = ((tgt / price) ** (1/horizon) - 1) * 100 if price and horizon else 0
        col.metric(f"{label} — {horizon}yr", f"${tgt:,.0f}", f"{cagr:+.1f}% CAGR")
        col.markdown(f"""<div style="font-family:'IBM Plex Mono',monospace; font-size:10px;
                     color:#444; margin-top:-6px; padding-left:2px;">
                     P/E band: ${path_lo[-1]:,.0f} – ${path_hi[-1]:,.0f}</div>""",
                     unsafe_allow_html=True)

    # ── Chart ─────────────────────────────────────────────────────────────────
    fig_p = go.Figure()

    for path_lo, path_hi, fill_color in [
        (bear_path_lo, bear_path_hi, "rgba(224,85,85,0.09)"),
        (base_path_lo, base_path_hi, "rgba(74,158,221,0.09)"),
        (bull_path_lo, bull_path_hi, "rgba(45,158,95,0.09)"),
    ]:
        fig_p.add_trace(go.Scatter(
            x=years_range + years_range[::-1],
            y=path_hi + path_lo[::-1],
            fill="toself", fillcolor=fill_color,
            line=dict(color="rgba(0,0,0,0)"),
            hoverinfo="skip", showlegend=False,
        ))

    for path, color, dash, name in [
        (bear_path, RED,   "dot",   "Bear"),
        (base_path, BLUE,  "solid", "Base"),
        (bull_path, GREEN, "dash",  "Bull"),
    ]:
        fig_p.add_trace(go.Scatter(
            x=years_range, y=path, mode="lines+markers", name=name,
            line=dict(color=color, width=2, dash=dash),
            marker=dict(size=5, color=color),
            hovertemplate=f"<b>{name}</b> %{{y:$,.0f}}<extra></extra>",
        ))

    fig_p.add_hline(y=price, line_dash="dot", line_color="#888",
                    annotation_text=f"Today  ${price:.0f}",
                    annotation_font=dict(family="IBM Plex Mono", size=10, color="#555"),
                    annotation_position="right")

    fig_p.update_layout(**dark_layout(
        height=360, margin=dict(t=30,b=20,l=10,r=90),
        xaxis=dict(title="", showgrid=False, tickvals=years_range,
                   ticktext=[str(y) for y in years_range],
                   tickfont=dict(family="IBM Plex Mono", color="#555", size=10)),
        yaxis=dict(title="", showgrid=True, gridcolor=GRID_COL, tickprefix="$",
                   tickfont=dict(family="IBM Plex Mono", color="#555", size=10)),
        legend=dict(orientation="h", y=1.08, font=dict(family="IBM Plex Mono", size=10)),
    ))
    st.plotly_chart(fig_p, use_container_width=True)

    # ── Table ─────────────────────────────────────────────────────────────────
    st.markdown("""<div style="font-family:'IBM Plex Mono',monospace; font-size:9px;
                letter-spacing:0.14em; color:#888; text-transform:uppercase;
                border-bottom:1px solid #0e1117; padding-bottom:6px; margin-bottom:14px;">
                Year-by-year targets (mid P/E)</div>""", unsafe_allow_html=True)

    current_year = pd.Timestamp.now().year
    table_rows = []
    for y in range(0, horizon + 1):
        def cagr_str(p, yr):
            if yr == 0 or not price: return "—"
            return f"{((p/price)**(1/yr)-1)*100:+.1f}%"
        def range_str(lo, hi, yr):
            if yr == 0: return "—"
            return f"${lo[yr]:,.0f}–${hi[yr]:,.0f}"
        table_rows.append({
            "Year":           "Today" if y == 0 else str(current_year + y),
            "Bear":           f"${bear_path[y]:,.0f}",
            "Bear P/E Band":  range_str(bear_path_lo, bear_path_hi, y),
            "Bear CAGR":      cagr_str(bear_path[y], y),
            "Base":           f"${base_path[y]:,.0f}",
            "Base P/E Band":  range_str(base_path_lo, base_path_hi, y),
            "Base CAGR":      cagr_str(base_path[y], y),
            "Bull":           f"${bull_path[y]:,.0f}",
            "Bull P/E Band":  range_str(bull_path_lo, bull_path_hi, y),
            "Bull CAGR":      cagr_str(bull_path[y], y),
        })

    df_proj = pd.DataFrame(table_rows).set_index("Year")
    st.dataframe(df_proj, use_container_width=True)

    st.markdown(f"""
<div style="font-family:'IBM Plex Mono',monospace; font-size:10px; color:#444; line-height:1.8;
     border:1px solid #0e1117; padding:12px 16px; border-radius:2px; margin-top:12px;
     border-left:2px solid #2d6a2d;">
P/E anchors for {ticker} &nbsp;·&nbsp; TTM {pe_ttm:.1f}x &nbsp;·&nbsp; Fwd {pe_fwd:.1f}x &nbsp;·&nbsp;
Suggested {pe_low_suggest}–{pe_high_suggest}x (±20% of TTM) &nbsp;·&nbsp;
Shaded bands = P/E spread per scenario &nbsp;·&nbsp; Central line = midpoint P/E
</div>""", unsafe_allow_html=True)

    st.markdown("""<div style="font-family:'IBM Plex Mono',monospace; font-size:10px; color:#888;
                margin-top:10px;">⚠ Projections are illustrative only. Not financial advice.</div>""",
                unsafe_allow_html=True)
