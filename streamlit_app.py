import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import io

st.set_page_config(page_title="Tableau de Bord des Notes", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: #ffffff !important; color: #1a1a2e; }
  .main, .block-container { background-color: #ffffff !important; padding-top: 1.5rem; }
  section[data-testid="stSidebar"] { background: linear-gradient(160deg, #f0f4ff 0%, #e8f0fe 100%); border-right: 1px solid #dce4f5; }
  .main-title { font-family: 'DM Serif Display', serif; font-size: 2.2rem; color: #2c3e7a; margin-bottom: 0.1rem; }
  .sub-title { font-size: 0.95rem; color: #6b7db3; margin-bottom: 1.5rem; }
  .kpi-card { background:#ffffff; border:1px solid #e0e8ff; border-radius:14px; padding:18px 20px; text-align:center; box-shadow:0 2px 12px rgba(44,62,122,0.07); margin-bottom:8px; }
  .kpi-value { font-size:1.9rem; font-weight:700; color:#2c3e7a; line-height:1; }
  .kpi-label { font-size:0.78rem; color:#7a8db3; margin-top:5px; text-transform:uppercase; letter-spacing:0.8px; font-weight:500; }
  .kpi-sub   { font-size:0.72rem; color:#a0aec0; margin-top:2px; }
  .section-title { font-family:'DM Serif Display',serif; font-size:1.3rem; color:#2c3e7a; margin-top:1.5rem; margin-bottom:0.5rem; border-left:4px solid #4a6cf7; padding-left:12px; }
  .stDownloadButton > button { background:linear-gradient(135deg,#4a6cf7,#7b5ea7); color:white; border:none; border-radius:8px; font-weight:600; padding:10px 20px; }
  .stTabs [data-baseweb="tab-list"] { background:#f0f4ff; border-radius:10px; padding:4px; gap:4px; }
  .stTabs [data-baseweb="tab"] { border-radius:8px; font-weight:500; color:#2c3e7a; padding:8px 18px; }
  .stTabs [aria-selected="true"] { background:#ffffff !important; color:#4a6cf7 !important; box-shadow:0 1px 6px rgba(74,108,247,0.15); }
  .mention-tb  { background:#e6f4ea; color:#1e7e34; padding:3px 10px; border-radius:20px; font-size:0.8rem; font-weight:600; }
  .mention-b   { background:#dbeafe; color:#1a56db; padding:3px 10px; border-radius:20px; font-size:0.8rem; font-weight:600; }
  .mention-ab  { background:#fef3c7; color:#92400e; padding:3px 10px; border-radius:20px; font-size:0.8rem; font-weight:600; }
  .mention-ins { background:#fee2e2; color:#b91c1c; padding:3px 10px; border-radius:20px; font-size:0.8rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── DONNÉES PAR DÉFAUT ──────────────────────────────────────────────────────
DEFAULT_DATA = {
    "Nom et Prénom": ["Acka Gustave Boris","Agnero Djadja","Kra Yao Assouman Aubin Gael","Kouao Marie-Paule","Sangaré Aissata","Kouassi Kangah Akissi Philomène","Yao Julienne","Amankan Adjo Josiane","Fouati Edwige","Agnehoura Vanessa","Djeha Somaud Marthe Abigail","Gnomblé Christelle","Loua Saty Veronique","Coulibaly Lancina Medard","Deza Boga Stefan","Beugré Brigitte","Bogui Kacohon Prisca Sandrine epse Gris","Touré Madongon Mariam","Konan Amenan Grâce-Victoire","Diarrassouba Madoussou"],
    "Note 2":[18,18,17,18,17,13,16,16,15,14,14,15,0,14,0,10,0,14,0,0],
    "Note 3":[14,14,6,0,11,11,11,9,9,9,11,6,14,6,6,9,3,11,0,0],
    "Note 4":[15,18,15,14,13,14,13,15,14,16,0,14,15,9,10,0,15,15,11,0],
    "Note 5":[20,13,10,17,13,10,10,0,13,0,13,13,13,10,13,13,10,10,10,0],
    "Note 6":[12,16,16,12,14,16,16,16,12,14,14,8,12,12,12,18,14,12,12,10],
    "Note 7":[19,17,19,19,18,18,17,15,18,18,16,19,17,17,17,15,18,15,14,11],
    "Note 8":[20,20,18,18,15,18,13,17,13,17,17,15,15,15,17,12,18,0,13,10],
    "Note 9":[18,18,19,20,15,14,13,19,12,17,17,9,12,13,16,13,0,0,8,3],
}

# ── FONCTIONS ────────────────────────────────────────────────────────────────
def mention_label(n):
    if n >= 16:  return "Très Bien",   "mention-tb"
    elif n >= 14: return "Bien",        "mention-b"
    elif n >= 10: return "Assez Bien",  "mention-ab"
    else:         return "Insuffisant", "mention-ins"

def get_note_cols(df):
    return [c for c in df.columns if c != df.columns[0]]

def compute_stats(df, note_cols, name_col):
    rows = []
    for _, row in df.iterrows():
        vals = [float(row[c]) for c in note_cols]   # 0 = vraie note
        moy  = round(np.mean(vals), 2)
        ml, _ = mention_label(moy)
        rows.append({
            "Agent":         row[name_col],
            "Moyenne":       moy,
            "Max":           max(vals),
            "Min":           min(vals),
            "Médiane":       round(np.median(vals), 2),
            "Écart-type":    round(np.std(vals), 2),
            "Nb notes":      len(vals),
            "Mention":       ml,
        })
    return pd.DataFrame(rows)

def color_cell(val, col):
    """Retourne une couleur de fond selon la valeur (pour notes 0-20)."""
    if col == "Moyenne" or col == "Médiane" or col == "Max" or col == "Min":
        if val >= 16:   return "background-color:#e6f4ea"
        elif val >= 14: return "background-color:#dbeafe"
        elif val >= 10: return "background-color:#fef3c7"
        else:           return "background-color:#fee2e2"
    return ""

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 Source des données")
    uploaded = st.file_uploader("Importer un fichier Excel", type=["xlsx","xls"],
        help="1ère colonne = noms · colonnes suivantes = notes (les 0 sont des vraies notes)")
    st.markdown("---")

if uploaded:
    try:
        df = pd.read_excel(uploaded)
        df.columns = df.columns.astype(str).str.strip()
        st.sidebar.success(f"✅ {df.shape[0]} agents · {df.shape[1]-1} notes chargées")
    except Exception as e:
        st.sidebar.error(f"Erreur : {e}")
        df = pd.DataFrame(DEFAULT_DATA)
else:
    df = pd.DataFrame(DEFAULT_DATA)
    st.sidebar.info("📌 Données par défaut actives\n(importez un Excel pour changer)")

name_col  = df.columns[0]
note_cols = get_note_cols(df)
agents    = df[name_col].tolist()

with st.sidebar:
    st.markdown("### 🔍 Filtres")
    selected_agents = st.multiselect("Agents — courbes individuelles", options=agents, default=agents[:5])
    note_range = st.slider("Filtre par moyenne (tableau)", 0.0, 20.0, (0.0, 20.0), 0.5)
    st.markdown("---")
    st.markdown("### ℹ️ Info")
    st.markdown(f"**{df.shape[0]}** agents · **{len(note_cols)}** évaluations")
    st.caption("ℹ️ Les notes 0 sont comptabilisées comme de vraies notes.")

# ── EN-TÊTE ──────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">📊 Tableau de Bord — Analyse des Notes</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">{df.shape[0]} agents · {len(note_cols)} évaluations · Les zéros sont des notes réelles</div>', unsafe_allow_html=True)

# ── CALCULS GLOBAUX ──────────────────────────────────────────────────────────
all_vals = df[note_cols].values.flatten().astype(float)
df_stats = compute_stats(df, note_cols, name_col)
moy_gen  = round(np.mean(all_vals), 2)

# ── KPI ──────────────────────────────────────────────────────────────────────
k1,k2,k3,k4,k5,k6 = st.columns(6)
kpi_data = [
    (moy_gen,                                              "Moyenne Générale",     "toutes notes"),
    (round(df[note_cols].astype(float).max(axis=1).mean(),2), "Moy. Max/Agent",    "meilleur score moyen"),
    (round(df[note_cols].astype(float).min(axis=1).mean(),2), "Moy. Min/Agent",    "score le plus bas moyen"),
    (int((df[note_cols]==20).sum().sum()),                  "Notes 20/20",         "scores parfaits"),
    (int((df[note_cols]==0).sum().sum()),                   "Notes = 0",           "zéros obtenus"),
    (df_stats[df_stats["Mention"]=="Très Bien"].shape[0],  "Très Bien",           f"sur {df.shape[0]} agents"),
]
for col,(val,label,sub) in zip([k1,k2,k3,k4,k5,k6],kpi_data):
    col.markdown(f'<div class="kpi-card"><div class="kpi-value">{val}</div><div class="kpi-label">{label}</div><div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# ONGLETS
# ════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Courbes individuelles",
    "🌐 Tendance globale",
    "📋 Tableau des stats",
    "📊 Distributions",
    "🔥 Carte de chaleur",
    "🏆 Classement & Podium",
])

# ───────────────────────────────────────────
# ONGLET 1 – COURBES INDIVIDUELLES
# ───────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">Évolution individuelle des notes</div>', unsafe_allow_html=True)
    st.caption("Les 0 sont affichés comme notes réelles. Lignes de seuil à 10 et 14.")

    if not selected_agents:
        st.info("👈 Sélectionnez au moins un agent dans le panneau latéral.")
    else:
        palette = (px.colors.qualitative.Pastel + px.colors.qualitative.Safe
                   + px.colors.qualitative.Vivid + px.colors.qualitative.Dark24)
        fig = go.Figure()
        for i, agent in enumerate(selected_agents):
            row   = df[df[name_col]==agent].iloc[0]
            notes = [float(row[c]) for c in note_cols]
            c     = palette[i % len(palette)]
            fig.add_trace(go.Scatter(
                x=note_cols, y=notes, mode="lines+markers+text", name=agent,
                line=dict(color=c, width=2.5, shape="spline"),
                marker=dict(size=9, color=c, line=dict(color="white", width=1.5)),
                text=[str(int(n)) for n in notes],
                textposition="top center",
                textfont=dict(size=9, color=c),
                hovertemplate=f"<b>{agent}</b><br>%{{x}} : <b>%{{y}}</b>/20<extra></extra>",
            ))
        fig.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(family="DM Sans", color="#2c3e7a"),
            xaxis=dict(title="Évaluation", gridcolor="#f0f4ff", linecolor="#dce4f5"),
            yaxis=dict(title="Note /20", range=[-0.5,21], gridcolor="#f0f4ff", linecolor="#dce4f5"),
            legend=dict(bgcolor="rgba(255,255,255,0.95)", bordercolor="#dce4f5", borderwidth=1, font=dict(size=10)),
            hovermode="x unified", height=500, margin=dict(t=30,b=40,l=50,r=80),
            shapes=[
                dict(type="line",xref="paper",x0=0,x1=1,yref="y",y0=10,y1=10,line=dict(color="#e74c3c",width=1.5,dash="dot")),
                dict(type="line",xref="paper",x0=0,x1=1,yref="y",y0=14,y1=14,line=dict(color="#27ae60",width=1.5,dash="dot")),
            ],
            annotations=[
                dict(xref="paper",x=1.01,yref="y",y=10,text="Seuil 10",showarrow=False,font=dict(size=9,color="#e74c3c"),xanchor="left"),
                dict(xref="paper",x=1.01,yref="y",y=14,text="Seuil 14",showarrow=False,font=dict(size=9,color="#27ae60"),xanchor="left"),
            ],
        )
        st.plotly_chart(fig, use_container_width=True)

        # Mini stats sous les courbes
        st.markdown("**Récapitulatif des agents sélectionnés :**")
        mini_rows = []
        for agent in selected_agents:
            row   = df[df[name_col]==agent].iloc[0]
            vals  = [float(row[c]) for c in note_cols]
            moy   = round(np.mean(vals),2)
            ml, mc = mention_label(moy)
            mini_rows.append({"Agent":agent,"Moyenne":moy,"Max":max(vals),"Min":min(vals),"Mention":f'<span class="{mc}">{ml}</span>'})
        mini_df = pd.DataFrame(mini_rows)
        st.write(mini_df.to_html(escape=False, index=False), unsafe_allow_html=True)

# ───────────────────────────────────────────
# ONGLET 2 – TENDANCE GLOBALE
# ───────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">Tendance globale de la promotion</div>', unsafe_allow_html=True)
    st.caption("Moyenne et médiane par évaluation + zone min/max. Les zéros sont inclus dans les calculs.")

    df_fl  = df[note_cols].astype(float)
    moy_e  = df_fl.mean().values
    med_e  = df_fl.median().values
    max_e  = df_fl.max().values
    min_e  = df_fl.min().values
    std_e  = df_fl.std().values

    fig2 = go.Figure()
    # Zone min-max
    fig2.add_trace(go.Scatter(
        x=list(note_cols)+list(reversed(note_cols)),
        y=list(max_e)+list(reversed(min_e)),
        fill="toself", fillcolor="rgba(74,108,247,0.07)",
        line=dict(color="rgba(0,0,0,0)"), hoverinfo="skip", name="Zone Min–Max",
    ))
    # Zone ±1 écart-type
    fig2.add_trace(go.Scatter(
        x=list(note_cols)+list(reversed(note_cols)),
        y=list(moy_e+std_e)+list(reversed(moy_e-std_e)),
        fill="toself", fillcolor="rgba(74,108,247,0.12)",
        line=dict(color="rgba(0,0,0,0)"), hoverinfo="skip", name="Zone ±1 σ",
    ))
    fig2.add_trace(go.Scatter(
        x=note_cols, y=med_e, mode="lines+markers", name="Médiane",
        line=dict(color="#7b5ea7",width=2,dash="dash",shape="spline"),
        marker=dict(size=7,color="#7b5ea7"),
        hovertemplate="Médiane %{x} : <b>%{y:.2f}</b>/20<extra></extra>",
    ))
    fig2.add_trace(go.Scatter(
        x=note_cols, y=moy_e, mode="lines+markers+text", name="Moyenne",
        line=dict(color="#4a6cf7",width=3,shape="spline"),
        marker=dict(size=10,color="#4a6cf7",line=dict(color="white",width=2)),
        text=[f"{v:.1f}" for v in moy_e],
        textposition="top center", textfont=dict(size=10,color="#2c3e7a"),
        hovertemplate="Moyenne %{x} : <b>%{y:.2f}</b>/20<extra></extra>",
    ))
    fig2.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="DM Sans",color="#2c3e7a"),
        xaxis=dict(title="Évaluation",gridcolor="#f0f4ff",linecolor="#dce4f5"),
        yaxis=dict(title="Note /20",range=[-0.5,21],gridcolor="#f0f4ff",linecolor="#dce4f5"),
        legend=dict(bgcolor="rgba(255,255,255,0.95)",bordercolor="#dce4f5",borderwidth=1),
        hovermode="x unified", height=430, margin=dict(t=30,b=40,l=50,r=20),
        shapes=[dict(type="line",xref="paper",x0=0,x1=1,yref="y",y0=10,y1=10,line=dict(color="#e74c3c",width=1.2,dash="dot"))],
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Tableau récap par évaluation
    st.markdown("**Résumé statistique par évaluation :**")
    recap = pd.DataFrame({
        "Évaluation": note_cols,
        "Moyenne":    [round(v,2) for v in moy_e],
        "Médiane":    [round(v,2) for v in med_e],
        "Max":        [int(v) for v in max_e],
        "Min":        [int(v) for v in min_e],
        "Écart-type": [round(v,2) for v in std_e],
    })
    st.dataframe(recap, use_container_width=True, hide_index=True)

# ───────────────────────────────────────────
# ONGLET 3 – TABLEAU DES STATS
# ───────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">Statistiques détaillées par agent</div>', unsafe_allow_html=True)
    st.caption(f"Filtre actif : moyenne entre {note_range[0]} et {note_range[1]}")

    df_filtered = df_stats[
        (df_stats["Moyenne"] >= note_range[0]) &
        (df_stats["Moyenne"] <= note_range[1])
    ].sort_values("Moyenne", ascending=False).reset_index(drop=True)
    df_filtered.index += 1

    # Coloration manuelle (sans matplotlib)
    def style_row(row):
        styles = []
        for col in row.index:
            if col in ["Moyenne","Max","Min","Médiane"]:
                v = row[col]
                if v >= 16:   styles.append("background-color:#e6f4ea; color:#1e7e34")
                elif v >= 14: styles.append("background-color:#dbeafe; color:#1a56db")
                elif v >= 10: styles.append("background-color:#fef3c7; color:#92400e")
                else:         styles.append("background-color:#fee2e2; color:#b91c1c")
            else:
                styles.append("")
        return styles

    styled = (df_filtered
              .style
              .apply(style_row, axis=1)
              .format({"Moyenne":"{:.2f}","Médiane":"{:.2f}","Écart-type":"{:.2f}","Max":"{:.0f}","Min":"{:.0f}"}))

    st.dataframe(styled, use_container_width=True, height=500)

    # Export partiel filtré
    buf2 = io.BytesIO()
    with pd.ExcelWriter(buf2, engine="openpyxl") as w:
        df_filtered.to_excel(w, sheet_name="Stats filtrées", index=True)
    st.download_button("⬇️ Exporter ce tableau (Excel)", data=buf2.getvalue(),
        file_name="stats_filtrees.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ───────────────────────────────────────────
# ONGLET 4 – DISTRIBUTIONS
# ───────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-title">Distribution des notes</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        # Histogramme global
        fig3 = go.Figure(go.Histogram(
            x=all_vals, nbinsx=21,
            marker=dict(
                color=all_vals,
                colorscale=[[0,"#fee2e2"],[0.5,"#dbeafe"],[1,"#1a237e"]],
                line=dict(color="white",width=0.8),
            ),
            hovertemplate="Note %{x} : <b>%{y}</b> occurrences<extra></extra>",
        ))
        fig3.update_layout(
            title="Distribution de toutes les notes (0 inclus)",
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(family="DM Sans",color="#2c3e7a"),
            xaxis=dict(title="Note",gridcolor="#f0f4ff",dtick=1),
            yaxis=dict(title="Fréquence",gridcolor="#f0f4ff"),
            height=380, margin=dict(t=50,b=40), showlegend=False,
        )
        st.plotly_chart(fig3, use_container_width=True)

    with c2:
        # Camembert mentions
        def cat(n):
            if n>=16:  return "Très Bien (≥16)"
            elif n>=14: return "Bien (14–15)"
            elif n>=10: return "Assez Bien (10–13)"
            else:       return "Insuffisant (<10)"
        counts = pd.Series([cat(m) for m in df_stats["Moyenne"]]).value_counts()
        fig4 = go.Figure(go.Pie(
            labels=counts.index, values=counts.values, hole=0.48,
            marker=dict(colors=["#2d6a4f","#1a56db","#92400e","#b91c1c"], line=dict(color="white",width=2)),
            textinfo="label+percent+value",
            hovertemplate="%{label}<br>%{value} agents (%{percent})<extra></extra>",
        ))
        fig4.update_layout(
            title="Répartition par mention (moyenne générale)",
            paper_bgcolor="white", font=dict(family="DM Sans",color="#2c3e7a"),
            height=380, margin=dict(t=50,b=40),
        )
        st.plotly_chart(fig4, use_container_width=True)

    # Boîte à moustaches par évaluation
    st.markdown('<div class="section-title">Boîtes à moustaches par évaluation</div>', unsafe_allow_html=True)
    fig_box = go.Figure()
    for col in note_cols:
        vals_col = df[col].astype(float).tolist()
        fig_box.add_trace(go.Box(
            y=vals_col, name=col, boxpoints="all", jitter=0.4,
            marker=dict(size=5, opacity=0.6),
            line=dict(color="#4a6cf7"),
            fillcolor="rgba(74,108,247,0.1)",
            hovertemplate=f"<b>{col}</b><br>Note : %{{y}}<extra></extra>",
        ))
    fig_box.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="DM Sans",color="#2c3e7a"),
        xaxis=dict(title="Évaluation",gridcolor="#f0f4ff"),
        yaxis=dict(title="Note /20",range=[-0.5,21],gridcolor="#f0f4ff"),
        showlegend=False, height=420, margin=dict(t=20,b=40,l=50,r=20),
    )
    st.plotly_chart(fig_box, use_container_width=True)

    # Violin
    st.markdown('<div class="section-title">Violin plot — densité des notes</div>', unsafe_allow_html=True)
    fig_vio = go.Figure()
    for i, col in enumerate(note_cols):
        vals_col = df[col].astype(float).tolist()
        c = px.colors.qualitative.Pastel[i % len(px.colors.qualitative.Pastel)]
        fig_vio.add_trace(go.Violin(
            y=vals_col, name=col, box_visible=True, meanline_visible=True,
            fillcolor=c, opacity=0.7, line_color="#2c3e7a",
            hovertemplate=f"<b>{col}</b><br>Note : %{{y}}<extra></extra>",
        ))
    fig_vio.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="DM Sans",color="#2c3e7a"),
        xaxis=dict(title="Évaluation",gridcolor="#f0f4ff"),
        yaxis=dict(title="Note /20",range=[-0.5,21],gridcolor="#f0f4ff"),
        showlegend=False, height=420, margin=dict(t=20,b=40,l=50,r=20),
    )
    st.plotly_chart(fig_vio, use_container_width=True)

# ───────────────────────────────────────────
# ONGLET 5 – HEATMAP
# ───────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-title">Carte de chaleur — Notes par agent et par évaluation</div>', unsafe_allow_html=True)
    st.caption("Lecture : plus la couleur est foncée, plus la note est élevée. Les 0 sont en rouge clair.")

    heat = df.set_index(name_col)[note_cols].astype(float)
    fig5 = go.Figure(go.Heatmap(
        z=heat.values, x=note_cols, y=heat.index.tolist(),
        colorscale=[
            [0.0,  "#fee2e2"],
            [0.01, "#fecaca"],
            [0.3,  "#bfdbfe"],
            [0.6,  "#4a6cf7"],
            [1.0,  "#1a237e"],
        ],
        text=heat.values.astype(int),
        texttemplate="%{text}",
        textfont=dict(size=10, color="#1a1a2e"),
        hovertemplate="<b>%{y}</b><br>%{x} : <b>%{z}</b>/20<extra></extra>",
        colorbar=dict(title="Note /20", tickvals=[0,5,10,14,16,20]),
        zmin=0, zmax=20,
    ))
    fig5.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="DM Sans",color="#2c3e7a"),
        xaxis=dict(side="top", tickfont=dict(size=11)),
        yaxis=dict(autorange="reversed", tickfont=dict(size=10)),
        height=max(400, len(agents)*30),
        margin=dict(t=50,b=20,l=240,r=20),
    )
    st.plotly_chart(fig5, use_container_width=True)

    # Heatmap des écarts à la moyenne de l'évaluation
    st.markdown('<div class="section-title">Écarts à la moyenne de chaque évaluation</div>', unsafe_allow_html=True)
    moy_par_eval = df[note_cols].astype(float).mean()
    ecarts = df[note_cols].astype(float).subtract(moy_par_eval, axis=1)
    ecarts_heat = ecarts.set_index(df[name_col])
    fig6 = go.Figure(go.Heatmap(
        z=ecarts_heat.values, x=note_cols, y=ecarts_heat.index.tolist(),
        colorscale="RdBu",
        text=[[f"{v:+.1f}" for v in row] for row in ecarts_heat.values],
        texttemplate="%{text}",
        textfont=dict(size=9),
        hovertemplate="<b>%{y}</b><br>%{x} : écart <b>%{z:+.2f}</b><extra></extra>",
        colorbar=dict(title="Écart"),
        zmid=0,
    ))
    fig6.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="DM Sans",color="#2c3e7a"),
        xaxis=dict(side="top"),
        yaxis=dict(autorange="reversed"),
        height=max(400, len(agents)*30),
        margin=dict(t=50,b=20,l=240,r=20),
    )
    st.plotly_chart(fig6, use_container_width=True)

# ───────────────────────────────────────────
# ONGLET 6 – CLASSEMENT & PODIUM
# ───────────────────────────────────────────
with tab6:
    st.markdown('<div class="section-title">🏆 Classement général</div>', unsafe_allow_html=True)

    df_ranked = df_stats.sort_values("Moyenne", ascending=False).reset_index(drop=True)
    df_ranked.index += 1

    # Podium top 3
    if len(df_ranked) >= 3:
        p1, p2, p3 = st.columns([1,1,1])
        for col, rank, medal, bg in [(p2,1,"🥇","#FFF9C4"),(p1,2,"🥈","#F5F5F5"),(p3,3,"🥉","#FBE9E7")]:
            r = df_ranked.iloc[rank-1]
            ml, mc = mention_label(r["Moyenne"])
            col.markdown(f"""
            <div style="background:{bg};border-radius:16px;padding:20px;text-align:center;box-shadow:0 4px 16px rgba(0,0,0,0.08);margin-bottom:12px;">
              <div style="font-size:2.5rem;">{medal}</div>
              <div style="font-weight:700;color:#2c3e7a;font-size:1rem;margin-top:6px;">{r['Agent']}</div>
              <div style="font-size:2rem;font-weight:700;color:#4a6cf7;margin-top:4px;">{r['Moyenne']:.2f}</div>
              <div style="font-size:0.8rem;color:#6b7db3;">/ 20</div>
              <div style="margin-top:6px;"><span class="{mc}">{ml}</span></div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Graphique bar horizontal classement
    fig_bar = go.Figure()
    colors_bar = []
    for m in df_ranked["Moyenne"]:
        if m>=16:   colors_bar.append("#2d6a4f")
        elif m>=14: colors_bar.append("#1a56db")
        elif m>=10: colors_bar.append("#92400e")
        else:       colors_bar.append("#b91c1c")

    fig_bar.add_trace(go.Bar(
        x=df_ranked["Moyenne"],
        y=df_ranked["Agent"],
        orientation="h",
        marker=dict(color=colors_bar, line=dict(color="white",width=0.5)),
        text=[f"{v:.2f}" for v in df_ranked["Moyenne"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Moyenne : <b>%{x:.2f}</b>/20<extra></extra>",
    ))
    fig_bar.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="DM Sans",color="#2c3e7a"),
        xaxis=dict(title="Moyenne /20",range=[0,22],gridcolor="#f0f4ff"),
        yaxis=dict(autorange="reversed",tickfont=dict(size=11)),
        height=max(400, len(agents)*30),
        margin=dict(t=20,b=40,l=220,r=60),
        showlegend=False,
        shapes=[
            dict(type="line",xref="x",x0=10,x1=10,yref="paper",y0=0,y1=1,line=dict(color="#e74c3c",width=1.5,dash="dot")),
            dict(type="line",xref="x",x0=14,x1=14,yref="paper",y0=0,y1=1,line=dict(color="#27ae60",width=1.5,dash="dot")),
        ],
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Progression : meilleure et moins bonne note de chaque agent
    st.markdown('<div class="section-title">Amplitude des notes (Max – Min)</div>', unsafe_allow_html=True)
    df_amp = df_stats.sort_values("Moyenne", ascending=False).copy()
    fig_amp = go.Figure()
    fig_amp.add_trace(go.Bar(
        x=df_amp["Agent"], y=df_amp["Max"]-df_amp["Min"],
        name="Amplitude (Max–Min)",
        marker=dict(color="rgba(74,108,247,0.7)", line=dict(color="white",width=0.5)),
        hovertemplate="<b>%{x}</b><br>Amplitude : <b>%{y}</b> pts<extra></extra>",
    ))
    fig_amp.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="DM Sans",color="#2c3e7a"),
        xaxis=dict(tickangle=-40,tickfont=dict(size=9),gridcolor="#f0f4ff"),
        yaxis=dict(title="Points d'écart",gridcolor="#f0f4ff"),
        height=380, margin=dict(t=20,b=100,l=50,r=20), showlegend=False,
    )
    st.plotly_chart(fig_amp, use_container_width=True)

# ── EXPORT GLOBAL ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-title">💾 Export complet</div>', unsafe_allow_html=True)
buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Données brutes", index=False)
    df_stats.to_excel(writer, sheet_name="Statistiques", index=False)
    df_ranked.to_excel(writer, sheet_name="Classement", index=True)
st.download_button(
    label="⬇️  Télécharger tout (Excel — 3 feuilles)",
    data=buf.getvalue(),
    file_name="stats_notes_complet.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
st.caption("Application Streamlit · N agents × M notes · Zéros = notes réelles · v2.0")
