import streamlit as st
import pandas as pd
import numpy as np

# 1. Configuration de la page
st.set_page_config(page_title="GeoQuant Proto", layout="wide")

st.title("🌍 GeoQuant : Le début de l'aventure (update)")
st.write("Bienvenue dans ton dashboard personnel.")

# 2. Sidebar (La télécommande)
st.sidebar.header("Paramètres")
volatilite = st.sidebar.slider("Niveau d'instabilité du monde", 0.0, 1.0, 0.1)
jours = st.sidebar.number_input("Horizon de prédiction (jours)", min_value=10, value=100)

# 3. Simulation de données (Pour tester sans Internet)
# On crée des dates
dates = pd.date_range(start="2024-01-01", periods=jours)
# On génère du bruit aléatoire (Random Walk)
noise = np.random.normal(0, volatilite, size=(jours, 2))
# On cumule pour faire des courbes
data = pd.DataFrame(np.cumsum(noise, axis=0), index=dates, columns=['Indice Tech (US)', 'Tension Géopolitique'])

# 4. Affichage des KPIs (Key Performance Indicators)
col1, col2 = st.columns(2)
# On prend la dernière valeur de la liste (.iloc[-1])
valeur_tech = data['Indice Tech (US)'].iloc[-1]
valeur_geo = data['Tension Géopolitique'].iloc[-1]

col1.metric("Indice Tech", f"{valeur_tech:.2f}", f"{valeur_tech * 0.1:.2f} pts")
col2.metric("Tension Géo", f"{valeur_geo:.2f}", f"{valeur_geo * -0.1:.2f} pts")

# 5. Le Graphique Interactif
st.line_chart(data)

# 6. Un petit bouton pour le fun
if st.button('Lancer une simulation de crise'):
    st.error("⚠️ ALERTE : Krach boursier simulé !")