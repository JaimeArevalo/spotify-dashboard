import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

def create_artist_bar_chart(df):
    """Crea un gráfico de barras de los artistas más populares"""
    if df.empty:
        return None
    
    # Identificar la columna correcta para el nombre del artista
    artist_column = None
    for col in df.columns:
        if 'artist' in col.lower():
            artist_column = col
            break
    
    if not artist_column:
        # Si no encontramos una columna de artista, usamos la primera columna
        artist_column = df.columns[0]
    
    # Identificar la columna de conteo
    count_column = 'count'
    if count_column not in df.columns:
        for col in df.columns:
            if 'count' in col.lower():
                count_column = col
                break
    
    fig = px.bar(
        df,
        x=count_column, 
        y=artist_column,
        orientation='h',
        color=count_column,
        color_continuous_scale=px.colors.sequential.Viridis,
        title="Artistas más populares en Spotify",
        labels={count_column: "Número de canciones", artist_column: "Artista"}
    )
    
    fig.update_layout(
        height=600,
        xaxis_title="Número de canciones",
        yaxis_title="Artista",
        yaxis={'categoryorder':'total ascending'},
        font=dict(size=12)
    )
    
    return fig

def create_playlist_bar_chart(df):
    """Crea un gráfico de barras de las playlists más populares"""
    if df.empty:
        return None
    
    # Identificar la columna correcta para el nombre de la playlist
    playlist_column = None
    for col in df.columns:
        if 'playlist' in col.lower():
            playlist_column = col
            break
    
    if not playlist_column:
        # Si no encontramos una columna de playlist, usamos la primera columna
        playlist_column = df.columns[0]
    
    # Crear una copia para no modificar el original
    df_copy = df.copy()
    
    # Asegurarse de que la columna es de tipo string
    df_copy[playlist_column] = df_copy[playlist_column].astype(str)
    
    # Limitar el nombre de las playlists para mejor visualización
    df_copy['playlist_display'] = df_copy[playlist_column].str.slice(0, 30) + '...'
    
    # Identificar la columna de conteo
    count_column = 'count'
    if count_column not in df.columns:
        for col in df.columns:
            if 'count' in col.lower():
                count_column = col
                break
    
    fig = px.bar(
        df_copy,
        x=count_column, 
        y="playlist_display",
        orientation='h',
        color=count_column,
        color_continuous_scale=px.colors.sequential.Plasma,
        title="Playlists más populares en Spotify",
        labels={count_column: "Número de canciones", "playlist_display": "Playlist"}
    )
    
    fig.update_layout(
        height=600,
        xaxis_title="Número de canciones",
        yaxis_title="Playlist",
        yaxis={'categoryorder':'total ascending'},
        font=dict(size=12)
    )
    
    return fig

def create_users_pie_chart(df):
    """Crea un gráfico de pastel de los usuarios más activos"""
    if df.empty:
        return None
    
    # Identificar la columna correcta para el ID de usuario
    user_column = None
    for col in df.columns:
        if 'user' in col.lower():
            user_column = col
            break
    
    if not user_column:
        # Si no encontramos una columna de usuario, usamos la primera columna
        user_column = df.columns[0]
    
    # Identificar la columna de conteo
    count_column = 'count'
    if count_column not in df.columns:
        for col in df.columns:
            if 'count' in col.lower():
                count_column = col
                break
    
    # Tomar los 10 principales usuarios
    top_10 = df.head(10).copy()
    # Agregar "Otros" para el resto
    others_count = df[count_column].sum() - top_10[count_column].sum()
    
    if others_count > 0:
        others = pd.DataFrame({user_column: ["Otros"], count_column: [others_count]})
        df_pie = pd.concat([top_10, others], ignore_index=True)
    else:
        df_pie = top_10
    
    fig = px.pie(
        df_pie, 
        values=count_column, 
        names=user_column,
        title='Distribución de usuarios por actividad',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.4
    )
    
    fig.update_layout(
        height=500,
        font=dict(size=12)
    )
    
    return fig

