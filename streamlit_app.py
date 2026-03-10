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
  .main, .block-container { background-color: #ffffff !important; }
  section[data-testid="stSidebar"] { background: linear-gradient(160deg, #f0f4ff 0%, #e8f0fe 100%); border-right: 1px solid #dce4f5; }
  .main-title { font-family: 'DM Serif Display', serif; font-size: 2.4rem; color: #2c3e7a; margin-bottom: 0.2rem; }
  .sub-title { font-size: 1rem; color: #6b7db3; margin-bottom: 2rem; }
  .kpi-card { background:#ffffff; border:1px solid #e0e8ff; border-radius:14px; padding:20px 24px; text-align:center; box-shadow:0 2px 12px rgba(44,62,122,0.07); }
  .kpi-value { font-size:2rem; font-weight:700; color:#2c3e7a; line-height:1; }
  .kpi-label { font-size:0.82rem; color:#7a8db3; margin-top:6px; text-transform:uppercase; letter-spacing:0.8px; font-weight:500; }
  .kpi-sub   { font-size:0.75rem; color:#a0aec0; margin-top:3px; }
  .section-title { font-family:'DM Serif Display',serif; font-size:1.35rem; color:#2c3e7a; margin-top:2rem; margin-bottom:0.5rem; border-left:4px solid #4a6cf7; padding-left:12px; }
  .stDownloadButton > button { background:linear-gradient(135deg,#4a6cf7,#7b5ea7); color:white; border:none; border-radius:8px; font-weight:600; padding:10px 20px; }
</style>
""", unsafe_allow_html=True)

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

def mention(n):
    if n>=16: return "Très Bien"
    elif n>=14: return "Bien"
    elif n>=10: return "Assez Bien"
    else: return "Insuffisant"

def get_note_cols(df):
    return [c for c in df.columns if c != df.columns[0]]

def compute_stats(df, note_cols, name_col):
    rows = []
    for _, row in df.iterrows():
        vals = [float(row[c]) for c in note_cols]
        nz = [v for v in vals if v > 0]
        moy = round(np.mean(nz),2) if nz else 0
        rows.append({"Agent":row[name_col],"Moy. (hors 0)":moy,"Moy. globale":round(np.mean(vals),2),"Max":max(vals),"Min":min(vals),"Médiane":round(np.median(vals),2),"Écart-type":round(np.std(vals),2),"Notes > 0":len(nz),"Nb total notes":len(vals),"Mention":mention(moy)})
    return pd.DataFrame(rows)

with st.sidebar:
    st.markdown("### 📂 Source des données")
    uploaded = st.file_uploader("Importer un fichier Excel (.xlsx / .xls)", type=["xlsx","xls"], help="1ère colonne = noms · colonnes suivantes = notes")
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
    st.sidebar.info("📌 Données par défaut utilisées (aucun fichier importé)")

name_col = df.columns[0]
note_cols = get_note_cols(df)
agents = df[name_col].tolist()

with st.sidebar:
    st.markdown("### 🔍 Filtres")
    selected_agents = st.multiselect("Agents — courbes individuelles", options=agents, default=agents[:5])
    note_range = st.slider("Filtre moyenne (tableau)", 0, 20, (0, 20))

st.markdown('<div class="main-title">📊 Tableau de Bord — Analyse des Notes</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">{df.shape[0]} agents · {len(note_cols)} évaluations · Données dynamiques (N agents × M notes)</div>', unsafe_allow_html=True)

all_vals = df[note_cols].values.flatten().astype(float)
all_nz = all_vals[all_vals > 0]
df_stats = compute_stats(df, note_cols, name_col)

k1,k2,k3,k4,k5 = st.columns(5)
kpi_data = [
    (round(np.mean(all_nz),2),"Moyenne Générale","hors absences"),
    (round(df[note_cols].replace(0,np.nan).astype(float).max(axis=1).mean(),2),"Moy. Max/Agent","meilleurs scores"),
    (round(df[note_cols].replace(0,np.nan).astype(float).min(axis=1).mean(),2),"Moy. Min/Agent","scores les plus bas"),
    (int((df[note_cols]==20).sum().sum()),"Notes 20/20","scores parfaits"),
    (int((df[note_cols]==0).sum().sum()),"Notes = 0","absences / manquants"),
]
for col,(val,label,sub) in zip([k1,k2,k3,k4,k5],kpi_data):
    col.markdown(f'<div class="kpi-card"><div class="kpi-value">{val}</div><div class="kpi-label">{label}</div><div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<div class="section-title">📈 Évolution individuelle des notes</div>', unsafe_allow_html=True)
if not selected_agents:
    st.info("👈 Sélectionnez au moins un agent dans le panneau latéral.")
else:
    palette = (px.colors.qualitative.Pastel + px.colors.qualitative.Safe + px.colors.qualitative.Vivid + px.colors.qualitative.Dark24)
    fig = go.Figure()
    for i, agent in enumerate(selected_agents):
        row = df[df[name_col]==agent].iloc[0]
        notes = [float(row[c]) for c in note_cols]
        c = palette[i % len(palette)]
        fig.add_trace(go.Scatter(x=note_cols, y=notes, mode="lines+markers+text", name=agent, line=dict(color=c,width=2.5,shape="spline"), marker=dict(size=8,color=c,line=dict(color="white",width=1.5)), text=[str(int(n)) for n in notes], textposition="top center", textfont=dict(size=9,color=c), hovertemplate=f"<b>{agent}</b><br>%{{x}} : <b>%{{y}}</b>/20<extra></extra>"))
    fig.update_layout(paper_bgcolor="white",plot_bgcolor="white",font=dict(family="DM Sans",color="#2c3e7a"),xaxis=dict(title="Évaluation",gridcolor="#f0f4ff",linecolor="#dce4f5"),yaxis=dict(title="Note /20",range=[-0.5,21],gridcolor="#f0f4ff",linecolor="#dce4f5"),legend=dict(bgcolor="rgba(255,255,255,0.95)",bordercolor="#dce4f5",borderwidth=1,font=dict(size=10)),hovermode="x unified",height=480,margin=dict(t=30,b=40,l=50,r=20),shapes=[dict(type="line",xref="paper",x0=0,x1=1,yref="y",y0=10,y1=10,line=dict(color="#e74c3c",width=1.2,dash="dot")),dict(type="line",xref="paper",x0=0,x1=1,yref="y",y0=14,y1=14,line=dict(color="#27ae60",width=1.2,dash="dot"))],annotations=[dict(xref="paper",x=1.01,yref="y",y=10,text="Seuil 10",showarrow=False,font=dict(size=9,color="#e74c3c"),xanchor="left"),dict(xref="paper",x=1.01,yref="y",y=14,text="Seuil 14",showarrow=False,font=dict(size=9,color="#27ae60"),xanchor="left")])
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="section-title">🌐 Tendance globale de la promotion</div>', unsafe_allow_html=True)
df_nz = df[note_cols].replace(0,np.nan).astype(float)
moy_e=df_nz.mean().values; med_e=df_nz.median().values; max_e=df_nz.max().values; min_e=df_nz.min().values
fig2=go.Figure()
fig2.add_trace(go.Scatter(x=list(note_cols)+list(reversed(note_cols)),y=list(max_e)+list(reversed(min_e)),fill="toself",fillcolor="rgba(74,108,247,0.08)",line=dict(color="rgba(0,0,0,0)"),hoverinfo="skip",name="Zone Min–Max"))
fig2.add_trace(go.Scatter(x=note_cols,y=med_e,mode="lines+markers",name="Médiane",line=dict(color="#7b5ea7",width=2,dash="dash",shape="spline"),marker=dict(size=7,color="#7b5ea7"),hovertemplate="Médiane %{x} : <b>%{y:.2f}</b>/20<extra></extra>"))
fig2.add_trace(go.Scatter(x=note_cols,y=moy_e,mode="lines+markers+text",name="Moyenne",line=dict(color="#4a6cf7",width=3,shape="spline"),marker=dict(size=10,color="#4a6cf7",line=dict(color="white",width=2)),text=[f"{v:.1f}" for v in moy_e],textposition="top center",textfont=dict(size=10,color="#2c3e7a"),hovertemplate="Moyenne %{x} : <b>%{y:.2f}</b>/20<extra></extra>"))
fig2.update_layout(paper_bgcolor="white",plot_bgcolor="white",font=dict(family="DM Sans",color="#2c3e7a"),xaxis=dict(title="Évaluation",gridcolor="#f0f4ff",linecolor="#dce4f5"),yaxis=dict(title="Note /20",range=[0,21],gridcolor="#f0f4ff",linecolor="#dce4f5"),legend=dict(bgcolor="rgba(255,255,255,0.95)",bordercolor="#dce4f5",borderwidth=1),hovermode="x unified",height=400,margin=dict(t=30,b=40,l=50,r=20))
st.plotly_chart(fig2, use_container_width=True)

st.markdown('<div class="section-title">📋 Statistiques détaillées par agent</div>', unsafe_allow_html=True)
df_filtered=df_stats[(df_stats["Moy. (hors 0)"]>=note_range[0])&(df_stats["Moy. (hors 0)"]<=note_range[1])].sort_values("Moy. (hors 0)",ascending=False).reset_index(drop=True)
df_filtered.index+=1
st.dataframe(df_filtered.style.background_gradient(subset=["Moy. (hors 0)","Max"],cmap="Blues").format({"Moy. (hors 0)":"{:.2f}","Moy. globale":"{:.2f}","Médiane":"{:.2f}","Écart-type":"{:.2f}"}),use_container_width=True,height=460)

st.markdown('<div class="section-title">📊 Distribution & Répartition par mention</div>', unsafe_allow_html=True)
ca,cb=st.columns(2)
with ca:
    fig3=go.Figure(go.Histogram(x=all_nz,nbinsx=20,marker=dict(color=all_nz,colorscale=[[0,"#e8f0fe"],[0.5,"#4a6cf7"],[1,"#2c3e7a"]],line=dict(color="white",width=0.8)),hovertemplate="Note : %{x}<br>Fréquence : %{y}<extra></extra>"))
    fig3.update_layout(title="Distribution de toutes les notes (hors 0)",paper_bgcolor="white",plot_bgcolor="white",font=dict(family="DM Sans",color="#2c3e7a"),xaxis=dict(title="Note",gridcolor="#f0f4ff"),yaxis=dict(title="Fréquence",gridcolor="#f0f4ff"),height=360,margin=dict(t=50,b=40),showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)
with cb:
    def cat(n):
        if n>=16: return "Très Bien (≥16)"
        elif n>=14: return "Bien (14–15)"
        elif n>=10: return "Assez Bien (10–13)"
        else: return "Insuffisant (<10)"
    counts=pd.Series([cat(m) for m in df_stats["Moy. (hors 0)"]]).value_counts()
    fig4=go.Figure(go.Pie(labels=counts.index,values=counts.values,hole=0.45,marker=dict(colors=["#2d6a4f","#1a6090","#b7770d","#b71c1c"],line=dict(color="white",width=2)),textinfo="label+percent",hovertemplate="%{label}<br>%{value} agents (%{percent})<extra></extra>"))
    fig4.update_layout(title="Répartition par mention",paper_bgcolor="white",font=dict(family="DM Sans",color="#2c3e7a"),height=360,margin=dict(t=50,b=40))
    st.plotly_chart(fig4, use_container_width=True)

st.markdown('<div class="section-title">🔥 Carte de chaleur des notes</div>', unsafe_allow_html=True)
heat=df.set_index(name_col)[note_cols].astype(float)
fig5=go.Figure(go.Heatmap(z=heat.values,x=note_cols,y=heat.index.tolist(),colorscale=[[0.0,"#f8f9fa"],[0.001,"#fdecea"],[0.25,"#fce4d6"],[0.5,"#aed6f1"],[0.75,"#4a6cf7"],[1.0,"#1a237e"]],text=heat.values.astype(int),texttemplate="%{text}",textfont=dict(size=10,color="#2c3e7a"),hovertemplate="<b>%{y}</b><br>%{x} : <b>%{z}</b>/20<extra></extra>",colorbar=dict(title="Note")))
fig5.update_layout(paper_bgcolor="white",plot_bgcolor="white",font=dict(family="DM Sans",color="#2c3e7a"),xaxis=dict(side="top"),yaxis=dict(autorange="reversed"),height=max(350,len(agents)*28),margin=dict(t=40,b=20,l=230,r=20))
st.plotly_chart(fig5, use_container_width=True)

st.markdown('<div class="section-title">💾 Exporter</div>', unsafe_allow_html=True)
buf=io.BytesIO()
with pd.ExcelWriter(buf,engine="openpyxl") as writer:
    df.to_excel(writer,sheet_name="Données brutes",index=False)
    df_stats.to_excel(writer,sheet_name="Statistiques",index=False)
st.download_button(label="⬇️  Télécharger les statistiques (Excel)",data=buf.getvalue(),file_name="stats_notes.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
st.markdown("<br>", unsafe_allow_html=True)
st.caption("Application Streamlit · N agents × M notes · Fond blanc · v1.0")
