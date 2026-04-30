import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ─── CONFIGURAÇÃO DA PÁGINA ───────────────────────────────────────────────────
st.set_page_config(
    page_title="DRE Executivo 2024",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── PALETA DARK-BLUE ─────────────────────────────────────────────────────────
C = {
    "bg":        "#060d1f",
    "card":      "#0b1630",
    "card2":     "#0f1e3d",
    "border":    "#1a3a6b",
    "accent":    "#1e6fcf",
    "blue":      "#2196f3",
    "cyan":      "#00bcd4",
    "green":     "#00e676",
    "red":       "#ff5252",
    "yellow":    "#ffd740",
    "orange":    "#ff9800",
    "purple":    "#ce93d8",
    "text":      "#e8edf8",
    "muted":     "#7a9cc6",
    "grid":      "#112244",
}

# ─── CSS GLOBAL ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }}
    .stApp {{
        background-color: {C['bg']};
        color: {C['text']};
    }}
    [data-testid="stSidebar"] {{
        background-color: {C['card2']};
        border-right: 1px solid {C['border']};
    }}
    [data-testid="stSidebar"] * {{
        color: {C['text']} !important;
    }}
    .block-container {{
        padding: 1rem 2rem 2rem 2rem;
        max-width: 100%;
    }}
    h1, h2, h3, h4 {{ color: {C['text']}; }}
    .metric-card {{
        background: linear-gradient(135deg, {C['card']} 0%, {C['card2']} 100%);
        border: 1px solid {C['border']};
        border-radius: 12px;
        padding: 16px 18px;
        text-align: center;
        transition: transform 0.2s;
    }}
    .metric-card:hover {{ transform: translateY(-2px); }}
    .metric-label {{
        color: {C['muted']};
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }}
    .metric-value {{
        font-size: 22px;
        font-weight: 800;
        line-height: 1.1;
    }}
    .metric-sub {{
        font-size: 11px;
        margin-top: 4px;
        color: {C['muted']};
    }}
    .section-title {{
        color: {C['muted']};
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
        padding-bottom: 4px;
        border-bottom: 1px solid {C['border']};
    }}
    .insight-card {{
        background: {C['card2']};
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }}
    .insight-title {{
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 4px;
    }}
    .insight-body {{
        font-size: 11px;
        color: {C['muted']};
        line-height: 1.5;
    }}
    .dre-table {{ width: 100%; border-collapse: collapse; }}
    .dre-table td {{
        padding: 7px 12px;
        font-size: 12px;
        border-bottom: 1px solid {C['grid']};
    }}
    .dre-header {{ background: #0a1929; font-weight: 700; color: {C['cyan']}; }}
    .dre-total  {{ background: #112244; font-weight: 700; }}
    .dre-final  {{ background: #0a2a4a; font-weight: 800; font-size: 13px; }}
    .dre-item   {{ color: {C['muted']}; }}
    .dre-pct    {{ background: {C['card2']}; font-style: italic; }}
    [data-testid="stSelectbox"] div,
    [data-testid="stMultiSelect"] div {{
        background-color: {C['card2']} !important;
        border-color: {C['border']} !important;
        color: {C['text']} !important;
    }}
    div[data-baseweb="select"] > div {{
        background-color: {C['card2']} !important;
        border-color: {C['border']} !important;
    }}
    .stSelectbox label, .stMultiSelect label {{ color: {C['muted']} !important; font-size: 11px; }}
    .header-bar {{
        background: linear-gradient(135deg, {C['card2']} 0%, #0a1929 100%);
        border-bottom: 2px solid {C['accent']};
        padding: 18px 24px;
        margin: -1rem -2rem 1.5rem -2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .header-tag {{ color: {C['cyan']}; font-size: 10px; font-weight: 700; letter-spacing: 2px; }}
    .header-title {{ color: {C['text']}; font-size: 26px; font-weight: 800; margin-top: 2px; }}
    .header-right {{ text-align: right; font-size: 12px; }}
    .stPlotlyChart {{ border-radius: 10px; overflow: hidden; }}
    div.stPlotlyChart > div {{ border-radius: 10px; }}
</style>
""", unsafe_allow_html=True)

# ─── DADOS ───────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("DADOS/dre_dataset.csv", sep=";", decimal=",")
    df["data"] = pd.to_datetime(df["data"])
    df["mes_ano"] = df["data"].dt.to_period("M").astype(str)
    return df

df = load_data()

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def fmt_M(v):
    if abs(v) >= 1_000_000:
        return f"R$ {v/1_000_000:.2f}M"
    if abs(v) >= 1_000:
        return f"R$ {v/1_000:.1f}K"
    return f"R$ {v:.0f}"

def calcular_dre(dff):
    g = dff.groupby("grupo_dre")["valor"].sum()
    rb  = g.get("Receita Bruta", 0)
    ded = g.get("Deduções", 0)
    cmv = g.get("CMV", 0)
    csp = g.get("CSP", 0)
    dc  = g.get("Despesas Comerciais", 0)
    da  = g.get("Despesas Administrativas", 0)
    rf  = g.get("Receitas Financeiras", 0)
    df_ = g.get("Despesas Financeiras", 0)
    or_ = g.get("Outras Receitas", 0)
    od  = g.get("Outras Despesas", 0)
    imp = g.get("Impostos sobre Lucro", 0)
    rl  = rb + ded
    lb  = rl + cmv + csp
    ebit  = lb + dc + da
    res_fin = rf + df_
    out = or_ + od
    lair  = ebit + res_fin + out
    ll    = lair + imp
    return dict(
        rb=rb, ded=ded, rl=rl, cmv=cmv, csp=csp, lb=lb,
        dc=dc, da=da, ebit=ebit, res_fin=res_fin, out=out,
        lair=lair, imp=imp, ll=ll,
        mg_bruta=(lb/rl*100) if rl != 0 else 0,
        mg_ebit=(ebit/rl*100) if rl != 0 else 0,
        mg_liq=(ll/rl*100) if rl != 0 else 0,
    )

def chart_cfg(title=""):
    """Layout base sem xaxis/yaxis — evita conflito de chave duplicada no update_layout."""
    return dict(
        paper_bgcolor=C["card"],
        plot_bgcolor=C["card"],
        font=dict(color=C["text"], family="Inter, Segoe UI, sans-serif", size=12),
        title=dict(text=title, font=dict(size=13, color=C["muted"]), x=0.01, pad=dict(l=8)),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=C["border"],
                    font=dict(size=10), orientation="h", y=1.05),
        hoverlabel=dict(bgcolor=C["card2"], bordercolor=C["border"],
                        font=dict(color=C["text"], size=11)),
    )

def xax(**kwargs):
    base = dict(gridcolor=C["grid"], linecolor=C["border"], zerolinecolor=C["border"])
    return {**base, **kwargs}

def yax(**kwargs):
    base = dict(gridcolor=C["grid"], linecolor=C["border"], zerolinecolor=C["border"])
    return {**base, **kwargs}

# ─── SIDEBAR — FILTROS ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding: 8px 0 20px 0;'>
        <div style='font-size:28px; margin-bottom:4px;'>📊</div>
        <div style='color:{C["cyan"]}; font-size:10px; font-weight:700; letter-spacing:2px;'>DRE EXECUTIVO</div>
        <div style='color:{C["text"]}; font-size:16px; font-weight:700;'>2024</div>
    </div>
    <hr style='border-color:{C["border"]}; margin-bottom:20px;'>
    <div style='color:{C["muted"]}; font-size:10px; font-weight:700; letter-spacing:1px; margin-bottom:12px;'>
        FILTROS
    </div>
    """, unsafe_allow_html=True)

    trimestre = st.selectbox(
        "Trimestre", ["Todos"] + sorted(df["trimestre"].unique().tolist()))
    regiao = st.selectbox(
        "Região", ["Todas"] + sorted(df["regiao"].unique().tolist()))
    filial = st.selectbox(
        "Filial", ["Todas"] + sorted(df["filial_nome"].unique().tolist()))
    categoria = st.selectbox(
        "Categoria", ["Todas"] + sorted(df["categoria_produto"].dropna().unique().tolist()))

    st.markdown(f"<hr style='border-color:{C['border']}; margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='color:{C["muted"]}; font-size:10px; text-align:center;'>
        5.000 lançamentos · 9 filiais<br>4 trimestres · 2024
    </div>
    """, unsafe_allow_html=True)

# ─── FILTRAR ─────────────────────────────────────────────────────────────────
dff = df.copy()
if trimestre != "Todos":   dff = dff[dff["trimestre"] == trimestre]
if regiao    != "Todas":   dff = dff[dff["regiao"] == regiao]
if filial    != "Todas":   dff = dff[dff["filial_nome"] == filial]
if categoria != "Todas":   dff = dff[dff["categoria_produto"] == categoria]

dre = calcular_dre(dff)

# ─── HEADER ───────────────────────────────────────────────────────────────────
filtro_ativo = " · ".join([
    t for t in [
        trimestre if trimestre != "Todos" else "",
        regiao if regiao != "Todas" else "",
        filial.replace("Filial ", "").replace("Matriz ", "") if filial != "Todas" else "",
        categoria if categoria != "Todas" else "",
    ] if t
]) or "Visão Consolidada"

st.markdown(f"""
<div class="header-bar">
    <div>
        <div class="header-tag">DEMONSTRAÇÃO DO RESULTADO DO EXERCÍCIO</div>
        <div class="header-title">Dashboard Executivo 2024</div>
    </div>
    <div class="header-right">
        <div style="color:{C['muted']}; font-size:11px;">Filtro ativo</div>
        <div style="color:{C['cyan']}; font-weight:700; font-size:13px;">{filtro_ativo}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── KPI CARDS ────────────────────────────────────────────────────────────────
def kpi_html(label, valor, cor, sub=""):
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color:{cor};">{valor}</div>
        {f'<div class="metric-sub">{sub}</div>' if sub else ''}
    </div>"""

c1, c2, c3, c4, c5, c6 = st.columns(6)
cols_kpi = [c1, c2, c3, c4, c5, c6]
kpis = [
    ("💰 Receita Bruta",   fmt_M(dre["rb"]),   C["blue"],   ""),
    ("📉 Deduções",        fmt_M(dre["ded"]),  C["red"],    f"{abs(dre['ded']/dre['rb']*100):.1f}% da RB"),
    ("📊 Receita Líquida", fmt_M(dre["rl"]),   C["cyan"],   ""),
    ("📈 Lucro Bruto",     fmt_M(dre["lb"]),   C["green"] if dre["lb"] >= 0 else C["red"],
                                                             f"Margem {dre['mg_bruta']:.1f}%"),
    ("⚡ EBIT",            fmt_M(dre["ebit"]), C["yellow"] if dre["ebit"] >= 0 else C["red"],
                                                             f"Margem {dre['mg_ebit']:.1f}%"),
    ("🏆 Lucro Líquido",   fmt_M(dre["ll"]),   C["green"] if dre["ll"] >= 0 else C["red"],
                                                             f"Margem {dre['mg_liq']:.1f}%"),
]
for col, (lbl, val, cor, sub) in zip(cols_kpi, kpis):
    with col:
        st.markdown(kpi_html(lbl, val, cor, sub), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── LINHA 1: WATERFALL + EVOLUÇÃO MENSAL ─────────────────────────────────────
col_wf, col_ev = st.columns([1, 1.7])

with col_wf:
    st.markdown('<div class="section-title">Cascata DRE — Composição do Resultado</div>',
                unsafe_allow_html=True)
    wf_x = ["Rec.\nBruta", "Deduções", "Rec.\nLíquida", "CMV", "CSP",
             "Lucro\nBruto", "Desp.\nCom.", "Desp.\nAdm.", "EBIT",
             "Res.\nFin.", "Outras", "LAIR", "Impostos", "Lucro\nLíquido"]
    wf_y = [dre["rb"], dre["ded"], None, dre["cmv"], dre["csp"], None,
            dre["dc"], dre["da"], None, dre["res_fin"], dre["out"], None,
            dre["imp"], None]
    wf_m = ["absolute", "relative", "total", "relative", "relative", "total",
            "relative", "relative", "total", "relative", "relative", "total",
            "relative", "total"]

    fig_wf = go.Figure(go.Waterfall(
        orientation="v", measure=wf_m, x=wf_x, y=wf_y,
        text=[fmt_M(v) if v is not None else "" for v in wf_y],
        textposition="outside",
        textfont=dict(color=C["text"], size=8),
        increasing=dict(marker=dict(color=C["green"], line=dict(width=0))),
        decreasing=dict(marker=dict(color=C["red"], line=dict(width=0))),
        totals=dict(marker=dict(color=C["blue"], line=dict(width=0))),
        connector=dict(line=dict(color=C["border"], width=1, dash="dot")),
    ))
    fig_wf.update_layout(**chart_cfg(), showlegend=False, height=400,
                         margin=dict(l=16, r=16, t=40, b=16),
                         xaxis=xax(tickfont=dict(size=8)),
                         yaxis=yax(tickformat=",.0f"))
    st.plotly_chart(fig_wf, use_container_width=True)

with col_ev:
    st.markdown('<div class="section-title">Evolução Mensal — Receita · Custos · Resultado</div>',
                unsafe_allow_html=True)

    meses = sorted(dff["mes_ano"].unique())
    ev_rows = []
    for m in meses:
        dm = dff[dff["mes_ano"] == m]
        d  = calcular_dre(dm)
        ev_rows.append(dict(
            mes=m, RB=d["rb"], Custo=abs(d["cmv"]) + abs(d["csp"]),
            DespOp=abs(d["dc"]) + abs(d["da"]), LL=d["ll"]
        ))
    ev = pd.DataFrame(ev_rows)

    fig_ev = make_subplots(specs=[[{"secondary_y": True}]])
    fig_ev.add_trace(go.Bar(x=ev["mes"], y=ev["RB"],     name="Receita Bruta",
                            marker_color=C["blue"], opacity=0.85), secondary_y=False)
    fig_ev.add_trace(go.Bar(x=ev["mes"], y=-ev["Custo"], name="CMV + CSP",
                            marker_color=C["red"], opacity=0.85), secondary_y=False)
    fig_ev.add_trace(go.Bar(x=ev["mes"], y=-ev["DespOp"], name="Desp. Operacionais",
                            marker_color=C["yellow"], opacity=0.8), secondary_y=False)
    fig_ev.add_trace(go.Scatter(x=ev["mes"], y=ev["LL"], name="Lucro Líquido",
                                mode="lines+markers",
                                line=dict(color=C["green"], width=2.5, shape="spline"),
                                marker=dict(size=7, color=C["green"],
                                            line=dict(width=2, color=C["bg"]))),
                     secondary_y=True)

    fig_ev.update_layout(
        **chart_cfg(), barmode="relative", height=400,
        margin=dict(l=16, r=40, t=40, b=50),
        xaxis=xax(tickangle=-45, tickfont=dict(size=9)),
        yaxis=yax(tickformat=",.0f", title=""),
        yaxis2=dict(showgrid=False, tickformat=",.0f", tickfont=dict(color=C["green"])),
    )
    st.plotly_chart(fig_ev, use_container_width=True)

# ─── LINHA 2: MARGENS + REGIÃO + CATEGORIA ────────────────────────────────────
col_mg, col_reg, col_cat = st.columns([1.3, 1, 1])

with col_mg:
    st.markdown('<div class="section-title">Evolução de Margens (%)</div>', unsafe_allow_html=True)
    mg_rows = []
    for m in meses:
        d = calcular_dre(dff[dff["mes_ano"] == m])
        mg_rows.append(dict(mes=m, Bruta=d["mg_bruta"], EBIT=d["mg_ebit"], Líquida=d["mg_liq"]))
    mg = pd.DataFrame(mg_rows)

    fig_mg = go.Figure()
    for col_name, cor, fill in [
        ("Bruta",   C["blue"],   "rgba(33,150,243,0.08)"),
        ("EBIT",    C["yellow"], "rgba(255,215,64,0.08)"),
        ("Líquida", C["green"],  "rgba(0,230,118,0.08)"),
    ]:
        fig_mg.add_trace(go.Scatter(
            x=mg["mes"], y=mg[col_name], name=f"Mg. {col_name}",
            mode="lines+markers",
            line=dict(color=cor, width=2.2, shape="spline"),
            marker=dict(size=5, color=cor, line=dict(width=1.5, color=C["bg"])),
            fill="tozeroy", fillcolor=fill,
            hovertemplate=f"<b>Mg. {col_name}</b><br>%{{x}}<br>%{{y:.1f}}%<extra></extra>",
        ))
    fig_mg.update_layout(
        **chart_cfg(), height=320,
        margin=dict(l=16, r=16, t=40, b=50),
        xaxis=xax(tickangle=-45, tickfont=dict(size=8)),
        yaxis=yax(ticksuffix="%", tickfont=dict(size=9)),
    )
    st.plotly_chart(fig_mg, use_container_width=True)

with col_reg:
    st.markdown('<div class="section-title">Resultado por Região</div>', unsafe_allow_html=True)
    reg_rows = []
    for r in dff["regiao"].unique():
        d = calcular_dre(dff[dff["regiao"] == r])
        reg_rows.append(dict(Região=r, RL=d["rl"], LB=d["lb"], LL=d["ll"]))
    reg_df = pd.DataFrame(reg_rows).sort_values("RL")

    fig_reg = go.Figure()
    for col_name, cor in [("RL", C["blue"]), ("LB", C["cyan"]), ("LL", C["green"])]:
        lbl = {"RL": "Rec. Líquida", "LB": "Lucro Bruto", "LL": "Lucro Líq."}[col_name]
        fig_reg.add_trace(go.Bar(
            y=reg_df["Região"], x=reg_df[col_name], name=lbl,
            orientation="h", marker_color=cor, opacity=0.87,
            text=[fmt_M(v) for v in reg_df[col_name]],
            textposition="outside", textfont=dict(size=8),
        ))
    fig_reg.update_layout(
        **chart_cfg(), barmode="group", height=320,
        xaxis=xax(tickformat=",.0f"),
        yaxis=yax(),
        margin=dict(l=16, r=60, t=40, b=16),
    )
    st.plotly_chart(fig_reg, use_container_width=True)

with col_cat:
    st.markdown('<div class="section-title">Receita por Categoria</div>', unsafe_allow_html=True)
    cat_df = (dff[dff["grupo_dre"] == "Receita Bruta"]
              .groupby("categoria_produto")["valor"].sum()
              .reset_index().dropna())
    cat_df.columns = ["Categoria", "Receita"]

    fig_cat = go.Figure(go.Pie(
        labels=cat_df["Categoria"],
        values=cat_df["Receita"],
        hole=0.6,
        marker=dict(
            colors=[C["blue"], C["cyan"], C["green"]],
            line=dict(color=C["bg"], width=3),
        ),
        textinfo="label+percent",
        textfont=dict(size=11, color=C["text"]),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>",
        rotation=90,
    ))
    fig_cat.update_layout(
        **chart_cfg(), height=320, showlegend=False,
        margin=dict(l=16, r=16, t=16, b=16),
        annotations=[dict(
            text=fmt_M(cat_df["Receita"].sum()),
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=13, color=C["text"], family="Inter"),
        )],
    )
    st.plotly_chart(fig_cat, use_container_width=True)

# ─── LINHA 3: FILIAIS + DESPESAS ─────────────────────────────────────────────
col_fil, col_desp = st.columns([1.6, 1])

with col_fil:
    st.markdown('<div class="section-title">Performance por Filial</div>', unsafe_allow_html=True)
    fil_rows = []
    for f in dff["filial_nome"].unique():
        d = calcular_dre(dff[dff["filial_nome"] == f])
        nome = f.replace("Filial ", "").replace("Matriz ", "★ ")
        fil_rows.append(dict(Filial=nome, RL=d["rl"], LB=d["lb"], LL=d["ll"]))
    fil_df = pd.DataFrame(fil_rows).sort_values("RL", ascending=True)

    fig_fil = go.Figure()
    for col_name, cor, lbl in [
        ("RL", C["blue"],  "Rec. Líquida"),
        ("LB", C["cyan"],  "Lucro Bruto"),
        ("LL", C["green"], "Lucro Líquido"),
    ]:
        fig_fil.add_trace(go.Bar(
            y=fil_df["Filial"], x=fil_df[col_name], name=lbl,
            orientation="h", marker_color=cor, opacity=0.87,
            text=[fmt_M(v) for v in fil_df[col_name]],
            textposition="outside", textfont=dict(size=9),
        ))
    fig_fil.update_layout(
        **chart_cfg(), barmode="group", height=360,
        xaxis=xax(tickformat=",.0f"),
        yaxis=yax(),
        margin=dict(l=16, r=80, t=40, b=16),
    )
    st.plotly_chart(fig_fil, use_container_width=True)

with col_desp:
    st.markdown('<div class="section-title">Top Contas de Despesa</div>', unsafe_allow_html=True)
    desp_grupos = ["Despesas Administrativas", "Despesas Comerciais",
                   "Despesas Financeiras", "Outras Despesas"]
    desp_df = (dff[dff["grupo_dre"].isin(desp_grupos)]
               .groupby("conta_contabil")["valor"].sum()
               .abs().reset_index()
               .sort_values("valor", ascending=True)
               .tail(12))
    desp_df.columns = ["Conta", "Valor"]

    fig_desp = go.Figure(go.Bar(
        x=desp_df["Valor"], y=desp_df["Conta"],
        orientation="h",
        marker=dict(
            color=desp_df["Valor"],
            colorscale=[[0, C["accent"]], [0.5, C["orange"]], [1, C["red"]]],
            showscale=False,
        ),
        text=[fmt_M(v) for v in desp_df["Valor"]],
        textposition="outside",
        textfont=dict(size=9, color=C["text"]),
    ))
    fig_desp.update_layout(
        **chart_cfg(), showlegend=False, height=360,
        xaxis=xax(tickformat=",.0f"),
        yaxis=yax(tickfont=dict(size=9)),
        margin=dict(l=16, r=80, t=40, b=16),
    )
    st.plotly_chart(fig_desp, use_container_width=True)

# ─── LINHA 4: DRE ESTRUTURADA + INSIGHTS ─────────────────────────────────────
col_dre, col_ins = st.columns([1.2, 1])

with col_dre:
    st.markdown('<div class="section-title">DRE Estruturada — Demonstração Completa</div>',
                unsafe_allow_html=True)
    rl = dre["rl"]
    linhas = [
        ("RECEITA BRUTA",                   dre["rb"],       "header",  None),
        ("&nbsp;&nbsp;Deduções s/ Venda",    dre["ded"],      "item",    None),
        ("RECEITA LÍQUIDA",                  dre["rl"],       "total",   None),
        ("&nbsp;&nbsp;CMV",                  dre["cmv"],      "item",    None),
        ("&nbsp;&nbsp;CSP",                  dre["csp"],      "item",    None),
        ("LUCRO BRUTO",                      dre["lb"],       "total",   None),
        ("&nbsp;&nbsp;Margem Bruta",         dre["mg_bruta"], "pct",     "%"),
        ("&nbsp;&nbsp;Despesas Comerciais",  dre["dc"],       "item",    None),
        ("&nbsp;&nbsp;Despesas Adm.",        dre["da"],       "item",    None),
        ("EBIT",                             dre["ebit"],     "total",   None),
        ("&nbsp;&nbsp;Margem EBIT",          dre["mg_ebit"],  "pct",     "%"),
        ("&nbsp;&nbsp;Resultado Financeiro", dre["res_fin"],  "item",    None),
        ("&nbsp;&nbsp;Outras Rec./Desp.",    dre["out"],      "item",    None),
        ("LAIR",                             dre["lair"],     "total",   None),
        ("&nbsp;&nbsp;Impostos sobre Lucro", dre["imp"],      "item",    None),
        ("LUCRO LÍQUIDO",                    dre["ll"],       "final",   None),
        ("&nbsp;&nbsp;Margem Líquida",       dre["mg_liq"],   "pct",     "%"),
    ]

    rows_html = ""
    for nome, val, tipo, unidade in linhas:
        cor_val = C["green"] if val >= 0 else C["red"]
        if tipo == "pct":
            v_fmt = f"{val:.1f}%"
            row_cls = "dre-pct"
            cor_val = C["green"] if val >= 0 else C["red"]
            fw = "400"
        elif tipo in ("header", "total"):
            v_fmt = fmt_M(val)
            row_cls = "dre-total" if tipo == "total" else "dre-header"
            fw = "700"
        elif tipo == "final":
            v_fmt = fmt_M(val)
            row_cls = "dre-final"
            fw = "800"
        else:
            v_fmt = fmt_M(val)
            row_cls = "dre-item"
            fw = "400"

        rows_html += f"""
        <tr class="{row_cls}">
            <td style="font-weight:{fw};">{nome}</td>
            <td style="text-align:right; color:{cor_val}; font-weight:{fw};">{v_fmt}</td>
        </tr>"""

    st.markdown(f"""
    <table class="dre-table">
        <thead>
            <tr style="background:#0a1929; border-bottom: 2px solid {C['accent']};">
                <th style="padding:8px 12px; color:{C['cyan']}; font-size:11px; text-align:left;">Conta</th>
                <th style="padding:8px 12px; color:{C['cyan']}; font-size:11px; text-align:right;">Valor</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)

with col_ins:
    st.markdown('<div class="section-title">Insights Estratégicos Executivos</div>',
                unsafe_allow_html=True)

    # calcula métricas para insights
    taxa_ded    = abs(dre["ded"]) / dre["rb"] * 100 if dre["rb"] else 0
    desp_op_tot = abs(dre["dc"]) + abs(dre["da"])
    desp_op_pct = desp_op_tot / rl * 100 if rl else 0

    top_filial = max(dff["filial_nome"].unique(),
                     key=lambda f: calcular_dre(dff[dff["filial_nome"] == f])["lb"])
    top_reg    = max(dff["regiao"].unique(),
                     key=lambda r: calcular_dre(dff[dff["regiao"] == r])["rl"])

    ml = dre["mg_liq"]
    mb = dre["mg_bruta"]
    if ml >= 15:   saude, s_cor = "Excelente 🟢", C["green"]
    elif ml >= 8:  saude, s_cor = "Saudável 🔵", C["cyan"]
    elif ml >= 3:  saude, s_cor = "Atenção 🟡", C["yellow"]
    else:          saude, s_cor = "Crítica 🔴", C["red"]

    insights = [
        (f"Saúde Financeira: {saude}", s_cor, "📊",
         f"Margem Líquida de <b>{ml:.1f}%</b> sobre Receita Líquida de <b>{fmt_M(rl)}</b>. "
         f"Margem Bruta em <b>{mb:.1f}%</b> — "
         f"{'eficiência produtiva adequada.' if mb > 40 else 'pressão nos custos diretos.'}"),

        ("Carga Tributária sobre Vendas", C["yellow"], "🏛️",
         f"Deduções representam <b>{taxa_ded:.1f}%</b> da Receita Bruta "
         f"(<b>{fmt_M(abs(dre['ded']))}</b>). "
         f"{'Impacto alto — avaliar planejamento tributário.' if taxa_ded > 20 else 'Carga moderada e controlada.'}"),

        ("Eficiência Operacional", C["blue"], "⚙️",
         f"EBIT de <b>{fmt_M(dre['ebit'])}</b> com margem <b>{dre['mg_ebit']:.1f}%</b>. "
         f"Despesas operacionais de <b>{fmt_M(desp_op_tot)}</b> representam "
         f"<b>{desp_op_pct:.1f}%</b> da receita líquida."),

        (f"Destaque: {top_reg} / {top_filial.replace('Filial ','').replace('Matriz ','')}",
         C["cyan"], "🗺️",
         f"Região <b>{top_reg}</b> lidera em Receita Líquida. "
         f"Filial com maior Lucro Bruto: <b>{top_filial.replace('Filial ','').replace('Matriz ','★ ')}</b>. "
         f"Replicar modelo comercial nas demais unidades."),

        ("Resultado Financeiro", C["red"] if dre["res_fin"] < 0 else C["green"], "💳",
         f"Resultado financeiro de <b>{fmt_M(dre['res_fin'])}</b>. "
         f"{'Pressão de juros relevante — priorizar reestruturação do passivo.' if dre['res_fin'] < -2_000_000 else 'Impacto financeiro sob controle.'}"),

        ("Recomendação Executiva", C["green"] if ml >= 8 else C["yellow"], "🎯",
         f"{'Manter estratégia atual com foco em crescimento de receita e controle de custos.' if ml >= 8 else 'Revisão urgente de precificação e estrutura de custos para recuperação de margem.'} "
         f"Resultado final: <b>{fmt_M(dre['ll'])}</b>."),
    ]

    for titulo, cor, icone, texto in insights:
        st.markdown(f"""
        <div class="insight-card" style="border-left: 3px solid {cor};">
            <div class="insight-title" style="color:{cor};">{icone}&nbsp; {titulo}</div>
            <div class="insight-body">{texto}</div>
        </div>
        """, unsafe_allow_html=True)

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="
    text-align: center;
    padding: 20px;
    margin-top: 20px;
    border-top: 1px solid {C['border']};
    color: {C['muted']};
    font-size: 11px;
">
    DRE Executivo 2024 · Powered by Streamlit + Plotly · {len(dff):,} lançamentos filtrados de {len(df):,} total
</div>
""", unsafe_allow_html=True)
