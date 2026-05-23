import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Research",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 1.5rem 2rem 2rem; max-width: 1200px; }
    [data-testid="metric-container"] {
        background: #f8f9fa; border: 1px solid #e9ecef;
        border-radius: 10px; padding: 14px 16px;
    }
    [data-testid="metric-container"] label { font-size: 11px !important; color: #6c757d !important; letter-spacing: 0.05em; text-transform: uppercase; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 22px !important; font-weight: 500 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 0; border-bottom: 1px solid #dee2e6; }
    .stTabs [data-baseweb="tab"] { font-size: 13px; padding: 10px 18px; background: transparent; border: none; color: #6c757d; }
    .stTabs [aria-selected="true"] { color: #212529 !important; font-weight: 500; border-bottom: 2px solid #212529 !important; }
    .stButton button { border-radius: 8px; border: 1px solid #dee2e6; font-size: 13px; padding: 6px 14px; background: white; color: #495057; }
    .stButton button:hover { background: #f8f9fa; border-color: #adb5bd; }
    [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; border: 1px solid #e9ecef; }
    .section-label { font-size: 10px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #adb5bd; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)


# ── Session state: holds the active ticker ────────────────────────────────────
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
    if pe < 15:  return "🟢 Low PE"
    if pe < 30:  return "🔵 Fair"
    if pe < 60:  return "🟡 Premium"
    return "🔴 High PE"

@st.cache_data(ttl=300, show_spinner=False)
def load_ticker(ticker):
    t = yf.Ticker(ticker)
    info       = t.info
    hist       = t.history(period="1y")
    financials = t.financials
    return info, hist, financials

@st.cache_data(ttl=300, show_spinner=False)
def load_hist(ticker, period):
    return yf.Ticker(ticker).history(period=period)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📈 Stock Research")
    st.markdown("---")

    # Main search box — pressing Enter or clicking Search updates the ticker
    search = st.text_input(
        "Search any ticker",
        value=st.session_state.ticker,
        placeholder="e.g. AAPL, TSLA, BP.L",
        key="search_box",
    )
    if st.button("🔍  Search", use_container_width=True):
        set_ticker(search)

    st.markdown("---")
    st.markdown("**Quick picks**")

    quick_tickers = ["AAPL","MSFT","NVDA","META","AMZN","TSLA","GOOGL","JPM","AMD","NFLX","DIS","PYPL"]
    cols = st.columns(3)
    for i, q in enumerate(quick_tickers):
        if cols[i % 3].button(q, key=f"btn_{q}", use_container_width=True):
            set_ticker(q)

    st.markdown("---")
    period_map   = {"1 month":"1mo","3 months":"3mo","6 months":"6mo","1 year":"1y","2 years":"2y","5 years":"5y"}
    period_label = st.selectbox("Chart period", list(period_map.keys()), index=3)
    chart_period = period_map[period_label]


# ── Load data for active ticker ───────────────────────────────────────────────
ticker = st.session_state.ticker

with st.spinner(f"Loading {ticker}…"):
    try:
        info, hist, financials = load_ticker(ticker)
    except Exception as e:
        st.error(f"Could not load **{ticker}**: {e}")
        st.stop()

price = safe(info, "currentPrice") or safe(info, "regularMarketPrice")
if not price:
    st.error(f"No data found for **{ticker}**. Check the ticker and try again.")
    st.stop()

name     = safe(info, "longName", ticker)
current  = safe(info, "currentPrice") or safe(info, "regularMarketPrice", 0) or 0
prev     = safe(info, "regularMarketPreviousClose") or safe(info, "previousClose", current) or current
chg_pct  = ((current - prev) / prev * 100) if prev else 0
sector   = safe(info, "sector", "—")
industry = safe(info, "industry", "—")
desc     = safe(info, "longBusinessSummary", "")

chg_arrow = "▲" if chg_pct >= 0 else "▼"
chg_color = "green" if chg_pct >= 0 else "red"

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-bottom:1.4rem">
  <div style="font-size:13px;color:#6c757d;margin-bottom:2px">{sector} · {industry}</div>
  <div style="font-size:21px;font-weight:500;margin-bottom:6px">
    {name} <span style="font-size:14px;color:#adb5bd;font-weight:400">({ticker})</span>
  </div>
  <div style="display:flex;align-items:baseline;gap:14px;flex-wrap:wrap">
    <span style="font-size:36px;font-weight:500;color:#212529">${price:,.2f}</span>
    <span style="font-size:15px;font-weight:500;color:{chg_color}">{chg_arrow} {abs(chg_pct):.2f}% today</span>
    <a href="https://finance.yahoo.com/quote/{ticker}/key-statistics/" target="_blank"
       style="font-size:12px;color:#6c757d;text-decoration:none;border:1px solid #dee2e6;
              border-radius:6px;padding:3px 9px;margin-left:4px;white-space:nowrap;
              font-weight:400;vertical-align:middle;line-height:1">
      📊 Yahoo Statistics ↗
    </a>
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

    # 2-year forward P/E: price / (fwd_eps * (1 + earnings_growth))
    fwd_eps       = safe(info, "forwardEps")
    earn_growth   = safe(info, "earningsGrowth") or safe(info, "earningsQuarterlyGrowth")
    fwd2_pe       = None
    fwd2_pe_note  = ""
    if fwd_eps and earn_growth and price:
        fwd2_eps = fwd_eps * (1 + earn_growth)
        if fwd2_eps > 0:
            fwd2_pe = price / fwd2_eps
            fwd2_pe_note = f"Based on 1-yr fwd EPS of ${fwd_eps:.2f} grown by analyst earnings growth of {earn_growth*100:.1f}%"
    elif fwd_pe and earn_growth and price:
        # fallback: derive fwd2_eps from fwd P/E and grow it
        implied_fwd_eps = price / fwd_pe if fwd_pe else None
        if implied_fwd_eps and implied_fwd_eps > 0:
            fwd2_eps = implied_fwd_eps * (1 + earn_growth)
            if fwd2_eps > 0:
                fwd2_pe = price / fwd2_eps
                fwd2_pe_note = f"Estimated from fwd P/E of {fwd_pe:.1f}x grown by analyst earnings growth of {earn_growth*100:.1f}%"

    c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
    c1.metric("Market cap",  fmt_large(mkt_cap))

    # Shared tooltip CSS (injected once)
    st.markdown("""
<style>
.pe-tip-wrap{display:inline-flex;align-items:center;gap:5px;margin-top:-8px;margin-bottom:4px}
.pe-tip-icon{display:inline-flex;align-items:center;justify-content:center;
  width:15px;height:15px;border-radius:50%;background:#e9ecef;color:#6c757d;
  font-size:9px;font-weight:700;cursor:help;position:relative;flex-shrink:0}
.pe-tip-icon .pe-tip-text{visibility:hidden;opacity:0;width:240px;
  background:#212529;color:#fff;font-size:11px;line-height:1.5;
  border-radius:8px;padding:8px 10px;position:absolute;z-index:9999;
  left:20px;top:-4px;transition:opacity 0.15s ease;pointer-events:none}
.pe-tip-icon:hover .pe-tip-text{visibility:visible;opacity:1}
</style>
""", unsafe_allow_html=True)

    # P/E (TTM) — value in metric, badge + tooltip rendered below
    pe_display = f"{pe:.1f}" if pe else "—"
    pe_badge   = pe_label(pe) if pe else ""
    with c2:
        st.metric("P/E (TTM)", pe_display)
        if pe_badge:
            st.markdown(f"""
<div class="pe-tip-wrap">
  <span style="font-size:12px;color:#6c757d">{pe_badge}</span>
  <span class="pe-tip-icon">i
    <span class="pe-tip-text">
      <b>P/E Sentiment bands</b><br>
      &#x1F7E2; &lt;15 &mdash; <b>Low PE:</b> below the broad market average; may signal undervaluation or a low-growth sector.<br>
      &#x1F535; 15&ndash;30 &mdash; <b>Fair:</b> in line with typical S&amp;P 500 valuations.<br>
      &#x1F7E1; 30&ndash;60 &mdash; <b>Premium:</b> priced for above-average growth; common in high-growth tech.<br>
      &#x1F534; &gt;60 &mdash; <b>High PE:</b> elevated multiple; sensitive to growth misses or rising rates.<br><br>
      Calculated as <i>share price &divide; trailing 12-month EPS</i>. Best compared within the same sector.
    </span>
  </span>
</div>
""", unsafe_allow_html=True)

    # P/E (1-yr Fwd)
    with c3:
        st.metric("P/E (1yr Fwd)", f"{fwd_pe:.1f}" if fwd_pe else "—")
        st.markdown(f"""
<div class="pe-tip-wrap">
  <span class="pe-tip-icon">i
    <span class="pe-tip-text">
      <b>1-Year Forward P/E</b><br>
      Price divided by analyst consensus EPS estimate for the next 12 months.<br><br>
      A lower forward P/E than TTM suggests earnings are expected to grow. Compare against sector peers and the stock&apos;s own historical forward P/E range for context.
    </span>
  </span>
</div>
""", unsafe_allow_html=True)

    # P/E (2-yr Fwd)
    fwd2_display = f"{fwd2_pe:.1f}" if fwd2_pe else "—"
    with c4:
        st.metric("P/E (2yr Fwd)", fwd2_display)
        tooltip_detail = fwd2_pe_note if fwd2_pe_note else "Insufficient data to estimate 2-year forward EPS. Requires forward EPS and analyst earnings growth rate."
        st.markdown(f"""
<div class="pe-tip-wrap">
  <span class="pe-tip-icon">i
    <span class="pe-tip-text">
      <b>2-Year Forward P/E</b><br>
      Price divided by an estimated EPS two years out, derived by applying the analyst consensus earnings growth rate to the 1-year forward EPS.<br><br>
      {tooltip_detail}<br><br>
      A declining P/E across TTM &rarr; 1yr &rarr; 2yr suggests the market expects strong earnings growth. A flat or rising curve may indicate slowing growth expectations or an expensive valuation.
    </span>
  </span>
</div>
""", unsafe_allow_html=True)

    c5.metric("EPS (TTM)",   f"${eps:.2f}" if eps else "—")
    c6.metric("Div yield",   f"{div_yld*100:.2f}%" if div_yld else "—")
    c7.metric("Beta",        f"{beta:.2f}" if beta else "—")

    st.markdown("")
    c1,c2 = st.columns(2)
    c1.metric("Volume",      fmt_large(vol).replace("$","") if vol else "—")
    c1.metric("Avg volume",  fmt_large(avg_vol).replace("$","") if avg_vol else "—")
    c2.metric("52w high",    f"${hi52:,.2f}" if hi52 else "—")
    c2.metric("52w low",     f"${lo52:,.2f}" if lo52 else "—")

    # 52-week range gauge
    if hi52 and lo52 and hi52 > lo52:
        pct = (price - lo52) / (hi52 - lo52)
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(pct * 100, 1),
            number={"suffix":"%","font":{"size":20}},
            title={"text":"52-week range position","font":{"size":12,"color":"#6c757d"}},
            gauge={
                "axis":{"range":[0,100],"tickvals":[0,25,50,75,100],
                        "ticktext":[f"${lo52:.0f}","25%","50%","75%",f"${hi52:.0f}"],
                        "tickfont":{"size":10}},
                "bar":{"color":"#378ADD","thickness":0.3},
                "steps":[{"range":[0,33],"color":"#fee2e2"},{"range":[33,66],"color":"#fef3c7"},{"range":[66,100],"color":"#d1fae5"}],
                "threshold":{"line":{"color":"#212529","width":2},"thickness":0.8,"value":pct*100},
            }
        ))
        fig_g.update_layout(height=200,margin=dict(t=40,b=10,l=20,r=20),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_g, use_container_width=True)

    if desc:
        st.markdown('<p class="section-label">About</p>', unsafe_allow_html=True)
        st.caption(desc[:700] + ("…" if len(desc) > 700 else ""))


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
    c1.metric("Gross margin",  fmt_pct(gm))
    c2.metric("Net margin",    fmt_pct(npm))
    c3.metric("Op margin",     fmt_pct(opm))
    c4.metric("ROE",           fmt_pct(roe))
    c5.metric("ROA",           fmt_pct(roa))
    c6.metric("Debt/Equity",   f"{de/100:.2f}" if de else "—")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Revenue (TTM)", fmt_large(rev))
    c2.metric("Free cash flow",fmt_large(fcf))
    c3.metric("P/S ratio",     f"{ps:.1f}x" if ps else "—")
    c4.metric("P/B ratio",     f"{pb:.1f}x" if pb else "—")

    # Margin bars
    if any([gm, npm, opm]):
        st.markdown("")
        st.markdown('<p class="section-label">Margins vs S&P 500 average (~11% net)</p>', unsafe_allow_html=True)
        labels = ["Gross margin","Op margin","Net margin","S&P avg net"]
        values = [round((gm or 0)*100,1), round((opm or 0)*100,1), round((npm or 0)*100,1), 11.0]
        colors = ["#1D9E75","#378ADD","#7F77DD","#adb5bd"]
        fig_m = go.Figure()
        for lbl, val, col in zip(labels, values, colors):
            fig_m.add_trace(go.Bar(y=[lbl], x=[val], orientation="h", marker_color=col,
                                   text=[f"{val:.1f}%"], textposition="outside", name=lbl))
        fig_m.update_layout(height=200, showlegend=False, barmode="group",
            margin=dict(t=10,b=10,l=10,r=60),
            xaxis=dict(ticksuffix="%", showgrid=True, gridcolor="#f0f0f0",
                       range=[0, max(values)*1.35]),
            yaxis=dict(title=""),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_m, use_container_width=True)

    # Income statement — annual + quarterly breakdown
    st.markdown('<p class="section-label">Annual income statement </p>', unsafe_allow_html=True)
    want = ["Total Revenue", "Gross Profit", "Operating Income", "Net Income", "EBITDA"]

    try:
        t_obj         = yf.Ticker(ticker)
        annual_fin    = t_obj.financials
        quarterly_fin = t_obj.quarterly_financials

        if not annual_fin.empty:
            ann_rows = [r for r in want if r in annual_fin.index]

            annual_cols    = sorted(annual_fin.columns,    reverse=True)
            quarterly_cols = sorted(quarterly_fin.columns, reverse=True) if not quarterly_fin.empty else []

            # Build column order: recent orphan quarters first, then annual years.
            # Quarterly breakdown is shown ONLY for the most recent completed annual year.
            combined_cols = []  # list of (label, "annual"|"quarterly", original_col)

            latest_annual_date = max(annual_cols)
            most_recent_annual_year = pd.Timestamp(latest_annual_date).year

            # Quarters whose fiscal year is NEWER than the most recent annual year
            # (truly not yet captured in any annual total)
            recent_qtrs = sorted(
                [q for q in quarterly_cols if pd.Timestamp(q).year > most_recent_annual_year],
                reverse=True
            )
            used_qtrs = set()
            for q in recent_qtrs:
                lbl = f"  Q{((pd.Timestamp(q).month-1)//3)+1} {pd.Timestamp(q).year} *"
                combined_cols.append((lbl, "quarterly", q))
                used_qtrs.add(q)

            for ann_col in annual_cols:
                year = pd.Timestamp(ann_col).year
                combined_cols.append((str(year), "annual", ann_col))
                # Only expand quarters for the most recent completed year
                if year == most_recent_annual_year:
                    yr_qtrs = sorted(
                        [q for q in quarterly_cols
                         if pd.Timestamp(q).year == year and q not in used_qtrs],
                        reverse=True
                    )
                    for q in yr_qtrs:
                        lbl = f"  Q{((pd.Timestamp(q).month-1)//3)+1} {year}"
                        combined_cols.append((lbl, "quarterly", q))
                        used_qtrs.add(q)

            # Build display dataframe
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
            st.caption("* = most recent quarter not yet in annual total · Quarters are indented under their fiscal year")
        else:
            st.info("No financial data available for this ticker.")
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
    h = load_hist(ticker, chart_period)

    if h.empty:
        st.warning("No price history available.")
    else:
        chart_type = st.radio("Chart type", ["Line","Candlestick","Area"], horizontal=True)

        fig = go.Figure()
        if chart_type == "Candlestick":
            fig.add_trace(go.Candlestick(x=h.index, open=h["Open"], high=h["High"],
                low=h["Low"], close=h["Close"],
                increasing_line_color="#059669", decreasing_line_color="#dc2626", name=ticker))
        elif chart_type == "Area":
            fig.add_trace(go.Scatter(x=h.index, y=h["Close"], fill="tozeroy",
                fillcolor="rgba(55,138,221,0.1)", line=dict(color="#378ADD",width=1.5), name=ticker))
        else:
            fig.add_trace(go.Scatter(x=h.index, y=h["Close"],
                line=dict(color="#378ADD",width=1.5), name=ticker))

        fig.add_trace(go.Bar(x=h.index, y=h["Volume"],
            marker_color="rgba(55,138,221,0.2)", name="Volume", yaxis="y2"))

        fig.update_layout(
            height=460, margin=dict(t=20,b=20,l=10,r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, rangeslider=dict(visible=False)),
            yaxis=dict(title="Price ($)", showgrid=True, gridcolor="#f0f0f0",
                       tickprefix="$", domain=[0.25,1]),
            yaxis2=dict(title="Volume", showgrid=False, domain=[0,0.2]),
            legend=dict(orientation="h", y=1.05),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

        ret     = ((h["Close"].iloc[-1] / h["Close"].iloc[0]) - 1) * 100
        vol_std = h["Close"].pct_change().std() * (252**0.5) * 100
        c1,c2,c3,c4 = st.columns(4)
        c1.metric(f"Return ({period_label})", f"{ret:+.1f}%")
        c2.metric("Annualised vol",            f"{vol_std:.1f}%")
        c3.metric("Period high",               f"${h['High'].max():,.2f}")
        c4.metric("Period low",                f"${h['Low'].min():,.2f}")


# ══════════════════════════════════════════════════════════════════════════════
# COMPARE
# ══════════════════════════════════════════════════════════════════════════════
with tab_compare:
    st.markdown('<p class="section-label">Enter up to 3 tickers to compare side by side</p>', unsafe_allow_html=True)

    presets = {"Big Tech":["AAPL","MSFT","GOOGL"], "AI Chips":["NVDA","AMD","INTC"],
               "Social":["META","SNAP","PINS"], "E-commerce":["AMZN","SHOP","EBAY"]}
    pc = st.columns(len(presets))
    selected_preset = None
    for i,(label,tks) in enumerate(presets.items()):
        if pc[i].button(label, key=f"preset_{label}"):
            selected_preset = tks

    defaults = selected_preset or [ticker, "MSFT", "GOOGL"]
    c1,c2,c3 = st.columns(3)
    t1 = c1.text_input("Ticker 1", value=defaults[0], key="cmp1").upper().strip()
    t2 = c2.text_input("Ticker 2", value=defaults[1], key="cmp2").upper().strip()
    t3 = c3.text_input("Ticker 3", value=defaults[2], key="cmp3").upper().strip()

    if st.button("Compare →", use_container_width=False):
        compare_list = [t for t in [t1,t2,t3] if t]
        rows = []
        prog = st.progress(0, text="Fetching data…")
        for i, tk in enumerate(compare_list):
            try:
                inf = yf.Ticker(tk).info
                rows.append({
                    "Ticker":       tk,
                    "Name":         safe(inf,"longName",tk)[:28],
                    "Price":        f"${safe(inf,'currentPrice',0) or 0:,.2f}",
                    "Mkt cap":      fmt_large(safe(inf,"marketCap")),
                    "P/E (TTM)":    f"{safe(inf,'trailingPE',0):.1f}x" if safe(inf,"trailingPE") else "—",
                    "Fwd P/E":      f"{safe(inf,'forwardPE',0):.1f}x" if safe(inf,"forwardPE") else "—",
                    "Gross margin": fmt_pct(safe(inf,"grossMargins")),
                    "Net margin":   fmt_pct(safe(inf,"profitMargins")),
                    "ROE":          fmt_pct(safe(inf,"returnOnEquity")),
                    "Revenue TTM":  fmt_large(safe(inf,"totalRevenue")),
                    "Div yield":    f"{(safe(inf,'dividendYield',0) or 0)*100:.2f}%",
                    "Beta":         f"{safe(inf,'beta',0) or 0:.2f}",
                })
            except Exception:
                rows.append({"Ticker":tk,"Name":"Error loading data"})
            prog.progress((i+1)/len(compare_list), text=f"Loaded {tk}")
        prog.empty()

        df_cmp = pd.DataFrame(rows).set_index("Ticker")
        st.dataframe(df_cmp.T, use_container_width=True)

        # Normalised performance chart
        st.markdown("")
        st.markdown('<p class="section-label">Price performance — normalised to 100</p>', unsafe_allow_html=True)
        fig_c = go.Figure()
        colors = ["#378ADD","#1D9E75","#D85A30"]
        for tk, color in zip(compare_list, colors):
            try:
                hh = load_hist(tk, "1y")
                if not hh.empty:
                    norm = (hh["Close"] / hh["Close"].iloc[0] * 100).round(2)
                    fig_c.add_trace(go.Scatter(x=hh.index, y=norm, name=tk,
                                               line=dict(color=color,width=1.5)))
            except Exception:
                pass
        fig_c.update_layout(height=340, margin=dict(t=20,b=20,l=10,r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
            legend=dict(orientation="h", y=1.08),
            hovermode="x unified")
        st.plotly_chart(fig_c, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PROJECTIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab_proj:

    # ── Derived anchors from live data ────────────────────────────────────────
    rev_ttm      = (safe(info,"totalRevenue",0) or 0) / 1e9
    shares_out   = (safe(info,"sharesOutstanding",1e9) or 1e9) / 1e9
    npm_curr     = (safe(info,"profitMargins",0.15) or 0.15) * 100
    pe_ttm       = safe(info,"trailingPE",25) or 25          # TTM P/E — used as cycle anchor
    pe_fwd       = safe(info,"forwardPE",pe_ttm) or pe_ttm   # Forward P/E from Yahoo
    rev_growth_1y = (safe(info,"revenueGrowth",0.08) or 0.08) * 100  # last YoY growth

    # Suggested P/E range: centre on TTM, ±20 % to capture cycle compression/expansion
    pe_low_suggest  = max(5,  int(round(pe_ttm * 0.8)))
    pe_high_suggest = min(200, int(round(pe_ttm * 1.2)))

    # Clamp defaults to slider bounds
    npm_default    = int(min(max(round(npm_curr), 1), 60))
    rev_g_default  = int(min(max(round(rev_growth_1y), 0), 200))
    shares_default = round(float(min(max(shares_out, 0.1), 100)), 1)

    # ── Tooltip CSS ───────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    .tip-wrap { display:inline-flex; align-items:center; gap:6px; margin-bottom:4px; }
    .tip-icon {
        display:inline-flex; align-items:center; justify-content:center;
        width:16px; height:16px; border-radius:50%;
        background:#e9ecef; color:#6c757d; font-size:10px; font-weight:700;
        cursor:help; position:relative; flex-shrink:0;
    }
    .tip-icon .tip-text {
        visibility:hidden; opacity:0;
        width:260px; background:#212529; color:#fff;
        font-size:11px; line-height:1.5; border-radius:8px;
        padding:8px 10px; position:absolute; z-index:999;
        left:22px; top:-4px;
        transition: opacity 0.15s ease;
        pointer-events:none;
    }
    .tip-icon:hover .tip-text { visibility:visible; opacity:1; }
    </style>
    """, unsafe_allow_html=True)

    def tip(label, tooltip_text):
        """Render a label with a hoverable ℹ bubble."""
        st.markdown(f"""
        <div class="tip-wrap">
          <span style="font-size:14px;color:#31333F">{label}</span>
          <span class="tip-icon">i<span class="tip-text">{tooltip_text}</span></span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("Build a bear / base / bull view using the sliders below. Anchors are pulled from live data.")
    st.markdown("")

    # ── Scenario columns ──────────────────────────────────────────────────────
    col_bear, col_base, col_bull = st.columns(3)

    with col_bear:
        st.markdown("##### 🔴 Bear")
        tip("Revenue growth (%)", "Annual top-line growth rate. Bear: assume macro headwinds slow growth well below recent trend. A useful floor is ~0–2%.")
        bear_rev_g  = st.slider("bear_rev_g",  0, 200, max(0, rev_g_default - 8), 1, label_visibility="collapsed", key=f"{ticker}_b_rg")
        tip("Net margin (%)", "Earnings as % of revenue. Bear: margins compress — rising costs, pricing pressure, or reinvestment. Set below the current TTM margin.")
        bear_margin = st.slider("bear_margin", 1, 200, max(1, npm_default - 5),  1, label_visibility="collapsed", key=f"{ticker}_b_nm")
        tip("Exit P/E low", f"The P/E multiple applied to terminal-year EPS to get your price target. TTM P/E is {pe_ttm:.1f}x; bear multiples should sit below that — e.g. {pe_low_suggest}x — reflecting de-rating risk if growth disappoints.")
        bear_pe     = st.slider("bear_pe",     5, 200, pe_low_suggest,            1, label_visibility="collapsed", key=f"{ticker}_b_pe")

    with col_base:
        st.markdown("##### 🔵 Base")
        tip("Revenue growth (%)", "Annual top-line growth rate. Base: use recent YoY growth or analyst consensus. Current trailing growth is shown in the snapshot.")
        base_rev_g  = st.slider("base_rev_g",  0, 200, rev_g_default,             1, label_visibility="collapsed", key=f"{ticker}_ba_rg")
        tip("Net margin (%)", f"Earnings as % of revenue. Base: hold margins roughly flat at the current TTM level ({npm_default}%). Only raise if there's a clear path to leverage.")
        base_margin = st.slider("base_margin", 1, 200, npm_default,              1, label_visibility="collapsed", key=f"{ticker}_ba_nm")
        tip("Exit P/E", f"Base: anchor to the TTM P/E ({pe_ttm:.1f}x) or a blend of TTM + forward ({pe_fwd:.1f}x). Avoid using a number that's materially above the historical average without justification.")
        base_pe     = st.slider("base_pe",     5, 200, int(min(max(round(pe_ttm),5),200)), 1, label_visibility="collapsed", key=f"{ticker}_ba_pe")

    with col_bull:
        st.markdown("##### 🟢 Bull")
        tip("Revenue growth (%)", "Annual top-line growth rate. Bull: reflect an optimistic but plausible upside — new markets, product cycles, market share gains. Avoid extrapolating short-term spikes.")
        bull_rev_g  = st.slider("bull_rev_g",  0, 200, min(200, rev_g_default + 8),1, label_visibility="collapsed", key=f"{ticker}_bu_rg")
        tip("Net margin (%)", "Earnings as % of revenue. Bull: margins expand via operating leverage as revenue scales. Keep it grounded — most mature companies top out at 25–40%.")
        bull_margin = st.slider("bull_margin", 1, 200, min(200, npm_default + 5),1, label_visibility="collapsed", key=f"{ticker}_bu_nm")
        tip("Exit P/E high", f"Bull: you can push above TTM if growth genuinely accelerates, but be cautious — P/E expansion is the most fragile assumption. The TTM is {pe_ttm:.1f}x and forward is {pe_fwd:.1f}x; {pe_high_suggest}x is a reasonable upper bound without heroic assumptions.")
        bull_pe     = st.slider("bull_pe",     5, 200, pe_high_suggest,           1, label_visibility="collapsed", key=f"{ticker}_bu_pe")

    st.markdown("")

    # Shared inputs row
    sc1, sc2 = st.columns([3,1])
    with sc1:
        tip("Shares outstanding (B)", "Total diluted shares used to convert net income → EPS → price target. Check for buyback programmes that reduce this over time (bullish) or dilution from stock comp (bearish). Pre-filled from live data.")
        shares_b = st.slider("shares_b", 0.1, 100.0, shares_default, 0.1, label_visibility="collapsed", key=f"{ticker}_shares")
        tip("Projection horizon (years)", "How many years forward to project. Longer horizons amplify compounding but also uncertainty. 3–5 years is the typical range for fundamental valuation; beyond 7 years, assumptions dominate entirely.")
        horizon = st.slider("horizon", 1, 10, 5, 1, label_visibility="collapsed", key=f"{ticker}_hz")

    with sc2:
        st.markdown('<p class="section-label">Current snapshot</p>', unsafe_allow_html=True)
        st.metric("Revenue (TTM)",  f"${rev_ttm:.1f}B")
        st.metric("Net margin",     f"{npm_default}%")
        st.metric("P/E TTM / Fwd",  f"{pe_ttm:.1f}x / {pe_fwd:.1f}x")
        st.metric("Price today",    f"${price:,.2f}")
        shares_display = f"{shares_default:.2f}B" if shares_default < 1 else f"{shares_default:.1f}B"
        st.metric("Shares outstanding", shares_display)

    # ── Compute scenario paths ─────────────────────────────────────────────────
    years_range = list(range(0, horizon + 1))

    def price_path(rev_g, margin, pe):
        path = [price]
        for y in range(1, horizon + 1):
            fr  = rev_ttm * ((1 + rev_g/100) ** y)
            eps = (fr * (margin/100) * 1e9) / (shares_b * 1e9)
            path.append(round(eps * pe, 2))
        return path

    bear_path = price_path(bear_rev_g, bear_margin, bear_pe)
    base_path = price_path(base_rev_g, base_margin, base_pe)
    bull_path = price_path(bull_rev_g, bull_margin, bull_pe)

    # ── Target metrics ─────────────────────────────────────────────────────────
    st.markdown("")
    st.markdown(f'<p class="section-label">Year {horizon} price targets & CAGR</p>', unsafe_allow_html=True)
    mc1, mc2, mc3 = st.columns(3)
    for col, label, path, color in [
        (mc1, "🔴 Bear", bear_path, "red"),
        (mc2, "🔵 Base", base_path, "blue"),
        (mc3, "🟢 Bull", bull_path, "green"),
    ]:
        tgt  = path[-1]
        cagr = ((tgt / price) ** (1/horizon) - 1) * 100 if price and horizon else 0
        col.metric(f"{label} — {horizon}yr target", f"${tgt:,.0f}", f"{cagr:+.1f}% CAGR")

    # ── Projection chart ───────────────────────────────────────────────────────
    fig_p = go.Figure()

    # Shaded uncertainty band (bear → bull)
    fig_p.add_trace(go.Scatter(
        x=years_range + years_range[::-1],
        y=bull_path + bear_path[::-1],
        fill="toself", fillcolor="rgba(55,138,221,0.08)",
        line=dict(color="rgba(0,0,0,0)"),
        hoverinfo="skip", showlegend=False,
    ))

    for path, color, dash, name in [
        (bear_path, "#dc2626", "dot",   "🔴 Bear"),
        (base_path, "#378ADD", "solid", "🔵 Base"),
        (bull_path, "#059669", "dash",  "🟢 Bull"),
    ]:
        fig_p.add_trace(go.Scatter(
            x=years_range, y=path,
            mode="lines+markers",
            name=name,
            line=dict(color=color, width=2, dash=dash),
            marker=dict(size=6, color=color),
            hovertemplate="%{y:$,.0f}<extra>" + name + "</extra>",
        ))

    fig_p.add_hline(y=price, line_dash="dot", line_color="#adb5bd",
                    annotation_text=f"Today ${price:.0f}", annotation_position="right")

    fig_p.update_layout(
        height=340, margin=dict(t=30,b=20,l=10,r=80),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="Years from now", showgrid=False,
                   tickvals=years_range, ticktext=[str(y) for y in years_range]),
        yaxis=dict(title="Price ($)", showgrid=True, gridcolor="#f0f0f0", tickprefix="$"),
        legend=dict(orientation="h", y=1.08),
        hovermode="x unified",
    )
    st.plotly_chart(fig_p, use_container_width=True)

    # ── Year-by-year breakdown table ──────────────────────────────────────────
    st.markdown("")
    st.markdown(f'<p class="section-label">Year-by-year price targets & CAGR</p>', unsafe_allow_html=True)

    current_year = pd.Timestamp.now().year
    table_rows = []
    for y in range(0, horizon + 1):
        bear_p = bear_path[y]
        base_p = base_path[y]
        bull_p = bull_path[y]

        def cagr_str(p, yr):
            if yr == 0 or not price: return "—"
            c = ((p / price) ** (1 / yr) - 1) * 100
            return f"{c:+.1f}%"

        table_rows.append({
            "Year":      "Today" if y == 0 else str(current_year + y),
            "🔴 Bear":   f"${bear_p:,.0f}",
            "Bear CAGR": cagr_str(bear_p, y),
            "🔵 Base":   f"${base_p:,.0f}",
            "Base CAGR": cagr_str(base_p, y),
            "🟢 Bull":   f"${bull_p:,.0f}",
            "Bull CAGR": cagr_str(bull_p, y),
        })

    df_proj = pd.DataFrame(table_rows).set_index("Year")
    st.dataframe(df_proj, use_container_width=True)

    # ── PE context note ────────────────────────────────────────────────────────
    st.info(
        f"**P/E anchors for {ticker}:** TTM = {pe_ttm:.1f}x · Forward = {pe_fwd:.1f}x · "
        f"Suggested range: {pe_low_suggest}–{pe_high_suggest}x (±20% of TTM). "
        "Bear/bull multiples outside this range require specific justification (e.g. sector re-rating, rate environment change)."
    )
    st.caption("⚠️ Projections are illustrative only and not financial advice.")
