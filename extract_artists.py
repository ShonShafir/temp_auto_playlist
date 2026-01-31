import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import config
import warnings
warnings.filterwarnings('ignore')
import os

def extract_playlist_id(url):
    """Extract playlist ID from Spotify URL"""
    if 'playlist/' in url:
        playlist_id = url.split('playlist/')[1].split('?')[0]
        return playlist_id
    return url

def get_all_tracks_from_playlist(sp, playlist_id):
    """Get all tracks from a playlist with pagination"""
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    tracks.extend(results['items'])
    
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    
    return tracks

def extract_artist_ids():
    """Extract all unique artist IDs from configured playlists"""
    client_credentials_manager = SpotifyClientCredentials(
        client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
        client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET")
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    artist_ids = set()
    
    print(f"Processing {len(config.PLAYLIST_URLS)} playlist(s)...")
    
    for playlist_url in config.PLAYLIST_URLS:
        playlist_id = extract_playlist_id(playlist_url)
        print(f"Fetching tracks from playlist: {playlist_id}")
        
        try:
            tracks = get_all_tracks_from_playlist(sp, playlist_id)
            print(f"Found {len(tracks)} tracks in playlist")
            
            for item in tracks:
                if item['track'] and item['track']['artists']:
                    for artist in item['track']['artists']:
                        artist_ids.add(artist['id'])
            
        except Exception as e:
            print(f"Error processing playlist {playlist_id}: {e}")
            continue
    
    print(f"Total unique artists found: {len(artist_ids)}")
    
    artist_ids = [aid for aid in artist_ids if aid]
    
    # === LOAD existing artists (if file exists) ===
    existing_artist_ids = set()
    if os.path.exists(config.ARTISTS_FILE):
        with open(config.ARTISTS_FILE, 'r') as f:
            existing_artist_ids = {x.strip() for x in f.read().split(',') if x.strip()}
    
    print(f"Existing artists in file: {len(existing_artist_ids)}")
    
    # === MERGE ===
    all_artist_ids = existing_artist_ids.union(artist_ids)
    
    print(f"Total unique artists after merge: {len(all_artist_ids)}")
    
    # === SAVE BACK (overwrite with merged list) ===
    with open(config.ARTISTS_FILE, 'w') as f:
        f.write(', '.join(sorted(all_artist_ids)))
    
    print(f"Updated artist IDs saved to {config.ARTISTS_FILE}")
    return len(all_artist_ids)
