import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="DRE Executivo 2024",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── PALETA ──────────────────────────────────────────────────────────────────
C = {
    "bg":      "#060d1f", "card":   "#0b1630", "card2":  "#0f1e3d",
    "border":  "#1a3a6b", "accent": "#1e6fcf", "blue":   "#2196f3",
    "cyan":    "#00bcd4", "green":  "#00e676", "red":    "#ff5252",
    "yellow":  "#ffd740", "orange": "#ff9800", "purple": "#ce93d8",
    "text":    "#e8edf8", "muted":  "#7a9cc6", "grid":   "#112244",
}

PALETA      = [C["blue"], C["cyan"], C["green"], C["yellow"], C["orange"], C["purple"], C["red"], "#4caf50"]
PALETA_FILL = [
    "rgba(33,150,243,0.15)",   # blue
    "rgba(0,188,212,0.15)",    # cyan
    "rgba(0,230,118,0.15)",    # green
    "rgba(255,215,64,0.15)",   # yellow
    "rgba(255,152,0,0.15)",    # orange
    "rgba(206,147,216,0.15)",  # purple
    "rgba(255,82,82,0.15)",    # red
    "rgba(76,175,80,0.15)",    # #4caf50
]

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', 'Segoe UI', sans-serif; }}
.stApp {{ background-color: {C['bg']}; color: {C['text']}; }}
[data-testid="stSidebar"] {{ background-color: {C['card2']}; border-right: 1px solid {C['border']}; }}
[data-testid="stSidebar"] * {{ color: {C['text']} !important; }}
.block-container {{ padding: 0.5rem 1.5rem 2rem 1.5rem; max-width: 100%; }}
h1,h2,h3,h4 {{ color: {C['text']}; }}
.kpi-card {{
    background: linear-gradient(135deg, {C['card']} 0%, {C['card2']} 100%);
    border: 1px solid {C['border']}; border-radius: 12px;
    padding: 14px 16px; text-align: center;
}}
.kpi-label {{ color:{C['muted']}; font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px; }}
.kpi-value {{ font-size:20px; font-weight:800; line-height:1.1; }}
.kpi-sub   {{ font-size:11px; margin-top:4px; color:{C['muted']}; }}
.kpi-delta-pos {{ font-size:11px; margin-top:3px; color:{C['green']}; font-weight:600; }}
.kpi-delta-neg {{ font-size:11px; margin-top:3px; color:{C['red']};   font-weight:600; }}
.sec-title {{
    color:{C['muted']}; font-size:11px; font-weight:700; text-transform:uppercase;
    letter-spacing:1.5px; margin-bottom:8px; padding-bottom:4px;
    border-bottom:1px solid {C['border']};
}}
.alert-card {{
    border-radius:8px; padding:12px 14px; margin-bottom:10px;
}}
.insight-card {{
    background:{C['card2']}; border-radius:8px; padding:12px 14px; margin-bottom:10px;
}}
.insight-title {{ font-size:12px; font-weight:700; margin-bottom:4px; }}
.insight-body  {{ font-size:11px; color:{C['muted']}; line-height:1.55; }}
.dre-table {{ width:100%; border-collapse:collapse; }}
.dre-table td {{ padding:7px 12px; font-size:12px; border-bottom:1px solid {C['grid']}; }}
.badge {{
    display:inline-block; padding:2px 10px; border-radius:20px;
    font-size:10px; font-weight:700; letter-spacing:.5px;
}}
div[data-baseweb="select"] > div {{ background-color:{C['card2']} !important; border-color:{C['border']} !important; }}
.stTabs [data-baseweb="tab-list"] {{ background-color:{C['card2']}; border-radius:8px; padding:4px; gap:4px; }}
.stTabs [data-baseweb="tab"] {{
    background-color:transparent; border-radius:6px; color:{C['muted']};
    font-size:12px; font-weight:600; padding:6px 16px;
}}
.stTabs [aria-selected="true"] {{ background-color:{C['accent']}; color:{C['text']}; }}
.stTabs [data-baseweb="tab-panel"] {{ padding-top:16px; }}
</style>
""", unsafe_allow_html=True)

# ─── DADOS ───────────────────────────────────────────────────────────────────
SHEET_ID  = "1NN-6E7B0CBMmc1LWpXZjixxG2gbosSkvAO6ZHEb3YGo"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=300)
def load_data():
    from datetime import datetime
    try:
        df = pd.read_csv(SHEET_URL)
        fonte = "Google Sheets"
    except Exception:
        df = pd.read_csv("DADOS/dre_dataset.csv", sep=";", decimal=",")
        fonte = "arquivo local (fallback)"
    # garante coluna valor sempre numérica, independente do formato
    df["valor"] = (
        df["valor"].astype(str)
        .str.replace(r"\.", "", regex=True)      # remove separador de milhar (ponto)
        .str.replace(",", ".", regex=False)       # converte decimal BR para EN
        .pipe(pd.to_numeric, errors="coerce")
        .fillna(0.0)
    )
    df["data"]    = pd.to_datetime(df["data"], errors="coerce")
    df["mes_ano"] = df["data"].dt.to_period("M").astype(str)
    df["mes_num"] = df["data"].dt.month
    ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return df, ts, fonte

df, ultima_atualizacao, fonte_dados = load_data()

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def fmt_M(v):
    if abs(v) >= 1_000_000: return f"R$ {v/1_000_000:.2f}M"
    if abs(v) >= 1_000:     return f"R$ {v/1_000:.1f}K"
    return f"R$ {v:.0f}"

def fmt_pct(v): return f"{v:.1f}%"

def calcular_dre_cached(trimestre, regiao, filial, categoria):
    dff = _filtrar(trimestre, regiao, filial, categoria)
    return _dre(dff), dff

def pct(num, den):
    try:
        d = float(den)
        return float(num) / d * 100 if d != 0.0 else 0.0
    except Exception:
        return 0.0

def _filtrar(trimestre, regiao, filial, categoria):
    dff = df.copy()
    if trimestre != "Todos": dff = dff[dff["trimestre"] == trimestre]
    if regiao    != "Todas": dff = dff[dff["regiao"]    == regiao]
    if filial    != "Todas": dff = dff[dff["filial_nome"]== filial]
    if categoria != "Todas": dff = dff[dff["categoria_produto"] == categoria]
    return dff

def _dre(dff):
    g = dff.groupby("grupo_dre")["valor"].sum()
    def gv(key):
        try:
            return float(g.get(key, 0))
        except Exception:
            return 0.0
    rb  = gv("Receita Bruta")
    ded = gv("Deduções")
    cmv = gv("CMV")
    csp = gv("CSP")
    dc  = gv("Despesas Comerciais")
    da  = gv("Despesas Administrativas")
    rf  = gv("Receitas Financeiras")
    df_ = gv("Despesas Financeiras")
    or_ = gv("Outras Receitas")
    od  = gv("Outras Despesas")
    imp = gv("Impostos sobre Lucro")
    rl  = rb + ded
    lb  = rl + cmv + csp
    ebit   = lb + dc + da
    res_fin= rf + df_
    out    = or_ + od
    lair   = ebit + res_fin + out
    ll     = lair + imp
    return dict(
        rb=rb, ded=ded, rl=rl, cmv=cmv, csp=csp, lb=lb,
        dc=dc, da=da, ebit=ebit, res_fin=res_fin, out=out,
        lair=lair, imp=imp, ll=ll,
        mg_bruta=pct(lb, rl),
        mg_ebit=pct(ebit, rl),
        mg_liq=pct(ll, rl),
        taxa_ded=pct(abs(ded), rb),
        custo_direto=abs(cmv)+abs(csp),
        desp_op=abs(dc)+abs(da),
    )

def chart_base(h=None):
    d = dict(
        paper_bgcolor=C["card"], plot_bgcolor=C["card"],
        font=dict(color=C["text"], family="Inter, Segoe UI, sans-serif", size=11),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10), orientation="h", y=1.05),
        hoverlabel=dict(bgcolor=C["card2"], bordercolor=C["border"], font=dict(color=C["text"], size=11)),
        hovermode="closest",
    )
    if h: d["height"] = h
    return d

def xax(**kw): return {**dict(gridcolor=C["grid"], linecolor=C["border"], zerolinecolor=C["border"]), **kw}
def yax(**kw): return {**dict(gridcolor=C["grid"], linecolor=C["border"], zerolinecolor=C["border"]), **kw}

def kpi_html(label, valor, cor, sub="", delta=None):
    delta_html = ""
    if delta is not None:
        cls = "kpi-delta-pos" if delta >= 0 else "kpi-delta-neg"
        sym = "▲" if delta >= 0 else "▼"
        delta_html = f'<div class="{cls}">{sym} {abs(delta):.1f}% vs trim. ant.</div>'
    return f"""<div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value" style="color:{cor};">{valor}</div>
        {f'<div class="kpi-sub">{sub}</div>' if sub else ''}
        {delta_html}
    </div>"""

def sec(txt):
    st.markdown(f'<div class="sec-title">{txt}</div>', unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;padding:8px 0 16px 0;'>
        <div style='font-size:32px;'>📊</div>
        <div style='color:{C["cyan"]};font-size:10px;font-weight:700;letter-spacing:2px;'>DRE EXECUTIVO</div>
        <div style='color:{C["text"]};font-size:18px;font-weight:800;'>2024</div>
    </div>
    <hr style='border-color:{C["border"]};margin-bottom:16px;'>
    <div style='color:{C["muted"]};font-size:10px;font-weight:700;letter-spacing:1px;margin-bottom:10px;'>FILTROS</div>
    """, unsafe_allow_html=True)

    # inicializa session_state dos filtros
    for key, default in [("f_tri","Todos"),("f_reg","Todas"),("f_fil","Todas"),("f_cat","Todas")]:
        if key not in st.session_state:
            st.session_state[key] = default

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 Atualizar", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col_btn2:
        if st.button("✖ Limpar", use_container_width=True):
            st.session_state.f_tri = "Todos"
            st.session_state.f_reg = "Todas"
            st.session_state.f_fil = "Todas"
            st.session_state.f_cat = "Todas"
            st.rerun()

    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)

    trimestre = st.selectbox("Trimestre", ["Todos"] + sorted(df["trimestre"].unique().tolist()), key="f_tri")
    regiao    = st.selectbox("Região",    ["Todas"] + sorted(df["regiao"].unique().tolist()),    key="f_reg")
    filial    = st.selectbox("Filial",    ["Todas"] + sorted(df["filial_nome"].unique().tolist()), key="f_fil")
    categoria = st.selectbox("Categoria", ["Todas"] + sorted(df["categoria_produto"].dropna().unique().tolist()), key="f_cat")

    st.markdown(f"<hr style='border-color:{C['border']};margin:16px 0;'>", unsafe_allow_html=True)

    # mini-resumo no sidebar
    dre_side, dff_side = calcular_dre_cached(trimestre, regiao, filial, categoria)
    n = len(dff_side)
    st.markdown(f"""
    <div style='font-size:11px;color:{C["muted"]};'>
        <div style='margin-bottom:6px;'><b style='color:{C["text"]};'>Lançamentos:</b> {n:,}</div>
        <div style='margin-bottom:6px;'><b style='color:{C["text"]};'>Receita Bruta:</b> {fmt_M(dre_side["rb"])}</div>
        <div style='margin-bottom:6px;'><b style='color:{C["text"]};'>Lucro Líquido:</b>
            <span style='color:{"#00e676" if dre_side["ll"]>=0 else "#ff5252"};font-weight:700;'>
            {fmt_M(dre_side["ll"])}</span></div>
        <div style='margin-bottom:10px;'><b style='color:{C["text"]};'>Margem Líq.:</b>
            <span style='color:{"#00e676" if dre_side["mg_liq"]>=0 else "#ff5252"};font-weight:700;'>
            {dre_side["mg_liq"]:.1f}%</span></div>
        <div style='font-size:10px;border-top:1px solid {C["border"]};padding-top:8px;'>
            🕐 <b style='color:{C["text"]};'>Atualizado:</b><br>{ultima_atualizacao}
        </div>
        <div style='font-size:10px;margin-top:4px;'>
            📡 <b style='color:{C["text"]};'>Fonte:</b> {fonte_dados}
        </div>
    </div>
    <hr style='border-color:{C["border"]};margin:16px 0;'>
    <div style='font-size:10px;color:{C["muted"]};text-align:center;line-height:1.7;'>
        <a href="https://www.linkedin.com/in/breno-teodomiro-power-bi/" target="_blank"
           style='color:{C["cyan"]};text-decoration:none;'>🔗 LinkedIn</a> ·
        <a href="https://github.com/Breno-Teodomiro" target="_blank"
           style='color:{C["cyan"]};text-decoration:none;'>🐙 GitHub</a>
    </div>
    """, unsafe_allow_html=True)

