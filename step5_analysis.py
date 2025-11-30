import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide", page_title="GeoQuant Lab")
st.title("⚗️ Laboratoire d'Analyse (Z-Score)")

# 1. Chargement des données (Source: Le travail du Bot)
DATA_URL = "data/market_history.csv"

@st.cache_data
def load_data():
    try:
        # On lit le CSV local (résultat du git pull)
        df = pd.read_csv(DATA_URL)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except FileNotFoundError:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.sidebar.success(f"Données chargées : {len(df)} points")
    
    # 2. Sélecteur de Tickers
    tickers = df['Ticker'].unique()
    selected_tickers = st.multiselect("Choisis les actifs à comparer", tickers, default=tickers[:2])
    
    if selected_tickers:
        # Filtrage
        df_filtered = df[df['Ticker'].isin(selected_tickers)].copy()
        
        # 3. La Formule Magique : Z-Score
        # Z = (Prix - Moyenne) / Écart-type
        # Cela transforme le prix en "Niveau de rareté"
        df_filtered['Z_Score'] = df_filtered.groupby('Ticker')['Close'].transform(
            lambda x: (x - x.mean()) / x.std()
        )
        
        # 4. Visualisation Normalisée
        st.subheader("Comparaison Normalisée (Z-Score)")
        st.info("ℹ️ 0 = Prix Moyen. +2 = Très cher (Rare). -2 = Très bas (Rare).")
        
        fig = px.line(df_filtered, x='Date', y='Z_Score', color='Ticker', 
                      title="Qui surperforme sa propre moyenne ?")
        
        # On ajoute des zones de "Normalité"
        fig.add_hrect(y0=-1, y1=1, line_width=0, fillcolor="green", opacity=0.1, annotation_text="Zone Normale")
        st.plotly_chart(fig, use_container_width=True)
        
        # 5. Matrice de Corrélation
        # Est-ce que quand NVDA monte, BTC monte aussi ?
        st.subheader("Matrice de Corrélation")
        
        # On pivote le tableau pour avoir les tickers en colonnes
        df_pivot = df_filtered.pivot(index='Date', columns='Ticker', values='Close')
        
        # Calcul de la corrélation (Pearson)
        corr_matrix = df_pivot.corr()
        
        fig_corr = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu_r', range_color=[-1, 1])
        st.plotly_chart(fig_corr)

else:
    st.warning("⚠️ Pas de données trouvées. Fais un 'git pull' pour récupérer le travail du bot !")