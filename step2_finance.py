import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(layout="wide", page_title="GeoQuant Market")

st.title("📈 Market Watcher")

# 1. Sidebar de configuration
st.sidebar.header("Configuration")
ticker_symbol = st.sidebar.text_input("Symbole (Ticker)", value="BTC-USD")
period = st.sidebar.selectbox("Période", ["1mo", "3mo", "6mo", "1y", "5y", "max"], index=3)

# 2. Récupération de la donnée (C'est ici que la magie opère)
@st.cache_data # Optimisation : garde les données en mémoire pour ne pas spammer Yahoo si on clique juste sur un bouton
def get_data(ticker, period):
    stock = yf.Ticker(ticker)
    # history() renvoie un DataFrame Pandas (tableau Excel sous stéroïdes)
    df = stock.history(period=period)
    return df, stock.info

try:
    # On appelle la fonction
    data, info = get_data(ticker_symbol, period)
    
    # 3. Affichage des infos de base
    col1, col2, col3 = st.columns(3)
    # .get() permet d'éviter de planter si l'info n'existe pas
    col1.metric("Prix Actuel", f"{data['Close'].iloc[-1]:.2f}", f"Dernière clôture")
    col2.metric("Haut (Période)", f"{data['High'].max():.2f}")
    col3.metric("Bas (Période)", f"{data['Low'].min():.2f}")

    # 4. Graphique Avancé (Bougies / Candlestick)
    st.subheader(f"Évolution de {ticker_symbol}")
    
    # On utilise Plotly ici au lieu du st.line_chart basique pour avoir les bougies
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'])])
    
    fig.update_layout(height=600, template="seaborn") # Un look un peu pro
    st.plotly_chart(fig, use_container_width=True)

    # 5. Inspection des données brutes (Pour comprendre ce qu'on manipule)
    with st.expander("Voir les données brutes (DataFrame)"):
        st.write(data)

except Exception as e:
    st.error(f"Erreur : Impossible de trouver le ticker '{ticker_symbol}'. Vérifie sur Yahoo Finance.")
    st.caption(f"Détail technique : {e}")