# ─── DADOS FILTRADOS ─────────────────────────────────────────────────────────
dre, dff = calcular_dre_cached(trimestre, regiao, filial, categoria)
meses    = sorted(dff["mes_ano"].unique())

# ─── HEADER ──────────────────────────────────────────────────────────────────
filtro_ativo = " · ".join([t for t in [
    trimestre if trimestre != "Todos" else "",
    regiao    if regiao    != "Todas" else "",
    filial.replace("Filial ","").replace("Matriz ","") if filial != "Todas" else "",
    categoria if categoria != "Todas" else "",
] if t]) or "Visão Consolidada"

ml_cor = C["green"] if dre["mg_liq"] >= 10 else C["yellow"] if dre["mg_liq"] >= 0 else C["red"]
st.markdown(f"""
<div style='background:linear-gradient(135deg,{C["card2"]} 0%,#0a1929 100%);
     border-bottom:2px solid {C["accent"]};padding:16px 20px;
     margin:-0.5rem -1.5rem 1rem -1.5rem;
     display:flex;justify-content:space-between;align-items:center;'>
    <div>
        <div style='color:{C["cyan"]};font-size:10px;font-weight:700;letter-spacing:2px;'>
            DEMONSTRAÇÃO DO RESULTADO DO EXERCÍCIO</div>
        <div style='color:{C["text"]};font-size:24px;font-weight:800;margin-top:2px;'>
            Dashboard Executivo 2024</div>
        <div style='color:{C["muted"]};font-size:11px;margin-top:4px;'>
            Filtro ativo: <b style='color:{C["cyan"]};'>{filtro_ativo}</b></div>
    </div>
    <div style='text-align:right;'>
        <div style='color:{C["muted"]};font-size:10px;'>RESULTADO FINAL</div>
        <div style='color:{ml_cor};font-size:26px;font-weight:800;'>{fmt_M(dre["ll"])}</div>
        <div style='color:{ml_cor};font-size:12px;font-weight:700;'>Margem {dre["mg_liq"]:.1f}%</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── KPIs ────────────────────────────────────────────────────────────────────
k1,k2,k3,k4,k5,k6,k7,k8 = st.columns(8)
kpis = [
    (k1, "💰 Receita Bruta",    fmt_M(dre["rb"]),   C["blue"],   ""),
    (k2, "📉 Deduções",         fmt_M(dre["ded"]),  C["red"],    f"carga {dre['taxa_ded']:.1f}%"),
    (k3, "📊 Receita Líquida",  fmt_M(dre["rl"]),   C["cyan"],   ""),
    (k4, "📦 Custo Direto",     fmt_M(-dre["custo_direto"]), C["orange"], f"{(dre['custo_direto']/dre['rl']*100) if dre['rl'] else 0:.1f}% da RL"),
    (k5, "📈 Lucro Bruto",      fmt_M(dre["lb"]),   C["green"] if dre["lb"]>=0 else C["red"],   f"marg. {dre['mg_bruta']:.1f}%"),
    (k6, "⚡ EBIT",             fmt_M(dre["ebit"]), C["yellow"] if dre["ebit"]>=0 else C["red"], f"marg. {dre['mg_ebit']:.1f}%"),
    (k7, "🏆 Lucro Líquido",    fmt_M(dre["ll"]),   C["green"] if dre["ll"]>=0 else C["red"],   f"marg. {dre['mg_liq']:.1f}%"),
    (k8, "💳 Res. Financeiro",  fmt_M(dre["res_fin"]), C["green"] if dre["res_fin"]>=0 else C["red"], ""),
]
for col, lbl, val, cor, sub in kpis:
    with col:
        st.markdown(kpi_html(lbl, val, cor, sub), unsafe_allow_html=True)

st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)

# ─── TABS ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Visão Executiva",
    "📈 Análise Comercial",
    "💰 Gestão de Custos",
    "🏢 Performance Regional",
    "🎯 Insights Estratégicos",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — VISÃO EXECUTIVA
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_wf, col_ev = st.columns([1, 1.7])

    with col_wf:
        sec("Cascata DRE — Composição do Resultado")
        wf_labels = ["Rec.\nBruta","Deduções","Rec.\nLíquida","CMV","CSP",
                     "Lucro\nBruto","Desp.\nCom.","Desp.\nAdm.","EBIT",
                     "Res.\nFin.","Outras","LAIR","Impostos","Lucro\nLíquido"]
        wf_vals   = [dre["rb"],dre["ded"],None,dre["cmv"],dre["csp"],None,
                     dre["dc"],dre["da"],None,dre["res_fin"],dre["out"],None,dre["imp"],None]
        wf_meas   = ["absolute","relative","total","relative","relative","total",
                     "relative","relative","total","relative","relative","total","relative","total"]

        fig = go.Figure(go.Waterfall(
            orientation="v", measure=wf_meas, x=wf_labels, y=wf_vals,
            text=[fmt_M(v) if v is not None else "" for v in wf_vals],
            textposition="outside", textfont=dict(size=8, color=C["text"]),
            increasing=dict(marker=dict(color=C["green"], line=dict(width=0))),
            decreasing=dict(marker=dict(color=C["red"],   line=dict(width=0))),
            totals=dict(marker=dict(color=C["blue"],       line=dict(width=0))),
            connector=dict(line=dict(color=C["border"], width=1, dash="dot")),
            customdata=[fmt_M(v) if v else "" for v in wf_vals],
            hovertemplate="<b>%{x}</b><br>Valor: %{customdata}<extra></extra>",
        ))
        fig.update_layout(**chart_base(400), showlegend=False,
                          margin=dict(l=8,r=8,t=30,b=8),
                          xaxis=xax(tickfont=dict(size=8)),
                          yaxis=yax(tickformat=",.0f"))
        st.plotly_chart(fig, use_container_width=True)

    with col_ev:
        sec("Evolução Mensal — Receita · Custos · Lucro Líquido")
        rows = []
        for m in meses:
            d = _dre(dff[dff["mes_ano"]==m])
            rows.append(dict(mes=m, RB=d["rb"], Custo=-d["custo_direto"],
                             DespOp=-d["desp_op"], LL=d["ll"],
                             MargLiq=d["mg_liq"]))
        ev = pd.DataFrame(rows)

        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Bar(x=ev["mes"], y=ev["RB"], name="Receita Bruta",
            marker_color=C["blue"], opacity=0.85,
            hovertemplate="<b>%{x}</b><br>Receita Bruta: R$ %{y:,.0f}<extra></extra>"),
            secondary_y=False)
        fig.add_trace(go.Bar(x=ev["mes"], y=ev["Custo"], name="Custo Direto",
            marker_color=C["red"], opacity=0.85,
            hovertemplate="<b>%{x}</b><br>Custo Direto: R$ %{y:,.0f}<extra></extra>"),
            secondary_y=False)
        fig.add_trace(go.Bar(x=ev["mes"], y=ev["DespOp"], name="Desp. Operacionais",
            marker_color=C["yellow"], opacity=0.8,
            hovertemplate="<b>%{x}</b><br>Desp. Operacionais: R$ %{y:,.0f}<extra></extra>"),
            secondary_y=False)
        fig.add_trace(go.Scatter(x=ev["mes"], y=ev["LL"], name="Lucro Líquido",
            mode="lines+markers", line=dict(color=C["green"], width=2.5, shape="spline"),
            marker=dict(size=7, color=C["green"], line=dict(width=2, color=C["bg"])),
            hovertemplate="<b>%{x}</b><br>Lucro Líquido: R$ %{y:,.0f}<br>Margem: %{customdata:.1f}%<extra></extra>",
            customdata=ev["MargLiq"]),
            secondary_y=True)
        fig.update_layout(**chart_base(400), barmode="relative",
                          margin=dict(l=8,r=40,t=30,b=50),
                          xaxis=xax(tickangle=-45, tickfont=dict(size=9)),
                          yaxis=yax(tickformat=",.0f"),
                          yaxis2=dict(showgrid=False, tickformat=".1f",
                                      ticksuffix="%", tickfont=dict(color=C["green"], size=9)))
        st.plotly_chart(fig, use_container_width=True)

    col_mg, col_gauge = st.columns([1.5, 1])

    with col_mg:
        sec("Evolução de Margens (%) — Bruta · EBIT · Líquida")
        mg_rows = []
        for m in meses:
            d = _dre(dff[dff["mes_ano"]==m])
            mg_rows.append(dict(mes=m, Bruta=d["mg_bruta"], EBIT=d["mg_ebit"], Líquida=d["mg_liq"]))
        mg = pd.DataFrame(mg_rows)

        fig = go.Figure()
        for col_nm, cor, fill in [
            ("Bruta",   C["blue"],   "rgba(33,150,243,0.08)"),
            ("EBIT",    C["yellow"], "rgba(255,215,64,0.08)"),
            ("Líquida", C["green"],  "rgba(0,230,118,0.08)"),
        ]:
            fig.add_trace(go.Scatter(
                x=mg["mes"], y=mg[col_nm], name=f"Mg. {col_nm}",
                mode="lines+markers", fill="tozeroy", fillcolor=fill,
                line=dict(color=cor, width=2.2, shape="spline"),
                marker=dict(size=6, color=cor, line=dict(width=2, color=C["bg"])),
                hovertemplate=f"<b>%{{x}}</b><br>Margem {col_nm}: %{{y:.1f}}%<extra></extra>",
            ))
        fig.update_layout(**chart_base(300), margin=dict(l=8,r=8,t=30,b=50),
                          xaxis=xax(tickangle=-45, tickfont=dict(size=9)),
                          yaxis=yax(ticksuffix="%"))
        st.plotly_chart(fig, use_container_width=True)

    with col_gauge:
        sec("Indicadores de Saúde — Benchmarks de Margem")
        fig = make_subplots(rows=1, cols=3,
                            specs=[[{"type":"indicator"},{"type":"indicator"},{"type":"indicator"}]])
        benchmarks = [
            ("Mg. Bruta", dre["mg_bruta"], 50),
            ("Mg. EBIT",  dre["mg_ebit"],  20),
            ("Mg. Líq.",  dre["mg_liq"],   12),
        ]
        for i, (lbl, val, ref) in enumerate(benchmarks, 1):
            cor = C["green"] if val >= ref else C["yellow"] if val >= ref*0.7 else C["red"]
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=val,
                title=dict(text=lbl, font=dict(color=C["muted"], size=11)),
                number=dict(suffix="%", font=dict(color=cor, size=18)),
                gauge=dict(
                    axis=dict(range=[-10, max(ref*1.5, val*1.2)],
                              tickcolor=C["muted"], tickfont=dict(size=8)),
                    bar=dict(color=cor, thickness=0.6),
                    bgcolor=C["card2"],
                    borderwidth=0,
                    steps=[
                        dict(range=[-10, ref*0.7], color="rgba(255,82,82,0.12)"),
                        dict(range=[ref*0.7, ref],  color="rgba(255,215,64,0.12)"),
                        dict(range=[ref, max(ref*1.5, val*1.2)], color="rgba(0,230,118,0.12)"),
                    ],
                    threshold=dict(line=dict(color=C["text"], width=2),
                                   thickness=0.8, value=ref),
                ),
            ), row=1, col=i)
        fig.update_layout(**chart_base(300), margin=dict(l=8,r=8,t=30,b=8))
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ANÁLISE COMERCIAL
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    col_a, col_b, col_c = st.columns([1, 1, 1])

    with col_a:
        sec("Mix de Receita por Categoria")
        cat_df = (dff[dff["grupo_dre"]=="Receita Bruta"]
                  .groupby("categoria_produto")["valor"].sum()
                  .reset_index().dropna())
        cat_df.columns = ["Categoria","Receita"]
        cat_df["Pct"] = cat_df["Receita"] / cat_df["Receita"].sum() * 100

        fig = go.Figure(go.Pie(
            labels=cat_df["Categoria"], values=cat_df["Receita"], hole=0.6,
            marker=dict(colors=[C["blue"],C["cyan"],C["green"]], line=dict(color=C["bg"],width=3)),
            customdata=cat_df[["Pct","Receita"]].values,
            hovertemplate="<b>%{label}</b><br>Receita: R$ %{customdata[1]:,.0f}<br>Participação: %{customdata[0]:.1f}%<extra></extra>",
            textinfo="label+percent", textfont=dict(size=11, color=C["text"]),
        ))
        fig.update_layout(**chart_base(300), showlegend=False,
                          margin=dict(l=8,r=8,t=8,b=8),
                          annotations=[dict(text=fmt_M(cat_df["Receita"].sum()),
                                            x=0.5,y=0.5,showarrow=False,
                                            font=dict(size=13,color=C["text"]))])
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        sec("Top 10 Contas de Receita")
        top_rec = (dff[dff["natureza"]=="Receita"]
                   .groupby("conta_contabil")["valor"].sum()
                   .reset_index().sort_values("valor", ascending=True).tail(10))
        fig = go.Figure(go.Bar(
            x=top_rec["valor"], y=top_rec["conta_contabil"], orientation="h",
            marker=dict(color=top_rec["valor"],
                        colorscale=[[0,C["accent"]],[1,C["cyan"]]],showscale=False),
            text=[fmt_M(v) for v in top_rec["valor"]],
            textposition="outside", textfont=dict(size=9),
            hovertemplate="<b>%{y}</b><br>Receita: R$ %{x:,.0f}<extra></extra>",
        ))
        fig.update_layout(**chart_base(300), showlegend=False,
                          margin=dict(l=8,r=70,t=8,b=8),
                          xaxis=xax(tickformat=",.0f"), yaxis=yax(tickfont=dict(size=9)))
        st.plotly_chart(fig, use_container_width=True)

    with col_c:
        sec("Receita por Trimestre e Categoria")
        tri_cat = (dff[dff["grupo_dre"]=="Receita Bruta"]
                   .groupby(["trimestre","categoria_produto"])["valor"].sum()
                   .reset_index().dropna())
        fig = go.Figure()
        for i, cat in enumerate(tri_cat["categoria_produto"].unique()):
            d = tri_cat[tri_cat["categoria_produto"]==cat]
            fig.add_trace(go.Bar(
                x=d["trimestre"], y=d["valor"], name=cat,
                marker_color=PALETA[i], opacity=0.87,
                hovertemplate=f"<b>{cat}</b><br>%{{x}}: R$ %{{y:,.0f}}<extra></extra>",
            ))
        fig.update_layout(**chart_base(300), barmode="group",
                          margin=dict(l=8,r=8,t=30,b=16),
                          xaxis=xax(), yaxis=yax(tickformat=",.0f"))
        st.plotly_chart(fig, use_container_width=True)

    col_d, col_e = st.columns([1.5, 1])

    with col_d:
        sec("Evolução do Mix de Receita — Área Empilhada por Categoria")
        mix = (dff[dff["grupo_dre"]=="Receita Bruta"]
               .groupby(["mes_ano","categoria_produto"])["valor"].sum()
               .reset_index().dropna())
        fig = go.Figure()
        cats = mix["categoria_produto"].unique()
        for i, cat in enumerate(cats):
            d = mix[mix["categoria_produto"]==cat].sort_values("mes_ano")
            fig.add_trace(go.Scatter(
                x=d["mes_ano"], y=d["valor"], name=cat,
                stackgroup="one", mode="lines",
                line=dict(color=PALETA[i], width=1),
                fillcolor=PALETA_FILL[i],
                hovertemplate=f"<b>{cat}</b><br>%{{x}}: R$ %{{y:,.0f}}<extra></extra>",
            ))
        fig.update_layout(**chart_base(300), margin=dict(l=8,r=8,t=30,b=50),
                          xaxis=xax(tickangle=-45, tickfont=dict(size=9)),
                          yaxis=yax(tickformat=",.0f"))
        st.plotly_chart(fig, use_container_width=True)

    with col_e:
        sec("Receita por Produto — Top 10")
        top_prod = (dff[dff["grupo_dre"]=="Receita Bruta"]
                    .groupby("produto_nome")["valor"].sum()
                    .dropna().reset_index()
                    .sort_values("valor", ascending=False).head(10))
        fig = go.Figure(go.Bar(
            x=top_prod["produto_nome"], y=top_prod["valor"],
            marker=dict(color=PALETA[:len(top_prod)]),
            text=[fmt_M(v) for v in top_prod["valor"]],
            textposition="outside", textfont=dict(size=9),
            hovertemplate="<b>%{x}</b><br>Receita: R$ %{y:,.0f}<extra></extra>",
        ))
        fig.update_layout(**chart_base(300), showlegend=False,
                          margin=dict(l=8,r=8,t=30,b=60),
                          xaxis=xax(tickangle=-30, tickfont=dict(size=9)),
                          yaxis=yax(tickformat=",.0f"))
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — GESTÃO DE CUSTOS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    col_a, col_b = st.columns([1.2, 1])

    with col_a:
        sec("Pareto de Despesas — Análise 80/20")
        desp_grupos = ["CMV","CSP","Despesas Administrativas","Despesas Comerciais",
                       "Despesas Financeiras","Outras Despesas"]
        pareto = (dff[dff["grupo_dre"].isin(desp_grupos)]
                  .groupby("conta_contabil")["valor"].sum()
                  .abs().reset_index()
                  .sort_values("valor", ascending=False).head(15))
        pareto["cumsum_pct"] = pareto["valor"].cumsum() / pareto["valor"].sum() * 100

        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Bar(
            x=pareto["conta_contabil"], y=pareto["valor"],
            name="Valor", marker_color=C["red"], opacity=0.85,
            hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.0f}<extra></extra>",
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=pareto["conta_contabil"], y=pareto["cumsum_pct"],
            name="% Acumulado", mode="lines+markers",
            line=dict(color=C["yellow"], width=2.5),
            marker=dict(size=6, color=C["yellow"]),
            hovertemplate="<b>%{x}</b><br>% Acumulado: %{y:.1f}%<extra></extra>",
        ), secondary_y=True)
        fig.add_hline(y=80, line_dash="dash", line_color=C["orange"],
                      annotation_text="80%", annotation_font_color=C["orange"],
                      secondary_y=True)
        fig.update_layout(**chart_base(350), barmode="group",
                          margin=dict(l=8,r=40,t=30,b=70),
                          xaxis=xax(tickangle=-35, tickfont=dict(size=8)),
                          yaxis=yax(tickformat=",.0f"),
                          yaxis2=dict(showgrid=False, ticksuffix="%",
                                      tickfont=dict(color=C["yellow"],size=9),
                                      range=[0,110]))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        sec("Composição dos Custos Diretos")
        custos_child = (dff[dff["grupo_dre"].isin(["CMV","CSP"])]
                        .groupby(["grupo_dre","conta_contabil"])["valor"].sum()
                        .abs().reset_index())
        custos_parent = custos_child.groupby("grupo_dre")["valor"].sum().reset_index()

        t_labels  = custos_parent["grupo_dre"].tolist() + custos_child["conta_contabil"].tolist()
        t_parents = [""] * len(custos_parent) + custos_child["grupo_dre"].tolist()
        t_values  = custos_parent["valor"].tolist() + custos_child["valor"].tolist()
        t_fmt     = [fmt_M(v) for v in t_values]

        fig = go.Figure(go.Treemap(
            labels=t_labels, parents=t_parents, values=t_values,
            customdata=t_fmt,
            texttemplate="<b>%{label}</b><br>%{customdata}",
            marker=dict(
                colorscale=[[0,C["accent"]],[1,C["red"]]],
                line=dict(width=1, color=C["bg"]),
            ),
            hovertemplate="<b>%{label}</b><br>Valor: %{customdata}<br>%{percentParent:.1%} do grupo<extra></extra>",
        ))
        fig.update_layout(**chart_base(350), margin=dict(l=8,r=8,t=30,b=8))
        st.plotly_chart(fig, use_container_width=True)

    col_c, col_d, col_e = st.columns(3)

    with col_c:
        sec("Despesas por Centro de Custo")
        cc = (dff[dff["natureza"]=="Despesa"]
              .groupby("centro_custo")["valor"].sum()
              .abs().reset_index().sort_values("valor", ascending=True))
        fig = go.Figure(go.Bar(
            x=cc["valor"], y=cc["centro_custo"], orientation="h",
            marker=dict(color=cc["valor"],
                        colorscale=[[0,C["blue"]],[1,C["red"]]],showscale=False),
            text=[fmt_M(v) for v in cc["valor"]],
            textposition="outside", textfont=dict(size=9),
            hovertemplate="<b>%{y}</b><br>Total despesas: R$ %{x:,.0f}<extra></extra>",
        ))
        fig.update_layout(**chart_base(300), showlegend=False,
                          margin=dict(l=8,r=70,t=8,b=8),
                          xaxis=xax(tickformat=",.0f"), yaxis=yax(tickfont=dict(size=10)))
        st.plotly_chart(fig, use_container_width=True)

    with col_d:
        sec("Deduções — Breakdown Tributário")
        ded_df = (dff[dff["grupo_dre"]=="Deduções"]
                  .groupby("conta_contabil")["valor"].sum()
                  .abs().reset_index().sort_values("valor", ascending=False))
        fig = go.Figure(go.Pie(
            labels=ded_df["conta_contabil"], values=ded_df["valor"], hole=0.5,
            marker=dict(colors=[C["red"],C["orange"],C["yellow"],C["purple"]],
                        line=dict(color=C["bg"],width=2)),
            textinfo="label+percent", textfont=dict(size=10),
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f}<br>%{percent}<extra></extra>",
        ))
        fig.update_layout(**chart_base(300), showlegend=False,
                          margin=dict(l=8,r=8,t=8,b=8),
                          annotations=[dict(text=fmt_M(ded_df["valor"].sum()),
                                            x=0.5,y=0.5,showarrow=False,
                                            font=dict(size=12,color=C["red"]))])
        st.plotly_chart(fig, use_container_width=True)

    with col_e:
        sec("Evolução Mensal dos Custos Diretos")
        ev_custo = []
        for m in meses:
            dm = dff[dff["mes_ano"]==m]
            cmv_m = dm[dm["grupo_dre"]=="CMV"]["valor"].sum()
            csp_m = dm[dm["grupo_dre"]=="CSP"]["valor"].sum()
            ev_custo.append(dict(mes=m, CMV=abs(cmv_m), CSP=abs(csp_m)))
        ev_c = pd.DataFrame(ev_custo)
        fig = go.Figure()
        for grp, cor in [("CMV", C["orange"]), ("CSP", C["red"])]:
            fig.add_trace(go.Scatter(
                x=ev_c["mes"], y=ev_c[grp], name=grp,
                mode="lines+markers", fill="tozeroy",
                fillcolor="rgba(255,82,82,0.08)" if grp=="CSP" else "rgba(255,152,0,0.08)",
                line=dict(color=cor, width=2, shape="spline"),
                marker=dict(size=5, color=cor),
                hovertemplate=f"<b>{grp}</b><br>%{{x}}: R$ %{{y:,.0f}}<extra></extra>",
            ))
        fig.update_layout(**chart_base(300), margin=dict(l=8,r=8,t=8,b=50),
                          xaxis=xax(tickangle=-45, tickfont=dict(size=8)),
                          yaxis=yax(tickformat=",.0f"))
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PERFORMANCE REGIONAL
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    col_a, col_b = st.columns([1, 1.2])

    with col_a:
        sec("Resultado por Região — Receita Líquida · Lucro Bruto · Lucro Líquido")
        reg_rows = []
        for r in dff["regiao"].unique():
            d = _dre(dff[dff["regiao"]==r])
            reg_rows.append(dict(Região=r, RL=d["rl"], LB=d["lb"], LL=d["ll"],
                                 MgLiq=d["mg_liq"], MgBruta=d["mg_bruta"]))
        reg_df = pd.DataFrame(reg_rows).sort_values("RL")

        fig = go.Figure()
        for col_nm, cor, lbl in [("RL",C["blue"],"Rec. Líquida"),
                                   ("LB",C["cyan"],"Lucro Bruto"),
                                   ("LL",C["green"],"Lucro Líquido")]:
            fig.add_trace(go.Bar(
                y=reg_df["Região"], x=reg_df[col_nm], name=lbl,
                orientation="h", marker_color=cor, opacity=0.87,
                text=[fmt_M(v) for v in reg_df[col_nm]],
                textposition="outside", textfont=dict(size=9),
                hovertemplate=f"<b>%{{y}}</b><br>{lbl}: R$ %{{x:,.0f}}<extra></extra>",
            ))
        fig.update_layout(**chart_base(320), barmode="group",
                          margin=dict(l=8,r=80,t=30,b=8),
                          xaxis=xax(tickformat=",.0f"), yaxis=yax())
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        sec("Treemap — Receita por Região e Filial")
        tree_fil = (dff[dff["grupo_dre"]=="Receita Bruta"]
                    .groupby(["regiao","filial_nome"])["valor"].sum().reset_index())
        tree_fil["filial_short"] = (tree_fil["filial_nome"]
                                    .str.replace("Filial ","").str.replace("Matriz ","★ "))
        tree_reg = tree_fil.groupby("regiao")["valor"].sum().reset_index()

        t_labels  = tree_reg["regiao"].tolist() + tree_fil["filial_short"].tolist()
        t_parents = [""] * len(tree_reg) + tree_fil["regiao"].tolist()
        t_values  = tree_reg["valor"].tolist() + tree_fil["valor"].tolist()
        t_fmt     = [fmt_M(v) for v in t_values]

        fig = go.Figure(go.Treemap(
            labels=t_labels, parents=t_parents, values=t_values,
            customdata=t_fmt,
            texttemplate="<b>%{label}</b><br>%{customdata}",
            marker=dict(
                colorscale=[[0,C["card2"]],[0.5,C["accent"]],[1,C["cyan"]]],
                line=dict(width=2, color=C["bg"]),
            ),
            hovertemplate="<b>%{label}</b><br>Receita: %{customdata}<br>%{percentParent:.1%} da região<extra></extra>",
        ))
        fig.update_layout(**chart_base(320), margin=dict(l=8,r=8,t=30,b=8))
        st.plotly_chart(fig, use_container_width=True)

    col_c, col_d = st.columns([1.4, 1])

    with col_c:
        sec("Performance por Filial — Comparativo Completo")
        fil_rows = []
        for f in dff["filial_nome"].unique():
            d = _dre(dff[dff["filial_nome"]==f])
            nome = f.replace("Filial ","").replace("Matriz ","★ ")
            fil_rows.append(dict(Filial=nome, RL=d["rl"], LB=d["lb"], LL=d["ll"],
                                 MgLiq=d["mg_liq"]))
        fil_df = pd.DataFrame(fil_rows).sort_values("RL", ascending=True)

        fig = go.Figure()
        for col_nm, cor, lbl in [("RL",C["blue"],"Rec. Líquida"),
                                   ("LB",C["cyan"],"Lucro Bruto"),
                                   ("LL",C["green"],"Lucro Líquido")]:
            fig.add_trace(go.Bar(
                y=fil_df["Filial"], x=fil_df[col_nm], name=lbl,
                orientation="h", marker_color=cor, opacity=0.87,
                text=[fmt_M(v) for v in fil_df[col_nm]],
                textposition="outside", textfont=dict(size=9),
                hovertemplate=f"<b>%{{y}}</b><br>{lbl}: R$ %{{x:,.0f}}<extra></extra>",
            ))
        fig.update_layout(**chart_base(380), barmode="group",
                          margin=dict(l=8,r=90,t=30,b=8),
                          xaxis=xax(tickformat=",.0f"), yaxis=yax())
        st.plotly_chart(fig, use_container_width=True)

    with col_d:
        sec("Ranking de Margem Líquida por Filial")
        fil_df_sorted = fil_df.sort_values("MgLiq", ascending=True)
        cores = [C["red"] if v < 0 else C["yellow"] if v < 8 else C["green"]
                 for v in fil_df_sorted["MgLiq"]]
        fig = go.Figure(go.Bar(
            x=fil_df_sorted["MgLiq"], y=fil_df_sorted["Filial"],
            orientation="h", marker_color=cores,
            text=[f"{v:.1f}%" for v in fil_df_sorted["MgLiq"]],
            textposition="outside", textfont=dict(size=10),
            hovertemplate="<b>%{y}</b><br>Margem Líquida: %{x:.1f}%<extra></extra>",
        ))
        fig.add_vline(x=0, line_color=C["border"], line_width=1)
        fig.update_layout(**chart_base(380), showlegend=False,
                          margin=dict(l=8,r=60,t=30,b=8),
                          xaxis=xax(ticksuffix="%"), yaxis=yax())
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — INSIGHTS ESTRATÉGICOS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    col_ins, col_dre = st.columns([1, 1.1])

    with col_ins:
        # ── Alertas executivos ─────────────────────────────────────────────
        sec("🚨 Alertas Executivos")

        alertas = []
        if dre["mg_liq"] < 0:
            alertas.append(("CRÍTICO", C["red"],
                "Resultado negativo", f"Lucro Líquido de {fmt_M(dre['ll'])}. Empresa operando em prejuízo. Revisão imediata da estrutura de custos e precificação."))
        elif dre["mg_liq"] < 5:
            alertas.append(("ATENÇÃO", C["orange"],
                "Margem líquida baixa", f"Margem de {dre['mg_liq']:.1f}% abaixo do mínimo recomendado (5%). Risco de operação no limite."))

        if dre["taxa_ded"] > 20:
            alertas.append(("ATENÇÃO", C["yellow"],
                "Carga tributária elevada", f"Deduções representam {dre['taxa_ded']:.1f}% da Receita Bruta ({fmt_M(abs(dre['ded']))}). Avaliar planejamento tributário."))

        if dre["res_fin"] < -dre["rl"] * 0.05:
            alertas.append(("ATENÇÃO", C["orange"],
                "Resultado financeiro negativo", f"Despesas financeiras líquidas de {fmt_M(abs(dre['res_fin']))} impactando resultado. Reestruturar passivo."))

        custo_pct = (dre["custo_direto"] / dre["rl"] * 100) if dre["rl"] else 0
        if custo_pct > 60:
            alertas.append(("ATENÇÃO", C["yellow"],
                "Custo direto alto", f"CMV + CSP = {custo_pct:.1f}% da Receita Líquida. Margem bruta comprimida."))

        # filial com margem negativa
        fil_neg = [f.replace("Filial ","") for f in dff["filial_nome"].unique()
                   if _dre(dff[dff["filial_nome"]==f])["mg_liq"] < 0]
        if fil_neg:
            alertas.append(("ATENÇÃO", C["orange"],
                f"Filial(is) com prejuízo", f"{', '.join(fil_neg)} apresentam margem líquida negativa. Intervenção necessária."))

        if not alertas:
            st.markdown(f"""
            <div style='background:{C["card2"]};border-left:3px solid {C["green"]};
                 border-radius:8px;padding:14px;margin-bottom:10px;'>
                <div style='color:{C["green"]};font-weight:700;font-size:13px;'>
                    ✅ Nenhum alerta crítico</div>
                <div style='color:{C["muted"]};font-size:11px;margin-top:4px;'>
                    Todos os indicadores dentro dos parâmetros aceitáveis.</div>
            </div>""", unsafe_allow_html=True)
        else:
            for nivel, cor, titulo, texto in alertas:
                st.markdown(f"""
                <div class="alert-card" style='background:{C["card2"]};border-left:3px solid {cor};'>
                    <div style='display:flex;align-items:center;gap:8px;margin-bottom:4px;'>
                        <span class="badge" style='background:{cor}20;color:{cor};'>{nivel}</span>
                        <span style='color:{cor};font-size:12px;font-weight:700;'>{titulo}</span>
                    </div>
                    <div style='color:{C["muted"]};font-size:11px;line-height:1.5;'>{texto}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)

        # ── Insights estratégicos ──────────────────────────────────────────
        sec("💡 Insights para Tomada de Decisão")

        ml  = dre["mg_liq"]
        mb  = dre["mg_bruta"]
        me  = dre["mg_ebit"]

        top_filial = max(dff["filial_nome"].unique(),
                         key=lambda f: _dre(dff[dff["filial_nome"]==f])["lb"])
        bot_filial = min(dff["filial_nome"].unique(),
                         key=lambda f: _dre(dff[dff["filial_nome"]==f])["mg_liq"])
        top_reg    = max(dff["regiao"].unique(),
                         key=lambda r: _dre(dff[dff["regiao"]==r])["rl"])

        cat_lider  = (dff[dff["grupo_dre"]=="Receita Bruta"]
                      .groupby("categoria_produto")["valor"].sum()
                      .dropna().idxmax()) if len(dff) else "N/D"

        saude = ("Excelente",C["green"]) if ml>=15 else \
                ("Saudável", C["cyan"])  if ml>=8  else \
                ("Atenção",  C["yellow"])if ml>=3  else \
                ("Crítica",  C["red"])

        insights = [
            ("📊 Saúde Financeira", saude[1],
             f"Classificação <b>{saude[0]}</b>. Margem Líquida de <b>{ml:.1f}%</b> sobre Receita Líquida de <b>{fmt_M(dre['rl'])}</b>. "
             f"Margem Bruta em <b>{mb:.1f}%</b> indica {'boa eficiência produtiva.' if mb>40 else 'pressão nos custos diretos — revisar precificação.'}"),

            ("🏛️ Gestão Tributária", C["yellow"],
             f"Carga de deduções em <b>{dre['taxa_ded']:.1f}%</b> da Receita Bruta ({fmt_M(abs(dre['ded']))}). "
             f"{'Recomenda-se análise de regime tributário e aproveitamento de créditos fiscais.' if dre['taxa_ded']>18 else 'Carga tributária dentro do esperado para o setor.'}"),

            ("⚙️ Eficiência Operacional", C["blue"],
             f"EBIT de <b>{fmt_M(dre['ebit'])}</b> (margem <b>{me:.1f}%</b>). "
             f"Despesas operacionais de <b>{fmt_M(dre['desp_op'])}</b> representam "
             f"<b>{(dre['desp_op']/dre['rl']*100) if dre['rl'] else 0:.1f}%</b> da Receita Líquida. "
             f"{'Estrutura de custos fixos elevada — avaliar otimização.' if dre['desp_op']/dre['rl']>0.3 and dre['rl'] else 'Opex controlado.'}"),

            (f"🗺️ Destaque Estratégico", C["cyan"],
             f"Região <b>{top_reg}</b> lidera em Receita Líquida. "
             f"Melhor filial por Lucro Bruto: <b>{top_filial.replace('Filial ','').replace('Matriz ','')}</b>. "
             f"Categoria <b>{cat_lider}</b> é a principal geradora de receita. "
             f"Replicar o modelo comercial das unidades de destaque nas demais."),

            ("💳 Resultado Financeiro", C["red"] if dre["res_fin"]<0 else C["green"],
             f"Resultado financeiro líquido de <b>{fmt_M(dre['res_fin'])}</b>. "
             f"{'Despesas financeiras relevantes — priorizar amortização de dívida e renegociação de taxas.' if dre['res_fin']<-1_000_000 else 'Exposição financeira sob controle.'}"),

            ("🎯 Recomendação CEO/CFO", C["green"] if ml>=8 else C["yellow"],
             f"{'Manter trajetória atual com foco em crescimento de receita e controle de inadimplência.' if ml>=10 else 'Priorizar: (1) revisão de precificação, (2) renegociação de custos fixos, (3) aceleração de receita em categorias com maior margem.'} "
             f"Resultado do período: <b>{fmt_M(dre['ll'])}</b>."),
        ]

        for titulo, cor, texto in insights:
            st.markdown(f"""
            <div class="insight-card" style='border-left:3px solid {cor};'>
                <div class="insight-title" style='color:{cor};'>{titulo}</div>
                <div class="insight-body">{texto}</div>
            </div>""", unsafe_allow_html=True)

    with col_dre:
        sec("📋 DRE Estruturada — Demonstração Completa")

        rl = dre["rl"]
        linhas = [
            ("RECEITA BRUTA",                   dre["rb"],       "header"),
            ("&nbsp;&nbsp;Deduções s/ Venda",    dre["ded"],      "item"),
            ("RECEITA LÍQUIDA",                  dre["rl"],       "total"),
            ("&nbsp;&nbsp;CMV",                  dre["cmv"],      "item"),
            ("&nbsp;&nbsp;CSP",                  dre["csp"],      "item"),
            ("LUCRO BRUTO",                      dre["lb"],       "total"),
            ("&nbsp;&nbsp;&nbsp;Margem Bruta",   dre["mg_bruta"], "pct"),
            ("&nbsp;&nbsp;Despesas Comerciais",  dre["dc"],       "item"),
            ("&nbsp;&nbsp;Despesas Adm.",         dre["da"],       "item"),
            ("EBIT",                             dre["ebit"],     "total"),
            ("&nbsp;&nbsp;&nbsp;Margem EBIT",    dre["mg_ebit"],  "pct"),
            ("&nbsp;&nbsp;Resultado Financeiro", dre["res_fin"],  "item"),
            ("&nbsp;&nbsp;Outras Rec./Desp.",    dre["out"],      "item"),
            ("LAIR",                             dre["lair"],     "total"),
            ("&nbsp;&nbsp;Impostos s/ Lucro",    dre["imp"],      "item"),
            ("LUCRO LÍQUIDO",                    dre["ll"],       "final"),
            ("&nbsp;&nbsp;&nbsp;Margem Líquida", dre["mg_liq"],   "pct"),
        ]

        rows_html = ""
        for nome, val, tipo in linhas:
            cor_val = C["green"] if val >= 0 else C["red"]
            if tipo == "pct":
                v_fmt = f"{val:.1f}%"
                bg, fw = C["card2"], "400"
            elif tipo == "final":
                v_fmt, bg, fw = fmt_M(val), "#0a2a4a", "800"
            elif tipo == "total":
                v_fmt, bg, fw = fmt_M(val), "#112244", "700"
            elif tipo == "header":
                v_fmt, bg, fw = fmt_M(val), "#0a1929", "700"
                cor_val = C["cyan"]
            else:
                v_fmt, bg, fw = fmt_M(val), C["card"], "400"
                cor_val = C["green"] if val >= 0 else C["red"]

            pct_rl = f"&nbsp;<span style='color:{C['muted']};font-size:10px;'>({val/rl*100:.1f}%)</span>" \
                     if tipo not in ("pct","header") and rl and tipo != "final" else ""

            rows_html += f"""
            <tr>
                <td style='background:{bg};font-weight:{fw};color:{C["text"] if tipo!="item" else C["muted"]};
                    padding:7px 12px;border-bottom:1px solid {C["grid"]};'>{nome}</td>
                <td style='background:{bg};font-weight:{fw};color:{cor_val};text-align:right;
                    padding:7px 12px;border-bottom:1px solid {C["grid"]};'>{v_fmt}{pct_rl}</td>
            </tr>"""

        st.markdown(f"""
        <table class="dre-table">
            <thead>
                <tr style='background:#0a1929;border-bottom:2px solid {C["accent"]};'>
                    <th style='padding:8px 12px;color:{C["cyan"]};font-size:11px;text-align:left;'>Conta</th>
                    <th style='padding:8px 12px;color:{C["cyan"]};font-size:11px;text-align:right;'>Valor · % RL</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
        """, unsafe_allow_html=True)

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='text-align:center;padding:20px;margin-top:20px;
     border-top:1px solid {C["border"]};color:{C["muted"]};font-size:11px;'>
    DRE Executivo 2024 · Powered by <b>Streamlit + Plotly</b> ·
    {len(dff):,} lançamentos filtrados de {len(df):,} total ·
    <a href="https://www.linkedin.com/in/breno-teodomiro-power-bi/"
       target="_blank" style='color:{C["cyan"]};text-decoration:none;'>LinkedIn</a> ·
    <a href="https://github.com/Breno-Teodomiro"
       target="_blank" style='color:{C["cyan"]};text-decoration:none;'>GitHub</a>
</div>
""", unsafe_allow_html=True)
