import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# 1. Configuration
TICKERS = ["NVDA", "TSLA", "AAPL", "MSFT", "BTC-USD", "EURUSD=X"]
DATA_FILE = "data/market_history.csv"

# Création du dossier data si inexistant
os.makedirs("data", exist_ok=True)

print(f"🤖 Lancement du Bot GeoQuant - {datetime.now()}")

# 2. Chargement de l'existant (si disponible)
if os.path.exists(DATA_FILE):
    df_existing = pd.read_csv(DATA_FILE)
    # On convertit la date pour être sûr
    df_existing['Date'] = pd.to_datetime(df_existing['Date'], utc=True)
    print(f"📚 Historique chargé : {len(df_existing)} lignes.")
else:
    df_existing = pd.DataFrame(columns=["Date", "Ticker", "Close", "Volume"])
    print("✨ Création d'un nouveau fichier d'historique.")

new_data = []

# 3. La Récolte
for ticker in TICKERS:
    try:
        print(f"  🎣 Récupération de {ticker}...")
        stock = yf.Ticker(ticker)
        # On prend juste le dernier jour (1d)
        hist = stock.history(period="1d")
        
        if not hist.empty:
            # Nettoyage
            hist = hist.reset_index()
            # On s'assure que la date est en UTC pour éviter les doublons flous
            current_date = pd.to_datetime(hist['Date'].iloc[0], utc=True)
            close_price = hist['Close'].iloc[0]
            volume = hist['Volume'].iloc[0]
            
            # Vérification anti-doublon basique
            # Est-ce que ce ticker a déjà une entrée pour cette date précise ?
            already_exists = False
            if not df_existing.empty:
                mask = (df_existing['Ticker'] == ticker) & (df_existing['Date'] == current_date)
                if not df_existing[mask].empty:
                    already_exists = True
            
            if not already_exists:
                new_data.append({
                    "Date": current_date,
                    "Ticker": ticker,
                    "Close": close_price,
                    "Volume": volume
                })
                print(f"    ✅ Donnée ajoutée : {close_price:.2f}")
            else:
                print(f"    ⚠️ Déjà en base pour cette date.")
        else:
            print(f"    ❌ Pas de données aujourd'hui (Bourse fermée ?).")
            
    except Exception as e:
        print(f"    ❌ Erreur sur {ticker}: {e}")

# 4. Sauvegarde
if new_data:
    df_new = pd.DataFrame(new_data)
    # Concaténation
    df_final = pd.concat([df_existing, df_new], ignore_index=True)
    # Tri par date
    df_final = df_final.sort_values(by="Date")
    # Sauvegarde CSV
    df_final.to_csv(DATA_FILE, index=False)
    print(f"💾 Sauvegarde terminée. {len(new_data)} nouvelles lignes ajoutées.")
else:
    print("💤 Aucune nouvelle donnée à sauvegarder.")