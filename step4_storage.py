import streamlit as st
import pandas as pd
import yfinance as yf
import duckdb
import plotly.express as px

st.set_page_config(layout="wide", page_title="GeoQuant Storage")
st.title("🦆 Le Coffre-fort du Quant (DuckDB)")

# 1. Connexion à la base de données (fichier local 'geoquant.duckdb')
# Si le fichier n'existe pas, il est créé automatiquement.
con = duckdb.connect(database='geoquant.duckdb', read_only=False)

# 2. Initialisation de la table (si elle n'existe pas encore)
# On stocke : Date, Ticker, Close, Volume
con.execute("""
    CREATE TABLE IF NOT EXISTS market_data (
        Date TIMESTAMP,
        Ticker VARCHAR,
        Close FLOAT,
        Volume BIGINT,
        PRIMARY KEY (Date, Ticker)
    )
""")

# --- PARTIE GAUCHE : INGESTION (ETL) ---
col_ingest, col_db = st.columns([1, 2])

with col_ingest:
    st.subheader("📥 Ingestion (Yahoo)")
    ticker = st.text_input("Ticker à sauvegarder", "NVDA")
    
    if st.button("Télécharger & Archiver"):
        with st.spinner(f"Récupération de {ticker}..."):
            # A. On récupère la donnée brute
            stock = yf.Ticker(ticker)
            df = stock.history(period="1mo") # On prend 1 mois pour tester
            
            if not df.empty:
                # B. Préparation pour DuckDB
                # Reset index pour avoir la Date en colonne, pas en index
                df = df.reset_index()
                # On ne garde que ce qui nous intéresse
                df_clean = df[['Date', 'Close', 'Volume']].copy()
                df_clean['Ticker'] = ticker # On ajoute la colonne Ticker
                
                # C. Insertion Magique (Upsert pour éviter les doublons)
                # DuckDB peut lire directement un DataFrame pandas !
                try:
                    # On supprime d'abord les données existantes pour ce ticker/date pour éviter les doublons (méthode brutale mais simple)
                    con.execute(f"DELETE FROM market_data WHERE Ticker = '{ticker}' AND Date >= '{df_clean['Date'].min()}'")
                    
                    # Insertion massive
                    con.execute("INSERT INTO market_data SELECT Date, Ticker, Close, Volume FROM df_clean")
                    st.success(f"✅ {len(df_clean)} jours archivés pour {ticker} !")
                except Exception as e:
                    st.error(f"Erreur SQL : {e}")
            else:
                st.warning("Pas de données trouvées.")

# --- PARTIE DROITE : ANALYSE (DATABASE) ---
with col_db:
    st.subheader("📊 Contenu du Coffre-fort")
    
    # A. Lecture de la base
    # Regarde cette syntaxe SQL simple
    df_stored = con.execute("SELECT * FROM market_data ORDER BY Date DESC").df()
    
    if not df_stored.empty:
        # B. Statistiques
        stats = con.execute("""
            SELECT 
                Ticker, 
                COUNT(*) as Jours, 
                MIN(Date) as Debut, 
                MAX(Date) as Fin,
                AVG(Close) as Prix_Moyen
            FROM market_data 
            GROUP BY Ticker
        """).df()
        
        st.dataframe(stats, use_container_width=True)
        
        # C. Visualisation multi-ticker depuis la base
        st.markdown("### Comparaison Historique")
        tickers_avail = df_stored['Ticker'].unique()
        selection = st.multiselect("Comparer", tickers_avail, default=tickers_avail)
        
        if selection:
            df_viz = df_stored[df_stored['Ticker'].isin(selection)]
            fig = px.line(df_viz, x='Date', y='Close', color='Ticker', title="Prix de clôture (Source: DuckDB)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Petit bonus volume
            st.bar_chart(df_viz, x="Date", y="Volume", color="Ticker", stack=False)
            
    else:
        st.info("La base est vide. Utilise le panneau de gauche pour la remplir.")