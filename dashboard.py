import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

st.set_page_config(page_title="Tequila Weekly Dashboard", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&family=DM+Mono:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .block-container { padding: 1.75rem 2.5rem 3rem; max-width: 1400px; }
    h1 { font-size: 1.6rem !important; font-weight: 600 !important; letter-spacing: -0.02em; }
    h2 { font-size: 1.05rem !important; font-weight: 600 !important; color: #1e293b; margin-bottom: 0 !important; }
    h3 { font-size: 0.85rem !important; font-weight: 500 !important; color: #64748b; text-transform: uppercase; letter-spacing: .06em; margin: 0 !important; }
    .stMetric { background: #f8f7f5; border: 1px solid #e8e4dc; border-radius: 10px; padding: .85rem 1rem; }
    .stMetric label { font-size: 10.5px !important; text-transform: uppercase; letter-spacing: .07em; color: #94a3b8 !important; }
    .stMetric [data-testid="stMetricValue"] { font-size: 1.55rem !important; font-weight: 600 !important; color: #0f172a !important; }
    .stMetric [data-testid="stMetricDelta"] { font-size: 12px !important; }
    div[data-testid="stHorizontalBlock"] { gap: 12px; }
    .chart-card {
        background: #ffffff;
        border: 1px solid #e8e4dc;
        border-radius: 12px;
        padding: 1.25rem 1.5rem 1rem;
        margin-bottom: 16px;
    }
    .chart-title { font-size: 14px; font-weight: 600; color: #0f172a; margin-bottom: 2px; }
    .chart-sub  { font-size: 12px; color: #94a3b8; margin-bottom: 12px; }
    .filter-bar {
        background: #f1f0ec;
        border-radius: 10px;
        padding: .75rem 1.25rem;
        margin-bottom: 20px;
        display: flex; gap: 12px; align-items: center;
    }
    .section-divider { border: none; border-top: 1.5px solid #f1f0ec; margin: 8px 0 20px; }
    div[data-testid="stSelectbox"] > div { border-radius: 8px !important; }
    div[data-testid="stMultiSelect"] > div { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ── Palette ──────────────────────────────────────────────────────────────────
EXPR_COLORS = {
    "Blanco":   {"ty": "#2563EB", "ly": "#93C5FD"},
    "Reposado": {"ty": "#16A34A", "ly": "#86EFAC"},
    "Joven":    {"ty": "#D97706", "ly": "#FCD34D"},
    "Anejo":    {"ty": "#9333EA", "ly": "#D8B4FE"},
}
EXPR_LIST = ["Blanco", "Reposado", "Joven", "Anejo"]
PIE_COLORS = ["#2563EB", "#16A34A", "#D97706", "#9333EA"]

BROAD_MARKETS = [
    "Total FMCG Retailers",
    "Total Liquor Open State",
    "Total Grocery Stores",
    "Total Convenience Stores",
    "Albertsons Companies Total Company",
    "Total Wine & More Liquor Total",
    "Whole Foods Total",
    "Specs Liquor Total",
    "Beverages & More Total Omni",
    "Ahold Delhaize Total",
]

# ── Data ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load():
    df = pd.read_excel("weekly_cleaned.xlsx")
    df["Year"] = df["Date"].dt.year
    return df

df_all = load()
df_ya  = df_all[df_all["Total $ Sales YA"].notna()].copy()

# ── Header + global filters ──────────────────────────────────────────────────
st.markdown("# 🥃 Tequila Weekly Sales Dashboard")
st.markdown("<p style='color:#94a3b8;margin-top:-10px;font-size:13px;'>Weekly performance · TY vs LY · All expressions</p>", unsafe_allow_html=True)
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

fc1, fc2, fc3 = st.columns([1, 1, 2])
with fc1:
    year_opts = sorted([y for y in df_ya["Year"].unique() if y > 2023])
    sel_year  = st.selectbox("📅 This Year", year_opts, index=len(year_opts) - 2 if len(year_opts) > 1 else 0)
prior_year = sel_year - 1

with fc2:
    all_exprs   = sorted(df_ya["Expression"].unique().tolist())
    sel_expr = st.multiselect("🍶 Expressions", all_exprs, default=all_exprs)
    if not sel_expr:
        sel_expr = all_exprs

with fc3:
    all_markets = BROAD_MARKETS
    sel_markets = st.multiselect("🏪 Markets", all_markets, default=all_markets)
    if not sel_markets:
        sel_markets = all_markets

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# Filtered base
base = df_ya[
    (df_ya["Year"] == sel_year) &
    (df_ya["Expression"].isin(sel_expr)) &
    (df_ya["Markets"].isin(sel_markets))
].copy()

# ══════════════════════════════════════════════════════════════════════════════
# KPI SCORECARD
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### KPI Scorecard")
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

total_ty    = base["Total $ Sales"].sum()
total_ly    = base["Total $ Sales YA"].sum()
sales_delta = (total_ty - total_ly) / total_ly * 100 if total_ly else 0

units_ty    = base["Total EQ Unit Sales"].sum()
units_ly    = base["Total EQ Unit Sales YA"].sum()
units_delta = (units_ty - units_ly) / units_ly * 100 if units_ly else 0

price_ty    = base["Total Average EQ Price"].mean()
price_ly    = base["Total Average EQ Price YA"].mean()
price_delta = (price_ty - price_ly) / price_ly * 100 if price_ly else 0

acv_ty      = base["% ACV (Max)"].sum()
acv_ly      = base["% ACV (Max) YA"].sum()
acv_delta   = acv_ty - acv_ly

weekly_agg  = base.groupby("Date")["Total $ Sales % Change vs Year Ago"].mean()
weeks_pos   = (weekly_agg > 0).sum()
weeks_total = len(weekly_agg)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total $ Sales TY",  f"${total_ty/1e6:.1f}M",   f"{sales_delta:+.1f}% vs LY")
k2.metric("EQ Unit Sales TY",  f"{units_ty/1e3:.1f}K",    f"{units_delta:+.1f}% vs LY")
k3.metric("Avg EQ Price",       f"${price_ty:.2f}",        f"{price_delta:+.1f}% vs LY")
k4.metric("% ACV (Max)",        f"{acv_ty:.1f}%",          f"{acv_delta:+.2f}pt vs LY")
k5.metric("Weeks Ahead of LY", f"{weeks_pos} / {weeks_total}")

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 — Weekly TY vs LY trend
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Chart 1 — Weekly $ Sales: TY vs LY")
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

view_mode = st.radio("View by", ["All expressions", "By expression"], horizontal=True, key="c1_mode")

def weekly_agg_all(data):
    return data.groupby("Date").agg(
        sales    =("Total $ Sales", "sum"),
        sales_ya =("Total $ Sales YA", "sum"),
        pct_chg  =("Total $ Sales % Change vs Year Ago", "mean"),
    ).reset_index()

def weekly_agg_expr(data, expr):
    return data[data["Expression"] == expr].groupby("Date").agg(
        sales    =("Total $ Sales", "sum"),
        sales_ya =("Total $ Sales YA", "sum"),
        pct_chg  =("Total $ Sales % Change vs Year Ago", "mean"),
    ).reset_index()

fig1 = make_subplots(specs=[[{"secondary_y": True}]])

if view_mode == "All expressions":
    w = weekly_agg_all(base)
    fig1.add_trace(go.Scatter(
        x=w["Date"], y=w["sales"],
        name=f"$ Sales {sel_year}",
        line=dict(color="#2563EB", width=2.5),
        fill="tozeroy", fillcolor="rgba(37,99,235,0.06)",
        hovertemplate="<b>%{x|%b %d}</b><br>TY: $%{y:,.0f}<extra></extra>",
    ), secondary_y=False)
    fig1.add_trace(go.Scatter(
        x=w["Date"], y=w["sales_ya"],
        name=f"$ Sales {prior_year} (LY)",
        line=dict(color="#93C5FD", width=2, dash="dot"),
        hovertemplate="<b>%{x|%b %d}</b><br>LY: $%{y:,.0f}<extra></extra>",
    ), secondary_y=False)
    fig1.add_trace(go.Bar(
        x=w["Date"], y=w["pct_chg"] * 100,
        name="% Chg vs LY",
        marker_color=["rgba(22,163,74,.4)" if v >= 0 else "rgba(220,38,38,.4)" for v in w["pct_chg"]],
        hovertemplate="<b>%{x|%b %d}</b><br>Δ: %{y:.1f}%<extra></extra>",
    ), secondary_y=True)
else:
    for expr in sel_expr:
        c = EXPR_COLORS.get(expr, {"ty": "#475569", "ly": "#94a3b8"})
        w = weekly_agg_expr(base, expr)
        if w.empty: continue
        fig1.add_trace(go.Scatter(
            x=w["Date"], y=w["sales"],
            name=f"{expr} {sel_year}",
            line=dict(color=c["ty"], width=2.5),
            hovertemplate=f"<b>{expr}</b> %{{x|%b %d}}<br>TY: $%{{y:,.0f}}<extra></extra>",
        ), secondary_y=False)
        fig1.add_trace(go.Scatter(
            x=w["Date"], y=w["sales_ya"],
            name=f"{expr} {prior_year}",
            line=dict(color=c["ly"], width=1.8, dash="dot"),
            hovertemplate=f"<b>{expr}</b> %{{x|%b %d}}<br>LY: $%{{y:,.0f}}<extra></extra>",
        ), secondary_y=False)

fig1.update_layout(
    height=400, margin=dict(l=0, r=0, t=10, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, font=dict(size=11)),
    hovermode="x unified", plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="DM Sans", size=12, color="#334155"),
    xaxis=dict(showgrid=False, tickformat="%b %d '%y", tickangle=-30, tickfont=dict(size=10)),
    yaxis=dict(tickprefix="$", tickformat=",.0f", gridcolor="#f1f0ec", zeroline=False,
               title="Weekly $ Sales", title_font=dict(size=11)),
    yaxis2=dict(ticksuffix="%", gridcolor="rgba(0,0,0,0)", zeroline=True,
                zerolinecolor="#e2e0da", title="% Change vs LY", title_font=dict(size=11))
                if view_mode == "All expressions" else dict(visible=False),
    bargap=0.3,
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 — YoY % change bar by week
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Chart 2 — Weekly $ Sales % Change vs LY")
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

w2 = weekly_agg_all(base)
w2["color"] = w2["pct_chg"].apply(lambda v: "rgba(22,163,74,.65)" if v >= 0 else "rgba(220,38,38,.65)")

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=w2["Date"], y=w2["pct_chg"] * 100,
    marker_color=w2["color"],
    hovertemplate="<b>%{x|%b %d, %Y}</b><br>% Chg: %{y:.1f}%<extra></extra>",
))
fig2.add_hline(y=0, line_color="#cbd5e1", line_width=1.5)
fig2.update_layout(
    height=300, margin=dict(l=0, r=0, t=10, b=0),
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="DM Sans", size=12, color="#334155"),
    xaxis=dict(showgrid=False, tickformat="%b %d '%y", tickangle=-30, tickfont=dict(size=10)),
    yaxis=dict(ticksuffix="%", gridcolor="#f1f0ec", zeroline=False,
               title="% Change vs LY", title_font=dict(size=11)),
    bargap=0.25, showlegend=False,
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 3 — Market comparison grouped bar
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Chart 3 — $ Sales by Market: TY vs LY")
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

mkt_base = df_ya[
    (df_ya["Year"] == sel_year) &
    (df_ya["Expression"].isin(sel_expr)) &
    (df_ya["Markets"].isin(sel_markets))
].groupby("Markets").agg(
    sales_ty=("Total $ Sales", "sum"),
    sales_ly=("Total $ Sales YA", "sum"),
).reset_index()
mkt_base["pct_chg"] = (mkt_base["sales_ty"] - mkt_base["sales_ly"]) / mkt_base["sales_ly"] * 100

sort_by = st.radio("Sort by", ["TY Sales", "% Change vs LY", "LY Sales"], horizontal=True, key="c3_sort")
sort_col = {"TY Sales": "sales_ty", "% Change vs LY": "pct_chg", "LY Sales": "sales_ly"}[sort_by]
mkt_sorted = mkt_base.sort_values(sort_col, ascending=True)

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    y=mkt_sorted["Markets"], x=mkt_sorted["sales_ly"],
    name=f"{prior_year} (LY)", orientation="h",
    marker_color="#cbd5e1",
    hovertemplate="<b>%{y}</b><br>LY: $%{x:,.0f}<extra></extra>",
))
fig3.add_trace(go.Bar(
    y=mkt_sorted["Markets"], x=mkt_sorted["sales_ty"],
    name=f"{sel_year} (TY)", orientation="h",
    marker_color="#2563EB",
    hovertemplate="<b>%{y}</b><br>TY: $%{x:,.0f}<br>Δ: %{customdata:.1f}%<extra></extra>",
    customdata=mkt_sorted["pct_chg"],
))
fig3.update_layout(
    height=420, margin=dict(l=0, r=0, t=10, b=0),
    barmode="group", bargap=0.25, bargroupgap=0.08,
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="DM Sans", size=11, color="#334155"),
    xaxis=dict(tickprefix="$", tickformat=",.0f", gridcolor="#f1f0ec",
               title="$ Sales", title_font=dict(size=11)),
    yaxis=dict(showgrid=False, tickfont=dict(size=10)),
    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, font=dict(size=11)),
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 4 — Expression mix
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Chart 4 — Expression Mix: TY vs LY")
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

mix = df_ya[
    (df_ya["Year"] == sel_year) &
    (df_ya["Expression"].isin(sel_expr))
].groupby("Expression").agg(
    sales_ty=("Total $ Sales", "sum"),
    sales_ly=("Total $ Sales YA", "sum"),
).reset_index()
mix["share_ty"] = mix["sales_ty"] / mix["sales_ty"].sum() * 100
mix["share_ly"] = mix["sales_ly"] / mix["sales_ly"].sum() * 100
mix["shift"]    = mix["share_ty"] - mix["share_ly"]

col_pie1, col_pie2, col_shift = st.columns([1.1, 1.1, 0.9])

expr_colors_list = [EXPR_COLORS.get(e, {}).get("ty", "#94a3b8") for e in mix["Expression"]]

with col_pie1:
    fig_pie_ty = go.Figure(go.Pie(
        labels=mix["Expression"], values=mix["sales_ty"],
        marker_colors=expr_colors_list,
        hole=0.55,
        textinfo="percent+label",
        textfont=dict(size=11, family="DM Sans"),
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    fig_pie_ty.update_layout(
        height=260, margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="white", showlegend=False,
        title=dict(text=f"Mix {sel_year} (TY)", font=dict(size=12, family="DM Sans"), x=0.5),
        annotations=[dict(text="TY", x=0.5, y=0.5, font_size=14, showarrow=False,
                          font=dict(family="DM Sans", color="#64748b"))]
    )
    st.plotly_chart(fig_pie_ty, use_container_width=True)

with col_pie2:
    fig_pie_ly = go.Figure(go.Pie(
        labels=mix["Expression"], values=mix["sales_ly"],
        marker_colors=expr_colors_list,
        hole=0.55,
        textinfo="percent+label",
        textfont=dict(size=11, family="DM Sans"),
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    fig_pie_ly.update_layout(
        height=260, margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="white", showlegend=False,
        title=dict(text=f"Mix {prior_year} (LY)", font=dict(size=12, family="DM Sans"), x=0.5),
        annotations=[dict(text="LY", x=0.5, y=0.5, font_size=14, showarrow=False,
                          font=dict(family="DM Sans", color="#64748b"))]
    )
    st.plotly_chart(fig_pie_ly, use_container_width=True)

with col_shift:
    st.markdown("<p style='font-size:12px;font-weight:600;color:#0f172a;margin-bottom:10px;'>Mix shift (TY vs LY)</p>", unsafe_allow_html=True)
    for _, row in mix.sort_values("shift", ascending=False).iterrows():
        color = EXPR_COLORS.get(row["Expression"], {}).get("ty", "#94a3b8")
        arrow = "▲" if row["shift"] >= 0 else "▼"
        shift_color = "#16A34A" if row["shift"] >= 0 else "#DC2626"
        st.markdown(f"""
        <div style='margin-bottom:12px;'>
          <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;'>
            <span style='font-size:12px;font-weight:500;color:#334155;'>{row['Expression']}</span>
            <span style='font-size:12px;font-weight:600;color:{shift_color};'>{arrow} {abs(row['shift']):.1f}pt</span>
          </div>
          <div style='height:6px;background:#f1f0ec;border-radius:3px;'>
            <div style='width:{row["share_ty"]:.1f}%;height:100%;background:{color};border-radius:3px;'></div>
          </div>
          <div style='font-size:10px;color:#94a3b8;margin-top:2px;'>TY {row["share_ty"]:.1f}% · LY {row["share_ly"]:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 5 — Avg EQ Price
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Chart 5 — Avg EQ Price: TY vs LY")
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

pt = base.groupby("Date").agg(
    price_ty =("Total Average EQ Price", "mean"),
    price_ly =("Total Average EQ Price YA", "mean"),
    tdp_ty   =("Total TDP", "sum"),
    tdp_ly   =("Total TDP YA", "sum"),
).reset_index()

fig5 = go.Figure()
fig5.add_trace(go.Scatter(
    x=pt["Date"], y=pt["price_ty"],
    name=f"Avg EQ Price {sel_year}",
    line=dict(color="#2563EB", width=2.5),
    hovertemplate="<b>%{x|%b %d}</b><br>Price TY: $%{y:.2f}<extra></extra>",
))
fig5.add_trace(go.Scatter(
    x=pt["Date"], y=pt["price_ly"],
    name=f"Avg EQ Price {prior_year}",
    line=dict(color="#93C5FD", width=2, dash="dot"),
    hovertemplate="<b>%{x|%b %d}</b><br>Price LY: $%{y:.2f}<extra></extra>",
))

fig5.update_layout(
    height=340, margin=dict(l=0, r=0, t=10, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, font=dict(size=11)),
    hovermode="x unified", plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="DM Sans", size=12, color="#334155"),
    xaxis=dict(showgrid=False, tickformat="%b %d '%y", tickangle=-30, tickfont=dict(size=10)),
    yaxis=dict(tickprefix="$", tickformat=".2f", gridcolor="#f1f0ec", zeroline=False,
               title="Avg EQ Price", title_font=dict(size=11)),
)
st.plotly_chart(fig5, use_container_width=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 6 — Total TDP
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Chart 6 — Total TDP: TY vs LY")
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

fig6 = go.Figure()
fig6.add_trace(go.Scatter(
    x=pt["Date"], y=pt["tdp_ty"],
    name=f"TDP {sel_year}",
    line=dict(color="#D97706", width=2.5),
    hovertemplate="<b>%{x|%b %d}</b><br>TDP TY: %{y:,.0f}<extra></extra>",
))
fig6.add_trace(go.Scatter(
    x=pt["Date"], y=pt["tdp_ly"],
    name=f"TDP {prior_year}",
    line=dict(color="#FCD34D", width=2, dash="dot"),
    hovertemplate="<b>%{x|%b %d}</b><br>TDP LY: %{y:,.0f}<extra></extra>",
))

fig6.update_layout(
    height=340, margin=dict(l=0, r=0, t=10, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, font=dict(size=11)),
    hovermode="x unified", plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="DM Sans", size=12, color="#334155"),
    xaxis=dict(showgrid=False, tickformat="%b %d '%y", tickangle=-30, tickfont=dict(size=10)),
    yaxis=dict(tickformat=",.0f", gridcolor="#f1f0ec", zeroline=False,
               title="Total TDP", title_font=dict(size=11)),
)
st.plotly_chart(fig6, use_container_width=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# WEEKLY DETAIL TABLE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Weekly Detail Table")
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

tbl = base.groupby("Date").agg(
    sales_ty   =("Total $ Sales", "sum"),
    sales_ly   =("Total $ Sales YA", "sum"),
    units_ty   =("Total EQ Unit Sales", "sum"),
    units_ly   =("Total EQ Unit Sales YA", "sum"),
    price_ty   =("Total Average EQ Price", "mean"),
    tdp_ty     =("Total TDP", "sum"),
    acv_ty     =("% ACV (Max)", "mean"),
    pct_sales  =("Total $ Sales % Change vs Year Ago", "mean"),
    pct_units  =("Total EQ Unit Sales % Change vs Year Ago", "mean"),
).reset_index().sort_values("Date", ascending=False)

tbl["Week Ending"]      = tbl["Date"].dt.strftime("%b %d, %Y")
tbl["$ Sales TY"]       = tbl["sales_ty"].map("${:,.0f}".format)
tbl["$ Sales LY"]       = tbl["sales_ly"].map("${:,.0f}".format)
tbl["$ Δ vs LY"]        = (tbl["pct_sales"] * 100).map("{:+.1f}%".format)
tbl["EQ Units TY"]      = tbl["units_ty"].map("{:,.0f}".format)
tbl["Units Δ vs LY"]    = (tbl["pct_units"] * 100).map("{:+.1f}%".format)
tbl["Avg EQ Price"]     = tbl["price_ty"].map("${:.2f}".format)
tbl["TDP"]              = tbl["tdp_ty"].map("{:,.0f}".format)
tbl["% ACV"]            = tbl["acv_ty"].map("{:.1f}%".format)

display_cols = ["Week Ending","$ Sales TY","$ Sales LY","$ Δ vs LY",
                "EQ Units TY","Units Δ vs LY","Avg EQ Price","TDP","% ACV"]
st.dataframe(tbl[display_cols], use_container_width=True, hide_index=True, height=320)
