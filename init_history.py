import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# Configuration
TICKERS = ["NVDA", "TSLA", "AAPL", "MSFT", "BTC-USD", "EURUSD=X"]
DATA_FILE = "data/market_history.csv"

print("🚀 Lancement de l'initialisation massive...")

all_data = []

for ticker in TICKERS:
    print(f"  📥 Téléchargement de l'historique (6 mois) pour {ticker}...")
    try:
        stock = yf.Ticker(ticker)
        # C'est ici que ça change : on demande 6 mois ("6mo") au lieu de 1 jour ("1d")
        hist = stock.history(period="6mo")
        
        if not hist.empty:
            hist = hist.reset_index()
            # Nettoyage des colonnes
            hist['Ticker'] = ticker
            
            # On standardise la date (UTC)
            hist['Date'] = pd.to_datetime(hist['Date'], utc=True)
            
            # On ne garde que les colonnes utiles
            hist_clean = hist[['Date', 'Ticker', 'Close', 'Volume']]
            all_data.append(hist_clean)
            print(f"    ✅ {len(hist_clean)} lignes récupérées.")
        else:
            print(f"    ⚠️ Aucune donnée pour {ticker}")
            
    except Exception as e:
        print(f"    ❌ Erreur : {e}")

# Assemblage et Sauvegarde
if all_data:
    print("💾 Fusion et écriture du fichier...")
    df_final = pd.concat(all_data, ignore_index=True)
    
    # Création du dossier si besoin
    os.makedirs("data", exist_ok=True)
    
    # Sauvegarde (On écrase l'ancien fichier, c'est un reset)
    df_final.sort_values(by="Date", inplace=True)
    df_final.to_csv(DATA_FILE, index=False)
    print(f"✨ Terminé ! Fichier {DATA_FILE} généré avec {len(df_final)} lignes.")
else:
    print("❌ Échec total. Aucune donnée récupérée.")