import streamlit as st
import pandas as pd
import time
import os
from utils.database import (
    get_spotify_data, 
    get_top_artists, 
    get_top_playlists, 
    get_user_stats,
    get_dataset_stats
)
from utils.visualizations import (
    create_artist_bar_chart,
    create_playlist_bar_chart,
    create_users_pie_chart,
    create_stats_cards,
    create_artist_network
)

# Configuración de la página
st.set_page_config(
    page_title="Spotify Analytics Dashboard",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
<style>
    .main {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    .stApp {
        background-color: #1a1a1a;
    }
    h1, h2, h3 {
        color: #1db954; /* Verde de Spotify */
    }
    .st-emotion-cache-1kyxreq {
        color: #ffffff;
    }
    .stMetric {
        background-color: #282828;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stMetric label {
        color: #1db954 !important;
    }
    .stMetric value {
        color: #ffffff !important;
    }
    .sidebar .sidebar-content {
        background-color: #121212;
    }
</style>
""", unsafe_allow_html=True)

# Título y descripción
st.title("🎵 Spotify Analytics Dashboard")
st.markdown("""
Este dashboard analiza y visualiza datos de Spotify extraídos mediante un proceso ETL desde Kaggle y almacenados en MongoDB Atlas.
Explora las tendencias, artistas populares y estadísticas de playlists.
""")

# Sidebar para filtros y controles
with st.sidebar:
    st.header("⚙️ Controles")
    
    # Datos de muestra vs. completos
    sample_data = st.checkbox("Usar muestra de datos", value=True, 
                            help="Activar para usar una muestra aleatoria. Desactivar para usar todos los datos disponibles.")
    
    # Tamaño de la muestra
    if sample_data:
        sample_size = st.slider("Tamaño de la muestra", 
                               min_value=1000, 
                               max_value=50000, 
                               value=10000, 
                               step=1000)
    else:
        sample_size = 100000  # Limitar a 100,000 registros para rendimiento
    
    # Número de elementos a mostrar en los gráficos
    top_n = st.slider("Elementos a mostrar", 
                     min_value=5, 
                     max_value=30, 
                     value=15)
    
    # Botón para actualizar los datos
    if st.button("🔄 Actualizar Datos"):
        st.cache_data.clear()

# Función para cargar datos con caché
@st.cache_data(ttl=3600)  # Caché por 1 hora
def load_data(sample=True, limit=10000):
    # Mostrar spinner mientras se cargan los datos
    with st.spinner("Cargando datos de MongoDB Atlas..."):
        return get_spotify_data(limit=limit, sample=sample)

@st.cache_data(ttl=3600)
def load_top_artists(limit=20):
    with st.spinner("Analizando artistas..."):
        return get_top_artists(limit=limit)

@st.cache_data(ttl=3600)
def load_top_playlists(limit=20):
    with st.spinner("Analizando playlists..."):
        return get_top_playlists(limit=limit)

@st.cache_data(ttl=3600)
def load_user_stats():
    with st.spinner("Analizando usuarios..."):
        return get_user_stats()

@st.cache_data(ttl=3600)
def load_dataset_stats():
    with st.spinner("Calculando estadísticas..."):
        return get_dataset_stats()

# Cargar estadísticas generales
stats = load_dataset_stats()

# Mostrar tarjetas con estadísticas generales
st.header("📊 Estadísticas Generales")
create_stats_cards(stats)

# Mostrar gráficos
st.header("🎨 Visualizaciones")

# Definir pestañas para las visualizaciones
tab1, tab2, tab3, tab4 = st.tabs(["👨‍🎤 Artistas", "📝 Playlists", "👥 Usuarios", "🔄 Red de Artistas"])

with tab1:
    # Cargar y mostrar los artistas más populares
    top_artists_df = load_top_artists(limit=top_n)
    
    if not top_artists_df.empty:
        st.subheader("Artistas más populares")
        artist_chart = create_artist_bar_chart(top_artists_df)
        if artist_chart:
            st.plotly_chart(artist_chart, use_container_width=True)
        
        # Mostrar datos en tabla
        st.subheader("Datos de artistas")
        st.dataframe(top_artists_df.style.set_properties(**{'background-color': '#282828', 'color': '#ffffff'}))
    else:
        st.error("No se pudieron cargar los datos de artistas. Verifica la conexión a MongoDB.")

with tab2:
    # Cargar y mostrar las playlists más populares
    top_playlists_df = load_top_playlists(limit=top_n)
    
    if not top_playlists_df.empty:
        st.subheader("Playlists más populares")
        playlist_chart = create_playlist_bar_chart(top_playlists_df)
        if playlist_chart:
            st.plotly_chart(playlist_chart, use_container_width=True)
        
        # Mostrar datos en tabla
        st.subheader("Datos de playlists")
        st.dataframe(top_playlists_df.style.set_properties(**{'background-color': '#282828', 'color': '#ffffff'}))
    else:
        st.error("No se pudieron cargar los datos de playlists. Verifica la conexión a MongoDB.")

with tab3:
    # Cargar y mostrar estadísticas de usuarios
    total_users, top_users_df = load_user_stats()
    
    if total_users > 0 and not top_users_df.empty:
        st.subheader(f"Total de usuarios únicos: {total_users:,}")
        
        # Gráfico de pastel de usuarios
        users_chart = create_users_pie_chart(top_users_df)
        if users_chart:
            st.plotly_chart(users_chart, use_container_width=True)
        
        # Mostrar datos en tabla
        st.subheader("Usuarios más activos")
        st.dataframe(top_users_df.head(top_n).style.set_properties(**{'background-color': '#282828', 'color': '#ffffff'}))
    else:
        st.error("No se pudieron cargar los datos de usuarios. Verifica la conexión a MongoDB.")

with tab4:
    # Cargar datos para el gráfico de red
    with st.spinner("Generando gráfico de red de artistas..."):
        data_sample = load_data(sample=True, limit=5000)
        
        if not data_sample.empty:
            st.subheader("Red de colaboraciones entre artistas")
            st.write("Este gráfico muestra cómo los artistas están relacionados a través de las playlists compartidas.")
            
            network_chart = create_artist_network(data_sample, limit=30)
            if network_chart:
                st.plotly_chart(network_chart, use_container_width=True)
            else:
                st.info("No hay suficientes datos para generar el gráfico de red.")
        else:
            st.error("No se pudieron cargar los datos para la red. Verifica la conexión a MongoDB.")

# Footer
st.markdown("""
---
### 📝 Información del proyecto
- Datos extraídos del dataset de Spotify Playlists de Kaggle mediante proceso ETL
- Almacenados en MongoDB Atlas
- Dashboard construido con Streamlit y desplegado en Railway
""")

# Mostrar fecha y hora de actualización
st.sidebar.markdown(f"Última actualización: {time.strftime('%d/%m/%Y %H:%M:%S')}")