def create_stats_cards(stats):
    """Crea tarjetas con estadísticas generales del dataset"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Total de registros", value=f"{stats['total_records']:,}")
    
    with col2:
        st.metric(label="Artistas únicos", value=f"{stats['total_artists']:,}")
    
    with col3:
        st.metric(label="Canciones únicas", value=f"{stats['total_tracks']:,}")
    
    with col4:
        st.metric(label="Playlists únicas", value=f"{stats['total_playlists']:,}")

def create_artist_network(df, limit=50):
    """Crea un gráfico de red de artistas y playlists"""
    if df.empty or len(df) < 10:
        return None
    
    # Identificar las columnas correctas para artista y playlist
    artist_column = None
    playlist_column = None
    
    for col in df.columns:
        if 'artist' in col.lower():
            artist_column = col
        elif 'playlist' in col.lower():
            playlist_column = col
    
    # Si no encontramos las columnas, no podemos crear el gráfico
    if not artist_column or not playlist_column:
        return None
    
    # Seleccionar los artistas más populares
    top_artists = df.groupby(artist_column).size().sort_values(ascending=False).head(limit).index.tolist()
    
    # Filtrar el dataframe para incluir solo los artistas populares
    filtered_df = df[df[artist_column].isin(top_artists)]
    
    # Crear un diccionario para almacenar las conexiones entre artistas y playlists
    artist_playlist_connections = {}
    
    # Contar co-ocurrencias de artistas en las mismas playlists
    for playlist in filtered_df[playlist_column].unique():
        artists_in_playlist = filtered_df[filtered_df[playlist_column] == playlist][artist_column].unique()
        
        for i, artist1 in enumerate(artists_in_playlist):
            for artist2 in artists_in_playlist[i+1:]:
                pair = tuple(sorted([artist1, artist2]))
                if pair in artist_playlist_connections:
                    artist_playlist_connections[pair] += 1
                else:
                    artist_playlist_connections[pair] = 1
    
    # Crear listas para los nodos y aristas del gráfico
    edge_x = []
    edge_y = []
    
    # Posición de los nodos (en círculo)
    node_positions = {}
    angle_step = 2 * np.pi / len(top_artists)
    radius = 1
    
    for i, artist in enumerate(top_artists):
        angle = i * angle_step
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        node_positions[artist] = (x, y)
    
    # Crear aristas
    for (artist1, artist2), weight in artist_playlist_connections.items():
        if artist1 in node_positions and artist2 in node_positions:
            x0, y0 = node_positions[artist1]
            x1, y1 = node_positions[artist2]
            
            # Añadir la línea
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
    
    # Crear el trazado de aristas
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')
    
    # Crear el trazado de nodos
    node_x = []
    node_y = []
    node_text = []
    
    for artist, (x, y) in node_positions.items():
        node_x.append(x)
        node_y.append(y)
        node_text.append(artist)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=10,
            colorbar=dict(
                thickness=15,
                title='Conexiones',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))
    
    # Contar el número de conexiones para cada nodo
    node_connections = {}
    for artist in top_artists:
        count = 0
        for (artist1, artist2) in artist_playlist_connections.keys():
            if artist == artist1 or artist == artist2:
                count += 1
        node_connections[artist] = count
    
    node_colors = []
    for artist in node_text:
        node_colors.append(node_connections.get(artist, 0))
    
    node_trace.marker.color = node_colors
    
    # Crear la figura
    fig = go.Figure(data=[edge_trace, node_trace],
                  layout=go.Layout(
                      title='Red de conexiones entre artistas en playlists',
                      titlefont_size=16,
                      showlegend=False,
                      hovermode='closest',
                      margin=dict(b=20,l=5,r=5,t=40),
                      xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                      yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                  ))
    
    return fig