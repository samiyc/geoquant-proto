import streamlit as st
import pandas as pd
import requests
import feedparser
from datetime import datetime

st.set_page_config(layout="wide", page_title="GeoQuant News")

st.title("📰 News Sentiment Radar")

# 1. Sidebar : Choix de la source
source_type = st.sidebar.radio("Source de données", ["Tech (Hacker News)", "Monde (Google News)"])

# 2. Fonction pour Hacker News (API JSON)
# Hacker News a une API gratuite et rapide. On récupère les IDs des top stories, puis les détails.
@st.cache_data(ttl=300) # Cache de 5 minutes pour ne pas spammer
def get_hackernews_stories(limit=15):
    stories = []
    try:
        # Étape 1 : Récupérer les IDs des 500 top stories
        response = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json")
        top_ids = response.json()[:limit] # On prend juste les 'limit' premiers
        
        # Étape 2 : Récupérer les détails pour chaque ID
        for item_id in top_ids:
            item_r = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json")
            item_data = item_r.json()
            if item_data:
                stories.append({
                    "Titre": item_data.get("title"),
                    "Lien": item_data.get("url", "#"),
                    "Score": item_data.get("score", 0),
                    "Date": datetime.fromtimestamp(item_data.get("time")).strftime('%Y-%m-%d %H:%M')
                })
    except Exception as e:
        st.error(f"Erreur API Hacker News : {e}")
    return pd.DataFrame(stories)

# 3. Fonction pour Google News (Flux RSS)
# Google News génère des RSS par langue/sujet. C'est très puissant.
@st.cache_data(ttl=600)
def get_google_news(query="Geopolitics"):
    # On encode la requête pour l'URL (ex: espace devient %20)
    encoded_query = requests.utils.quote(query)
    # URL magique de Google News RSS
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    feed = feedparser.parse(rss_url)
    stories = []
    
    for entry in feed.entries[:20]:
        stories.append({
            "Titre": entry.title,
            "Lien": entry.link,
            "Source": entry.source.title if 'source' in entry else "Inconnu",
            "Date": entry.published
        })
    return pd.DataFrame(stories)

# 4. Logique d'affichage conditionnelle
if source_type == "Tech (Hacker News)":
    st.subheader("🔥 Tendances Tech (Hacker News)")
    df_tech = get_hackernews_stories(limit=20)
    
    # Un petit filtre interactif
    keyword = st.text_input("Filtrer par mot clé (ex: AI, Python)", "")
    if keyword:
        # Filtre insensible à la casse
        df_tech = df_tech[df_tech['Titre'].str.contains(keyword, case=False, na=False)]
    
    # Affichage propre avec des liens cliquables
    # Streamlit dataframe permet des interactions basiques
    st.dataframe(
        df_tech, 
        column_config={"Lien": st.column_config.LinkColumn("Article")},
        use_container_width=True,
        hide_index=True
    )

else:
    st.subheader("🌍 Tendances Géopolitiques (Google News)")
    
    # Input pour changer le sujet de géopolitique
    topic = st.text_input("Sujet de veille", "Ukraine Crisis")
    
    df_geo = get_google_news(topic)
    
    if not df_geo.empty:
        for index, row in df_geo.iterrows():
            # Affichage style "Feed"
            with st.container():
                st.markdown(f"**[{row['Titre']}]({row['Lien']})**")
                st.caption(f"{row['Source']} - {row['Date']}")
                st.divider()
    else:
        st.info("Aucune news trouvée.")