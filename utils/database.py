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
            
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error al obtener datos de Spotify: {str(e)}")
        return pd.DataFrame()

def get_top_artists(limit=20):
    """Obtiene los artistas con más canciones en la base de datos"""
    client = get_mongodb_connection()
    db = client["spotify_music_db"]
    collection = db["spotify_dataset"]
    
    try:
        pipeline = [
            {"$group": {"_id": "$_artistname", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        
        results = list(collection.aggregate(pipeline))
        return pd.DataFrame(results, columns=["artist", "count"]).rename(columns={"_id": "artist"})
    except Exception as e:
        print(f"Error al obtener los artistas más populares: {str(e)}")
        return pd.DataFrame()

def get_top_playlists(limit=20):
    """Obtiene las playlists con más canciones en la base de datos"""
    client = get_mongodb_connection()
    db = client["spotify_music_db"]
    collection = db["spotify_dataset"]
    
    try:
        pipeline = [
            {"$group": {"_id": "$_playlistname", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        
        results = list(collection.aggregate(pipeline))
        return pd.DataFrame(results, columns=["playlist", "count"]).rename(columns={"_id": "playlist"})
    except Exception as e:
        print(f"Error al obtener las playlists más populares: {str(e)}")
        return pd.DataFrame()

def get_user_stats():
    """Obtiene estadísticas de los usuarios"""
    client = get_mongodb_connection()
    db = client["spotify_music_db"]
    collection = db["spotify_dataset"]
    
    try:
        # Número total de usuarios únicos
        total_users = len(collection.distinct("user_id"))
        
        # Usuarios con más canciones
        top_users_pipeline = [
            {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 20}
        ]
        
        top_users = list(collection.aggregate(top_users_pipeline))
        top_users_df = pd.DataFrame(top_users, columns=["user_id", "count"]).rename(columns={"_id": "user_id"})
        
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
        # Total de registros
        total_records = collection.count_documents({})
        
        # Total de artistas únicos
        total_artists = len(collection.distinct("_artistname"))
        
        # Total de canciones únicas
        total_tracks = len(collection.distinct("_trackname"))
        
        # Total de playlists únicas
        total_playlists = len(collection.distinct("_playlistname"))
        
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