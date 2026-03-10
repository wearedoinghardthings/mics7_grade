# ═══════════════════════════════════════════════════════════════════════════
#  AgentTracker PRO — Application Streamlit complète
#  Installation  : pip install streamlit pandas plotly openpyxl numpy
#  Lancement     : streamlit run streamlit_app.py
# ═══════════════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

st.set_page_config(page_title="AgentTracker PRO", page_icon="🎯",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background:#070b13; }
  [data-testid="stSidebar"]          { background:#0d1421; }
  h1,h2,h3,h4                        { color:#FFD93D !important; }
  .stTabs [data-baseweb="tab"]        { color:#888; font-weight:700; }
  .stTabs [aria-selected="true"]      { color:#FFD93D !important;
                                        border-bottom:2px solid #FFD93D; }
  div[data-testid="metric-container"] {
      background:rgba(255,255,255,0.03);
      border:1px solid rgba(255,255,255,0.08);
      border-radius:12px; padding:14px 18px; }
</style>""", unsafe_allow_html=True)

# ── Données par défaut ─────────────────────────────────────────────────────
DEFAULT = {
    "Acka Gustave Boris":              [18,14,15,20,12,19,20,18],
    "Agnero Djadja":                   [18,14,18,13,16,17,20,18],
    "Kra Yao Assouman Aubin Gael":     [17, 6,15,10,16,19,18,19],
    "Kouao Marie-Paule":               [18, 0,14,17,12,19,18,20],
    "Sangaré Aissata":                 [17,11,13,13,14,18,15,15],
    "Kouassi Kangah Akissi Philomène": [13,11,14,10,16,18,18,14],
    "Yao Julienne":                    [16,11,13,10,16,17,13,13],
    "Amankan Adjo Josiane":            [16, 9,15, 0,16,15,17,19],
    "Fouati Edwige":                   [15, 9,14,13,12,18,13,12],
    "Agnehoura Vanessa":               [14, 9,16, 0,14,18,17,17],
    "Djeha Somaud Marthe Abigail":     [14,11, 0,13,14,16,17,17],
    "Gnomblé Christelle":              [15, 6,14,13, 8,19,15, 9],
    "Loua Saty Veronique":             [ 0,14,15,13,12,17,15,12],
    "Coulibaly Lancina Medard":        [14, 6, 9,10,12,17,15,13],
    "Deza Boga Stefan":                [ 0, 6,10,13,12,17,17,16],
    "Beugré Brigitte":                 [10, 9, 0,13,18,15,12,13],
    "Bogui Kacohon Prisca Sandrine":   [ 0, 3,15,10,14,18,18, 0],
    "Touré Madongon Mariam":           [14,11,15,10,12,15, 0, 0],
    "Konan Amenan Grâce-Victoire":     [ 0, 0,11,10,12,14,13, 8],
    "Diarrassouba Madoussou":          [ 0, 0, 0, 0,10,11,10, 3],
}

COLORS = ["#FF6B6B","#FFD93D","#69DB7C","#4DABF7","#FF922B","#CC5DE8",
          "#20C997","#F06595","#74C0FC","#A9E34B","#FF8787","#FFA94D",
          "#63E6BE","#91A7FF","#DA77F2","#748FFC","#F783AC","#C0EB75",
          "#FFD43B","#66D9E8"]

# ── Utilitaires ────────────────────────────────────────────────────────────
def get_mention(avg):
    if avg >= 18: return "🏆 Excellent",  "#69DB7C"
    if avg >= 16: return "⭐ Très Bien",  "#4DABF7"
    if avg >= 14: return "✅ Bien",       "#74C0FC"
    if avg >= 12: return "👍 Assez Bien", "#FFD93D"
    if avg >= 10: return "⚠️ Passable",   "#FF922B"
    return         "❌ Insuffisant",      "#FF6B6B"

def color_note(v):
    if v == 0:  return "#FF6B6B"
    if v >= 18: return "#69DB7C"
    if v >= 16: return "#4DABF7"
    if v >= 14: return "#74C0FC"
    if v >= 12: return "#FFD93D"
    if v >= 10: return "#FF922B"
    return "#FF6B6B"

def calc_slope(arr):
    n = len(arr)
    if n < 2: return 0.0
    x = np.arange(n, dtype=float)
    return round(float(np.polyfit(x, arr, 1)[0]), 3)

def build_df(data, nlabels, seuil):
    records = []
    for i, (name, notes) in enumerate(data.items()):
        n   = np.array(notes, dtype=float)
        av  = round(float(n.mean()), 2)
        men, col = get_mention(av)
        records.append({
            "Agent":       name,
            "Couleur":     COLORS[i % len(COLORS)],
            **{nlabels[j]: int(notes[j]) for j in range(len(notes))},
            "Moyenne":     av,
            "Mediane":     round(float(np.median(n)), 2),
            "Ecart_type":  round(float(np.std(n)), 2),
            "Min":         int(n.min()),
            "Max":         int(n.max()),
            "Zeros":       int((n == 0).sum()),
            "Taux_Reussite": round(float((n >= seuil).mean() * 100), 1),
            "Pente":       calc_slope(notes),
            "Delta":       int(notes[-1]) - int(notes[0]),
            "Mention":     men,
            "MCouleur":    col,
        })
    return pd.DataFrame(records).set_index("Agent")

def dark_fig(fig, height=350):
    fig.update_layout(
        plot_bgcolor="#0d1421", paper_bgcolor="#0d1421",
        font_color="#aaa", height=height,
        legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#aaa"),
        margin=dict(t=48, b=32, l=48, r=16))
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", zeroline=False)
    return fig

def add_refs(fig, seuil, promo, show_s, show_p):
    if show_s:
        fig.add_hline(y=seuil, line_dash="dash",
                      line_color="rgba(255,107,107,0.5)",
                      annotation_text=f"Seuil {seuil}",
                      annotation_font_color="#FF6B6B",
                      annotation_font_size=10)
    if show_p:
        fig.add_hline(y=promo, line_dash="dot",
                      line_color="rgba(255,217,61,0.4)",
                      annotation_text=f"Promo {promo}",
                      annotation_font_color="#FFD93D",
                      annotation_font_size=10)
    return fig

def style_note_col(val):
    """CSS pour colorer une note — sans matplotlib."""
    if not isinstance(val, (int, float)):
        return ""
    return f"color:{color_note(val)}; font-weight:700; font-family:monospace"

def style_avg_col(val):
    if not isinstance(val, (int, float)):
        return ""
    return f"color:{color_note(val)}; font-weight:900; font-family:monospace; font-size:14px"

def style_pente_col(val):
    if not isinstance(val, (int, float)):
        return ""
    c = "#69DB7C" if val > 0 else "#FF6B6B" if val < 0 else "#666"
    return f"color:{c}; font-weight:700"

def style_taux_col(val):
    if not isinstance(val, (int, float)):
        return ""
    c = "#69DB7C" if val >= 80 else "#FFD93D" if val >= 50 else "#FF6B6B"
    return f"color:{c}; font-weight:700"

def export_excel(df_exp, nlabels):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_exp.reset_index()[
            ["Agent"] + nlabels +
            ["Moyenne","Mediane","Ecart_type","Min","Max",
             "Zeros","Taux_Reussite","Pente","Delta","Mention"]
        ].to_excel(writer, sheet_name="Donnees", index=False)
        pd.DataFrame({
            "Epreuve":    nlabels,
            "Moyenne":    [round(df_exp[n].mean(), 2)   for n in nlabels],
            "Mediane":    [round(df_exp[n].median(), 2) for n in nlabels],
            "Ecart_type": [round(df_exp[n].std(), 2)    for n in nlabels],
            "Min":        [int(df_exp[n].min())          for n in nlabels],
            "Max":        [int(df_exp[n].max())          for n in nlabels],
            "Zeros":      [int((df_exp[n] == 0).sum())   for n in nlabels],
        }).to_excel(writer, sheet_name="Stats_Epreuves", index=False)
        df_exp.sort_values("Moyenne", ascending=False).reset_index()[
            ["Agent","Moyenne","Mention","Taux_Reussite","Pente"]
        ].to_excel(writer, sheet_name="Classement", index=False)
    return output.getvalue()

# ══════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🎯 AgentTracker PRO")
    st.markdown("---")
    st.markdown("### 📂 Importer des données")
    uploaded = st.file_uploader("Fichier Excel ou CSV",
                                type=["xlsx","xls","csv"],
                                help="1ère colonne=Noms, colonnes suivantes=notes. Les 0 sont des vraies notes.")
    st.caption("Format : Nom | Note2 | Note3 | … (tabulation ou ;)")
    st.markdown("---")
    st.markdown("### ⚙️ Paramètres")
    seuil      = st.slider("Seuil d'admission", 0, 20, 10, 1)
    show_seuil = st.checkbox("Ligne de seuil", True)
    show_promo = st.checkbox("Ligne moyenne promo", True)
    st.markdown("---")
    st.markdown("### 🔍 Filtres")
    search     = st.text_input("Rechercher un agent", "")
    sort_opt   = st.selectbox("Trier par", [
        "Moyenne ↓","Moyenne ↑","Nom A→Z",
        "Progression ↑","Regression ↓",
        "Taux reussite ↓","Ecart-type ↓","Zeros ↓"])
    filter_men = st.multiselect("Filtrer par mention", [
        "🏆 Excellent","⭐ Très Bien","✅ Bien",
        "👍 Assez Bien","⚠️ Passable","❌ Insuffisant"])

# ══════════════════════════════════════════════════════════════════════════
#  CHARGEMENT
# ══════════════════════════════════════════════════════════════════════════
is_demo     = True
data        = DEFAULT.copy()
note_labels = [f"Note {i+2}" for i in range(8)]

if uploaded is not None:
    try:
        if uploaded.name.endswith(".csv"):
            raw = pd.read_csv(uploaded, sep=None, engine="python", index_col=0)
        else:
            raw = pd.read_excel(uploaded, index_col=0)
        raw         = raw.apply(pd.to_numeric, errors="coerce").fillna(0).astype(int)
        note_labels = [f"Note {i+2}" for i in range(raw.shape[1])]
        raw.columns = note_labels
        data        = {row: list(raw.loc[row]) for row in raw.index}
        is_demo     = False
        st.sidebar.success(f"✅ {len(data)} agents · {len(note_labels)} épreuves")
    except Exception as e:
        st.sidebar.error(f"⚠️ Erreur : {e}")

df = build_df(data, note_labels, seuil)

# ── Tri & filtres ──────────────────────────────────────────────────────────
df_view = df.copy()
if search:
    df_view = df_view[df_view.index.str.lower().str.contains(search.lower())]
if filter_men:
    df_view = df_view[df_view["Mention"].isin(filter_men)]

sort_map = {
    "Moyenne ↓":       ("Moyenne",        False),
    "Moyenne ↑":       ("Moyenne",        True),
    "Nom A→Z":         ("__index__",      True),
    "Progression ↑":   ("Pente",          False),
    "Regression ↓":    ("Pente",          True),
    "Taux reussite ↓": ("Taux_Reussite",  False),
    "Ecart-type ↓":    ("Ecart_type",     False),
    "Zeros ↓":         ("Zeros",          False),
}
sc, sa = sort_map[sort_opt]
if sc == "__index__":
    df_view = df_view.sort_index(ascending=True)
else:
    df_view = df_view.sort_values(sc, ascending=sa)

# ── Stats globales ─────────────────────────────────────────────────────────
G_avg   = round(df["Moyenne"].mean(), 2)
G_med   = round(df["Moyenne"].median(), 2)
G_std   = round(df["Moyenne"].std(), 2)
G_admis = int((df["Moyenne"] >= seuil).sum())
G_total = len(df)
G_up    = int((df["Pente"] > 0).sum())
G_down  = int((df["Pente"] < 0).sum())

# ══════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════
badge = ('<span style="color:#FF922B">⚡ DONNÉES DÉMO</span>' if is_demo
         else '<span style="color:#69DB7C">✅ DONNÉES IMPORTÉES</span>')
st.markdown(f"""
<div style="background:linear-gradient(135deg,#0d1421,#111827);
     border:1px solid rgba(255,255,255,0.08);border-radius:16px;
     padding:22px 30px;margin-bottom:22px">
  <div style="font-size:24px;font-weight:900;color:#fff;margin-bottom:4px">
    🎯 AgentTracker <span style="color:#FFD93D">PRO</span></div>
  <div style="font-size:11px;color:#555;letter-spacing:2px">
    PLATEFORME D'ANALYSE · FORMATION AGENTS ENQUÊTEURS &nbsp;·&nbsp;
    {badge} &nbsp;·&nbsp; {G_total} agents &nbsp;·&nbsp;
    {len(note_labels)} épreuves &nbsp;·&nbsp; Seuil {seuil}/20
  </div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
#  ONGLETS
# ══════════════════════════════════════════════════════════════════════════
t1,t2,t3,t4,t5,t6,t7,t8 = st.tabs([
    "🏠 Dashboard","🏆 Classement","📈 Évolution",
    "⚖️ Comparer","🔥 Heatmap","🔬 Analytique",
    "📋 Épreuves","📤 Export"])

# ══════════════════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════
with t1:
    k1,k2,k3,k4,k5,k6,k7 = st.columns(7)
    k1.metric("👥 Agents",        G_total)
    k2.metric("📊 Moy. générale", G_avg,  help="/20")
    k3.metric("📐 Médiane",       G_med,  help="/20")
    k4.metric("🎯 Ecart-type σ",  G_std)
    k5.metric("✅ Admis",  f"{G_admis}/{G_total}", help=f"≥{seuil}/20")
    k6.metric("📈 En hausse",     G_up)
    k7.metric("📉 En baisse",     G_down)
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        avgs_ep = [round(df[n].mean(), 2) for n in note_labels]
        meds_ep = [round(df[n].median(), 2) for n in note_labels]
        fig = go.Figure()
        fig.add_bar(x=note_labels, y=avgs_ep, name="Moyenne",
                    marker_color=["#69DB7C" if v >= seuil else "#FF6B6B"
                                  for v in avgs_ep],
                    marker_line_width=0)
        fig.add_scatter(x=note_labels, y=meds_ep, name="Médiane",
                        mode="lines+markers",
                        line=dict(color="#FFD93D", width=2, dash="dot"),
                        marker=dict(size=6))
        fig = add_refs(fig, seuil, G_avg, show_seuil, False)
        fig.update_yaxes(range=[0, 20])
        st.plotly_chart(dark_fig(fig).update_layout(
            title="Moyenne de classe par épreuve"), use_container_width=True)

    with c2:
        bins  = [0,5,10,12,14,16,18,20.01]
        blabs = ["0–5","5–10","10–12","12–14","14–16","16–18","18–20"]
        bcols = ["#444","#FF6B6B","#FF922B","#FFD93D","#74C0FC","#4DABF7","#69DB7C"]
        cuts  = pd.cut(df["Moyenne"], bins=bins, labels=blabs, right=False)
        cnts  = cuts.value_counts().reindex(blabs).fillna(0)
        fig2  = go.Figure(go.Bar(x=cnts.index, y=cnts.values,
                                 marker_color=bcols, marker_line_width=0))
        st.plotly_chart(dark_fig(fig2).update_layout(
            title="Distribution des moyennes"), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        men_order  = ["🏆 Excellent","⭐ Très Bien","✅ Bien",
                      "👍 Assez Bien","⚠️ Passable","❌ Insuffisant"]
        men_colors = ["#69DB7C","#4DABF7","#74C0FC","#FFD93D","#FF922B","#FF6B6B"]
        men_cnts   = df["Mention"].value_counts().reindex(men_order).fillna(0)
        fig3 = go.Figure(go.Bar(
            x=men_cnts.values, y=men_cnts.index, orientation="h",
            marker_color=men_colors, marker_line_width=0,
            text=men_cnts.values, textposition="auto"))
        st.plotly_chart(dark_fig(fig3).update_layout(
            title="Répartition par mention"), use_container_width=True)

    with c4:
        st.markdown("#### 🏅 Top 5 agents")
        top5   = df.sort_values("Moyenne", ascending=False).head(5)
        medals = ["🥇","🥈","🥉","4️⃣","5️⃣"]
        for i, (ag, row) in enumerate(top5.iterrows()):
            c   = row["MCouleur"]
            pct = int(row["Moyenne"] / 20 * 100)
            st.markdown(f"""
<div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.06);
     border-radius:10px;padding:10px 14px;margin-bottom:8px;
     display:flex;align-items:center;justify-content:space-between">
  <div style="display:flex;align-items:center;gap:10px">
    <span style="font-size:18px">{medals[i]}</span>
    <div>
      <div style="font-size:12px;font-weight:700;color:#ddd">{ag}</div>
      <div style="width:120px;height:4px;background:rgba(255,255,255,0.07);
           border-radius:2px;margin-top:4px">
        <div style="width:{pct}%;height:4px;background:{c};border-radius:2px"></div>
      </div>
    </div>
  </div>
  <span style="font-size:18px;font-weight:900;color:{c};font-family:monospace">{row['Moyenne']}</span>
</div>""", unsafe_allow_html=True)

    st.markdown("#### 📈 Évolution notes — Top 8 agents")
    top8 = df.sort_values("Moyenne", ascending=False).head(8)
    fig4 = go.Figure()
    for ag, row in top8.iterrows():
        fig4.add_scatter(x=note_labels, y=[row[n] for n in note_labels],
                         name=ag.split()[0], mode="lines+markers",
                         line=dict(color=row["Couleur"], width=2),
                         marker=dict(size=5))
    fig4 = add_refs(fig4, seuil, G_avg, show_seuil, show_promo)
    fig4.update_yaxes(range=[0, 20])
    st.plotly_chart(dark_fig(fig4, 320).update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    bgcolor="rgba(0,0,0,0)")), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# TAB 2 — CLASSEMENT
# ══════════════════════════════════════════════════════════════════════════
with t2:
    st.caption(f"{len(df_view)} agents affichés")
    cols_show = (note_labels +
                 ["Moyenne","Mention","Mediane","Ecart_type",
                  "Min","Max","Taux_Reussite","Pente","Delta","Zeros"])
    df_tab = df_view[cols_show].reset_index()
    df_tab.insert(0, "Rang", range(1, len(df_tab)+1))

    # Style pur CSS, SANS matplotlib
    styled = df_tab.style
    for col in note_labels:
        styled = styled.applymap(style_note_col, subset=[col])
    styled = styled.applymap(style_avg_col,   subset=["Moyenne"])
    styled = styled.applymap(style_pente_col, subset=["Pente","Delta"])
    styled = styled.applymap(style_taux_col,  subset=["Taux_Reussite"])
    st.dataframe(styled, use_container_width=True, height=580)

    fig5 = go.Figure()
    for ag, row in df_view.sort_values("Moyenne").iterrows():
        fig5.add_bar(x=[row["Moyenne"]], y=[ag], orientation="h",
                     marker_color=row["MCouleur"], marker_line_width=0,
                     showlegend=False,
                     hovertemplate=f"<b>{ag}</b><br>Moy: {row['Moyenne']}<br>{row['Mention']}<extra></extra>")
    if show_seuil:
        fig5.add_vline(x=seuil, line_dash="dash",
                       line_color="rgba(255,107,107,0.5)")
    if show_promo:
        fig5.add_vline(x=G_avg, line_dash="dot",
                       line_color="rgba(255,217,61,0.4)")
    fig5.update_xaxes(range=[0, 20])
    st.plotly_chart(dark_fig(fig5, max(420, G_total*24)).update_layout(
        title="Classement visuel"), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# TAB 3 — ÉVOLUTION
# ══════════════════════════════════════════════════════════════════════════
with t3:
    agent_sel = st.selectbox("Choisir un agent", df.index.tolist(), key="evo")
    row_sel   = df.loc[agent_sel]
    notes_sel = [row_sel[n] for n in note_labels]
    c_sel     = row_sel["MCouleur"]

    x_num   = np.arange(len(note_labels), dtype=float)
    trend_y = list(np.poly1d(np.polyfit(x_num, notes_sel, 1))(x_num))

    fig6 = go.Figure()
    fig6.add_scatter(x=note_labels, y=notes_sel,
                     name=agent_sel, mode="lines+markers+text",
                     text=[str(n) for n in notes_sel],
                     textposition="top center",
                     textfont=dict(size=11, color=c_sel),
                     line=dict(color=c_sel, width=3),
                     marker=dict(size=9,
                                 color=[color_note(n) for n in notes_sel]),
                     fill="tozeroy", fillcolor=c_sel+"18")
    fig6.add_scatter(x=note_labels, y=trend_y,
                     name=f"Tendance (pente={row_sel['Pente']:+.3f})",
                     mode="lines",
                     line=dict(color="#FFD93D", width=1.5, dash="dot"),
                     hoverinfo="skip")
    fig6 = add_refs(fig6, seuil, G_avg, show_seuil, show_promo)
    fig6.update_yaxes(range=[0, 20])
    st.plotly_chart(dark_fig(fig6, 380).update_layout(
        title=f"{agent_sel} — {row_sel['Mention']} — Moy. {row_sel['Moyenne']}/20"
    ), use_container_width=True)

    m1,m2,m3,m4,m5,m6,m7 = st.columns(7)
    m1.metric("Moyenne",       row_sel["Moyenne"])
    m2.metric("Médiane",       row_sel["Mediane"])
    m3.metric("Ecart-type σ",  row_sel["Ecart_type"])
    m4.metric("Min",           row_sel["Min"])
    m5.metric("Max",           row_sel["Max"])
    m6.metric("Taux réussite", f"{row_sel['Taux_Reussite']}%")
    m7.metric("Pente",         f"{row_sel['Pente']:+.3f}")

    st.markdown("---")
    st.markdown("#### Δ Note : Première → Dernière épreuve")
    cohort         = df[["Pente","MCouleur"]].copy()
    cohort["first"]= [df.loc[ag, note_labels[0]]  for ag in df.index]
    cohort["last"] = [df.loc[ag, note_labels[-1]] for ag in df.index]
    cohort["delta"]= cohort["last"] - cohort["first"]
    cohort         = cohort.sort_values("delta", ascending=True)
    fig7 = go.Figure(go.Bar(
        x=cohort["delta"], y=cohort.index, orientation="h",
        marker_color=["#69DB7C" if d >= 0 else "#FF6B6B"
                      for d in cohort["delta"]],
        marker_line_width=0,
        text=[f"{d:+d}" for d in cohort["delta"]], textposition="auto"))
    fig7.add_vline(x=0, line_color="rgba(255,255,255,0.25)")
    st.plotly_chart(dark_fig(fig7, max(400, G_total*24)).update_layout(
        title=f"Delta ({note_labels[-1]} - {note_labels[0]})"
    ), use_container_width=True)

    st.markdown("#### Courbes individuelles — tous agents")
    cols_grid = st.columns(3)
    for i, (ag, row) in enumerate(
            df.sort_values("Moyenne", ascending=False).iterrows()):
        vals = [row[n] for n in note_labels]
        c    = row["MCouleur"]
        with cols_grid[i % 3]:
            fg = go.Figure()
            fg.add_scatter(x=note_labels, y=vals,
                           mode="lines+markers",
                           line=dict(color=c, width=2),
                           marker=dict(size=4),
                           fill="tozeroy", fillcolor=c+"15")
            if show_seuil:
                fg.add_hline(y=seuil, line_dash="dash",
                             line_color="rgba(255,107,107,0.3)")
            fg.update_yaxes(range=[0, 20])
            fg = dark_fig(fg, 140)
            fg.update_layout(
                title=dict(
                    text=f"<b>{ag.split()[0]}</b> {row['Mention']} {row['Moyenne']}",
                    font=dict(size=11, color=c), x=0),
                showlegend=False, margin=dict(t=32, b=16, l=24, r=8))
            fg.update_xaxes(showticklabels=False)
            fg.update_yaxes(showticklabels=False)
            st.plotly_chart(fg, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# TAB 4 — COMPARER
# ══════════════════════════════════════════════════════════════════════════
with t4:
    sel = st.multiselect("Sélectionnez 2 à 6 agents",
                         df.index.tolist(), max_selections=6)
    if len(sel) < 2:
        st.info("👆 Sélectionnez au moins 2 agents pour démarrer.")
    else:
        rcols = st.columns(len(sel))
        for i, ag in enumerate(sel):
            row = df.loc[ag]
            c   = row["MCouleur"]
            rcols[i].markdown(f"""
<div style="background:{c}15;border:1px solid {c}44;border-radius:12px;
     padding:14px;text-align:center">
  <div style="font-size:10px;color:{c};font-weight:700;letter-spacing:1px">{ag.split()[0].upper()}</div>
  <div style="font-size:24px;font-weight:900;color:{c};font-family:monospace;margin:6px 0">{row['Moyenne']}</div>
  <div style="font-size:10px;color:#666">{row['Mention']}</div>
  <div style="font-size:10px;color:#444;margin-top:4px">σ {row['Ecart_type']} · med {row['Mediane']}</div>
</div>""", unsafe_allow_html=True)

        st.markdown("")
        cA, cB = st.columns(2)
        with cA:
            fc = go.Figure()
            for ag in sel:
                row = df.loc[ag]
                fc.add_scatter(
                    x=note_labels, y=[row[n] for n in note_labels],
                    name=ag.split()[0], mode="lines+markers",
                    line=dict(color=row["Couleur"], width=2.5),
                    marker=dict(size=6))
            fc = add_refs(fc, seuil, G_avg, show_seuil, show_promo)
            fc.update_yaxes(range=[0, 20])
            st.plotly_chart(dark_fig(fc).update_layout(
                title="Courbes comparées"), use_container_width=True)

        with cB:
            fr = go.Figure()
            for ag in sel:
                row  = df.loc[ag]
                vals = [row[n] for n in note_labels]
                fr.add_scatterpolar(
                    r=vals+[vals[0]], theta=note_labels+[note_labels[0]],
                    name=ag.split()[0], fill="toself",
                    line=dict(color=row["Couleur"], width=2),
                    fillcolor=row["Couleur"]+"25")
            fr.update_layout(
                polar=dict(
                    radialaxis=dict(range=[0,20], color="#555",
                                    gridcolor="rgba(255,255,255,0.07)"),
                    bgcolor="#0d1421", angularaxis=dict(color="#666")),
                paper_bgcolor="#0d1421", font_color="#aaa", height=350,
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                title=dict(text="Radar — Profil par épreuve",
                           font_color="#aaa"),
                margin=dict(t=48, b=32))
            st.plotly_chart(fr, use_container_width=True)

        st.markdown("#### Tableau comparatif")
        rows_cmp = []
        for nl in note_labels:
            r_dict = {ag.split()[0]: df.loc[ag, nl] for ag in sel}
            best   = max(r_dict.values())
            row_d  = {"Épreuve": nl}
            for k, v in r_dict.items():
                row_d[k] = f"{v} ★" if v == best and best > 0 else str(v)
            rows_cmp.append(row_d)
        avg_row = {"Épreuve": "📊 Moyenne"}
        for ag in sel:
            avg_row[ag.split()[0]] = df.loc[ag, "Moyenne"]
        rows_cmp.append(avg_row)
        st.dataframe(pd.DataFrame(rows_cmp).set_index("Épreuve"),
                     use_container_width=True)

        fig_met = go.Figure()
        for ag in sel:
            row = df.loc[ag]
            fig_met.add_bar(
                name=ag.split()[0],
                x=["Moyenne","Médiane","Ecart-type","Taux Réussite"],
                y=[row["Moyenne"], row["Mediane"],
                   row["Ecart_type"], row["Taux_Reussite"]],
                marker_color=row["Couleur"])
        st.plotly_chart(dark_fig(fig_met).update_layout(
            title="Métriques clés comparées", barmode="group"),
            use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# TAB 5 — HEATMAP
# ══════════════════════════════════════════════════════════════════════════
with t5:
    st.caption("Chaque cellule = note réelle (0 = vraie note zéro).")
    hm = df_view[note_labels + ["Moyenne"]]
    fig_hm = go.Figure(go.Heatmap(
        z=hm.values, x=note_labels+["Moyenne"],
        y=hm.index.tolist(),
        colorscale="RdYlGn", zmin=0, zmax=20,
        text=hm.values, texttemplate="%{text}",
        textfont=dict(size=11),
        colorbar=dict(title="Note",
                      tickfont=dict(color="#aaa"),
                      titlefont=dict(color="#aaa"),
                      bgcolor="#0d1421")))
    fig_hm.update_layout(
        plot_bgcolor="#0d1421", paper_bgcolor="#0d1421", font_color="#aaa",
        height=max(500, G_total*28), title="Heatmap complète",
        xaxis=dict(side="top"), yaxis=dict(autorange="reversed"),
        margin=dict(t=64, b=16, l=220, r=80))
    st.plotly_chart(fig_hm, use_container_width=True)

    moys_ep = pd.DataFrame([[round(df[n].mean(),2) for n in note_labels]],
                            columns=note_labels, index=["Moy. classe"])
    fig_hm2 = go.Figure(go.Heatmap(
        z=moys_ep.values, x=note_labels, y=["Moy. classe"],
        colorscale="RdYlGn", zmin=0, zmax=20,
        text=moys_ep.values, texttemplate="%{text}",
        textfont=dict(size=12, color="white")))
    fig_hm2.update_layout(
        plot_bgcolor="#0d1421", paper_bgcolor="#0d1421", font_color="#aaa",
        height=110, title="Moyenne de classe par épreuve",
        margin=dict(t=40, b=16, l=220, r=80))
    st.plotly_chart(fig_hm2, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# TAB 6 — ANALYTIQUE
# ══════════════════════════════════════════════════════════════════════════
with t6:
    cA, cB = st.columns(2)
    with cA:
        df_sc = df.reset_index()[["Agent","Moyenne","Ecart_type","Mention"]]
        fig_sc = px.scatter(
            df_sc, x="Moyenne", y="Ecart_type", text="Agent",
            color="Mention",
            color_discrete_map={
                "🏆 Excellent":"#69DB7C","⭐ Très Bien":"#4DABF7",
                "✅ Bien":"#74C0FC","👍 Assez Bien":"#FFD93D",
                "⚠️ Passable":"#FF922B","❌ Insuffisant":"#FF6B6B"},
            title="Moyenne vs Régularité (σ)", hover_name="Agent",
            labels={"Ecart_type":"Ecart-type σ"})
        fig_sc.update_traces(textposition="top center", marker=dict(size=10))
        if show_seuil:
            fig_sc.add_vline(x=seuil, line_dash="dash",
                             line_color="rgba(255,107,107,0.4)")
        fig_sc.update_xaxes(range=[0, 20])
        st.plotly_chart(dark_fig(fig_sc, 380), use_container_width=True)

    with cB:
        all_vals = df[note_labels].values.flatten().astype(int)
        freq     = pd.Series(all_vals).value_counts().sort_index()
        fig_fr   = go.Figure(go.Bar(
            x=freq.index, y=freq.values,
            marker_color=["#FF6B6B" if n < seuil else "#69DB7C"
                          for n in freq.index],
            marker_line_width=0, text=freq.values, textposition="auto"))
        if show_seuil:
            fig_fr.add_vline(x=seuil-0.5, line_dash="dash",
                             line_color="rgba(255,107,107,0.5)")
        st.plotly_chart(dark_fig(fig_fr, 380).update_layout(
            title="Fréquence de chaque note (0–20)"
        ), use_container_width=True)

    ep_stats = pd.DataFrame({
        "Épreuve":        note_labels,
        "Moyenne":        [round(df[n].mean(), 2)   for n in note_labels],
        "Médiane":        [round(df[n].median(), 2) for n in note_labels],
        "Ecart_type_σ":   [round(df[n].std(), 2)    for n in note_labels],
        "Min":            [int(df[n].min())           for n in note_labels],
        "Max":            [int(df[n].max())           for n in note_labels],
        "Zeros":          [int((df[n]==0).sum())      for n in note_labels],
        f"Admis≥{seuil}": [int((df[n]>=seuil).sum()) for n in note_labels],
        "Taux_pct":       [round((df[n]>=seuil).mean()*100,1) for n in note_labels],
    }).set_index("Épreuve")
    st.markdown("#### Statistiques détaillées par épreuve")
    st.dataframe(ep_stats, use_container_width=True)

    fig_ep = go.Figure()
    fig_ep.add_scatter(x=note_labels, y=ep_stats["Moyenne"],
                       name="Moyenne", mode="lines+markers",
                       line=dict(color="#4DABF7", width=2.5))
    fig_ep.add_scatter(x=note_labels, y=ep_stats["Médiane"],
                       name="Médiane", mode="lines+markers",
                       line=dict(color="#FFD93D", width=2, dash="dot"))
    fig_ep.add_scatter(x=note_labels, y=ep_stats["Max"],
                       name="Max", mode="lines+markers",
                       line=dict(color="#69DB7C", width=1.5))
    fig_ep.add_scatter(x=note_labels, y=ep_stats["Min"],
                       name="Min", mode="lines+markers",
                       line=dict(color="#FF6B6B", width=1.5))
    fig_ep = add_refs(fig_ep, seuil, G_avg, show_seuil, show_promo)
    fig_ep.update_yaxes(range=[0, 20])
    st.plotly_chart(dark_fig(fig_ep, 320).update_layout(
        title="Stats par épreuve"), use_container_width=True)

    st.markdown("#### Classement par pente de progression")
    pentes = df.sort_values("Pente", ascending=True)
    fig_p  = go.Figure(go.Bar(
        x=pentes["Pente"], y=pentes.index, orientation="h",
        marker_color=["#69DB7C" if p >= 0 else "#FF6B6B"
                      for p in pentes["Pente"]],
        marker_line_width=0,
        text=[f"{p:+.3f}" for p in pentes["Pente"]], textposition="auto"))
    fig_p.add_vline(x=0, line_color="rgba(255,255,255,0.25)")
    st.plotly_chart(dark_fig(fig_p, max(420, G_total*24)).update_layout(
        title="Pente de progression (régression linéaire)"
    ), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# TAB 7 — ÉPREUVES
# ══════════════════════════════════════════════════════════════════════════
with t7:
    note_sel  = st.selectbox("Choisir une épreuve", note_labels)
    vals_note = df[note_sel].sort_values(ascending=False)
    avg_note  = round(float(vals_note.mean()), 2)
    med_note  = round(float(vals_note.median()), 2)
    std_note  = round(float(vals_note.std()), 2)
    pass_note = int((vals_note >= seuil).sum())

    e1,e2,e3,e4,e5,e6,e7 = st.columns(7)
    e1.metric("Moyenne",       avg_note)
    e2.metric("Médiane",       med_note)
    e3.metric("Ecart-type",    std_note)
    e4.metric("Min",           int(vals_note.min()))
    e5.metric("Max",           int(vals_note.max()))
    e6.metric("Zeros",         int((vals_note==0).sum()))
    e7.metric(f"Admis ≥{seuil}", f"{pass_note}/{G_total}")

    cA, cB = st.columns(2)
    with cA:
        fig_ep2 = go.Figure(go.Bar(
            x=vals_note.values, y=vals_note.index, orientation="h",
            marker_color=["#FF6B6B" if v==0 else "#69DB7C" if v>=seuil
                          else "#FF922B" for v in vals_note.values],
            marker_line_width=0,
            text=vals_note.values, textposition="auto"))
        if show_seuil:
            fig_ep2.add_vline(x=seuil, line_dash="dash",
                              line_color="rgba(255,107,107,0.5)")
        if show_promo:
            fig_ep2.add_vline(x=avg_note, line_dash="dot",
                              line_color="rgba(255,217,61,0.4)")
        fig_ep2.update_xaxes(range=[0, 20])
        st.plotly_chart(dark_fig(fig_ep2, max(400, G_total*22)).update_layout(
            title=f"Notes — {note_sel}"), use_container_width=True)

    with cB:
        st.markdown("#### 🏅 Podium")
        medals = ["🥇","🥈","🥉"]
        for i, (ag, v) in enumerate(vals_note.head(3).items()):
            c = "#69DB7C" if v >= 16 else "#FFD93D" if v >= 12 else "#FF922B"
            st.markdown(f"""
<div style="background:rgba(105,219,124,0.07);
     border:1px solid rgba(105,219,124,0.15);
     border-radius:9px;padding:10px 14px;margin-bottom:6px;
     display:flex;justify-content:space-between;align-items:center">
  <span>{medals[i]} {ag}</span>
  <span style="font-family:monospace;font-size:16px;font-weight:900;color:#69DB7C">{v}</span>
</div>""", unsafe_allow_html=True)

        st.markdown("#### ⚠️ Bas du classement")
        for ag, v in vals_note.tail(3).items():
            st.markdown(f"""
<div style="background:rgba(255,107,107,0.07);
     border:1px solid rgba(255,107,107,0.15);
     border-radius:9px;padding:10px 14px;margin-bottom:6px;
     display:flex;justify-content:space-between;align-items:center">
  <span>⚠️ {ag}</span>
  <span style="font-family:monospace;font-size:16px;font-weight:900;color:#FF6B6B">{v}</span>
</div>""", unsafe_allow_html=True)

        fig_dist = go.Figure(go.Histogram(
            x=vals_note.values, nbinsx=10,
            marker_color="#4DABF7",
            marker_line_color="#0d1421", marker_line_width=1))
        if show_seuil:
            fig_dist.add_vline(x=seuil, line_dash="dash",
                               line_color="rgba(255,107,107,0.5)")
        st.plotly_chart(dark_fig(fig_dist, 220).update_layout(
            title=f"Distribution — {note_sel}",
            xaxis=dict(range=[0, 20])), use_container_width=True)

    st.markdown("---")
    st.markdown("#### Récapitulatif de toutes les épreuves")
    all_ep = []
    for nl in note_labels:
        v = df[nl]
        all_ep.append({
            "Épreuve":        nl,
            "Moy.":           round(v.mean(), 2),
            "Med.":           round(v.median(), 2),
            "σ":              round(v.std(), 2),
            "Min":            int(v.min()),
            "Max":            int(v.max()),
            "Zeros":          int((v==0).sum()),
            f"Admis≥{seuil}": int((v>=seuil).sum()),
            "Taux%":          round((v>=seuil).mean()*100, 1),
        })
    st.dataframe(pd.DataFrame(all_ep).set_index("Épreuve"),
                 use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# TAB 8 — EXPORT
# ══════════════════════════════════════════════════════════════════════════
with t8:
    st.markdown("### 📤 Exporter les données")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 Export Excel complet (3 feuilles)")
        st.markdown("""
- **Donnees** : toutes les notes + toutes les métriques
- **Stats_Epreuves** : analyse épreuve par épreuve
- **Classement** : classement final trié par moyenne
""")
        st.download_button(
            label="⬇️ Télécharger Excel (.xlsx)",
            data=export_excel(df, note_labels),
            file_name="agenttracker_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with col2:
        st.markdown("#### 📋 Export CSV — Notes brutes")
        csv_raw = (df.reset_index()[["Agent"]+note_labels]
                   .to_csv(sep=";", index=False)
                   .encode("utf-8-sig"))
        st.download_button("⬇️ CSV notes brutes", csv_raw,
                           "notes_brutes.csv", "text/csv")

        st.markdown("#### 📋 Export CSV — Classement")
        csv_rank = (df.sort_values("Moyenne", ascending=False)
                    .reset_index()[
                        ["Agent","Moyenne","Mention","Mediane","Ecart_type",
                         "Min","Max","Taux_Reussite","Pente","Delta","Zeros"]]
                    .to_csv(sep=";", index=False)
                    .encode("utf-8-sig"))
        st.download_button("⬇️ CSV classement", csv_rank,
                           "classement.csv", "text/csv")

    st.markdown("---")
    st.markdown("#### Aperçu des données")
    st.dataframe(
        df.reset_index()[["Agent"]+note_labels+["Moyenne","Mention","Taux_Reussite","Pente"]],
        use_container_width=True, height=400)

# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<div style='text-align:center;color:#333;font-size:11px;letter-spacing:1.5px'>"
    f"AGENTTRACKER PRO · {G_total} AGENTS · {len(note_labels)} ÉPREUVES · "
    f"SEUIL {seuil}/20 · {G_admis} ADMIS / {G_total-G_admis} AJOURNÉS"
    f"</div>", unsafe_allow_html=True)
