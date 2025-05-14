import os
from pymongo import MongoClient
import pandas as pd
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_mongodb_connection():
    """Establece la conexión con MongoDB Atlas"""
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb+srv://jajserman3521:MJsXfxlt5TiboXIE@cluster0.5pckf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    
    try:
        client = MongoClient(mongodb_uri)
        # Verificar la conexión
        client.admin.command('ping')
        print("Conexión a MongoDB establecida correctamente")
        return client
    except Exception as e:
        print(f"Error al conectar a MongoDB: {str(e)}")
        raise

def get_spotify_data(limit=10000, sample=True):
    """Obtiene los datos de la colección spotify_dataset de MongoDB Atlas"""
    client = get_mongodb_connection()
    db = client["spotify_music_db"]
    collection = db["spotify_dataset"]
    
    try:
        if sample:
            # Usar aggregation para obtener una muestra aleatoria
            data = list(collection.aggregate([
                {"$sample": {"size": limit}}
            ]))
        else:
            # Limitar la cantidad de documentos si no es una muestra
            data = list(collection.find().limit(limit))
            
        # Convertir a DataFrame y manejar las claves
        df = pd.DataFrame(data)
        
        # Imprimir las columnas para depuración
        print("Columnas encontradas en el DataFrame:", df.columns.tolist())
        
        return df
    except Exception as e:
        print(f"Error al obtener datos de Spotify: {str(e)}")
        return pd.DataFrame()

def get_top_artists(limit=20):
    """Obtiene los artistas con más canciones en la base de datos"""
    client = get_mongodb_connection()
    db = client["spotify_music_db"]
    collection = db["spotify_dataset"]
    
    try:
        # Primero, identificar el nombre correcto de la columna del artista
        sample_doc = collection.find_one()
        artist_field = None
        
        if sample_doc:
            for field in sample_doc:
                if 'artist' in field.lower():
                    artist_field = field
                    break
        
        if not artist_field:
            artist_field = "_artistname"  # Nombre predeterminado
        
        pipeline = [
            {"$group": {"_id": f"${artist_field}", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        
        results = list(collection.aggregate(pipeline))
        return pd.DataFrame(results).rename(columns={"_id": "artist"})
    except Exception as e:
        print(f"Error al obtener los artistas más populares: {str(e)}")
        return pd.DataFrame()

def get_top_playlists(limit=20):
    """Obtiene las playlists con más canciones en la base de datos"""
    client = get_mongodb_connection()
    db = client["spotify_music_db"]
    collection = db["spotify_dataset"]
    
    try:
        # Primero, identificar el nombre correcto de la columna de la playlist
        sample_doc = collection.find_one()
        playlist_field = None
        
        if sample_doc:
            for field in sample_doc:
                if 'playlist' in field.lower():
                    playlist_field = field
                    break
        
        if not playlist_field:
            playlist_field = "_playlistname"  # Nombre predeterminado
        
        pipeline = [
            {"$group": {"_id": f"${playlist_field}", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        
        results = list(collection.aggregate(pipeline))
        return pd.DataFrame(results).rename(columns={"_id": "playlist"})
    except Exception as e:
        print(f"Error al obtener las playlists más populares: {str(e)}")
        return pd.DataFrame()

def get_user_stats():
    """Obtiene estadísticas de los usuarios"""
    client = get_mongodb_connection()
    db = client["spotify_music_db"]
    collection = db["spotify_dataset"]
    
    try:
        # Identificar la columna de usuario
        sample_doc = collection.find_one()
        user_field = None
        
        if sample_doc:
            for field in sample_doc:
                if 'user' in field.lower():
                    user_field = field
                    break
        
        if not user_field:
            user_field = "user_id"  # Nombre predeterminado
            
        print(f"Campo de usuario identificado: {user_field}")
        
        # Número total de usuarios únicos
        total_users = len(collection.distinct(user_field))
        
        # Usuarios con más canciones
        top_users_pipeline = [
            {"$group": {"_id": f"${user_field}", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 20}
        ]
        
        top_users = list(collection.aggregate(top_users_pipeline))
        top_users_df = pd.DataFrame(top_users).rename(columns={"_id": "user_id"})
        
        return total_users, top_users_df
    except Exception as e:
        print(f"Error al obtener estadísticas de usuarios: {str(e)}")
        return 0, pd.DataFrame()

def get_dataset_stats():
    """Obtiene estadísticas generales del dataset"""
    client = get_mongodb_connection()
    db = client["spotify_music_db"]
    collection = db["spotify_dataset"]
    
    try:
        # Obtener y mostrar un documento de muestra para depuración
        sample_doc = collection.find_one()
        if sample_doc:
            print("Estructura de un documento de muestra:")
            for key in sample_doc:
                print(f"  - {key}: {type(sample_doc[key])}")
        
        # Identificar los campos relevantes
        user_field = artist_field = track_field = playlist_field = None
        
        for field in sample_doc:
            if 'user' in field.lower():
                user_field = field
            elif 'artist' in field.lower():
                artist_field = field
            elif 'track' in field.lower():
                track_field = field
            elif 'playlist' in field.lower():
                playlist_field = field
        
        print(f"Campos identificados: usuario={user_field}, artista={artist_field}, track={track_field}, playlist={playlist_field}")
        
        # Total de registros
        total_records = collection.count_documents({})
        
        # Total de artistas únicos (usar el campo identificado o un valor predeterminado)
        artist_field = artist_field or "_artistname"
        total_artists = len(collection.distinct(artist_field))
        
        # Total de canciones únicas
        track_field = track_field or "_trackname"
        total_tracks = len(collection.distinct(track_field))
        
        # Total de playlists únicas
        playlist_field = playlist_field or "_playlistname"
        total_playlists = len(collection.distinct(playlist_field))
        
        return {
            "total_records": total_records,
            "total_artists": total_artists,
            "total_tracks": total_tracks,
            "total_playlists": total_playlists
        }
    except Exception as e:
        print(f"Error al obtener estadísticas del dataset: {str(e)}")
        return {
            "total_records": 0,
            "total_artists": 0,
            "total_tracks": 0,
            "total_playlists": 0
        }