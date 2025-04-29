import spotipy
from django.templatetags.static import static
from spotipy.oauth2 import SpotifyClientCredentials
from decouple import config
from pprint import pprint

client_id = config("SPOTIPY_CLIENT_ID")
client_secret = config("SPOTIPY_CLIENT_SECRET")

client_credentials_manager = SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
)

spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

default_image = static("default/default.jpg")

# Get all of the results based off the user input
def get_results(input):
    top_result = {}
    album_results = {}
    artist_results = {}
    
    top_result = get_top_result(input)
    artist_results = get_artists(input)
        
    if top_result is not None and top_result["type"] is not None:

        if top_result["type"] == "artist":
            uri = top_result["uri"]
            albums = get_artist_albums(uri, limit=7)
            album_results.update(albums)
            additional_albums = get_albums(input)
            album_results = append_dicts(album_results, additional_albums)
            
            # Remove duplicate artists
            artist_results = {
                key: artist
                for key, artist in artist_results.items()
                if artist.get("name") != top_result["name"]
            }
            
        elif top_result["type"] == "album":
            uri = top_result["artist_uri"]
            albums = get_artist_albums(uri, limit=4)
            album_results.update(albums)
            additional_albums = get_albums(input)
            album_results = append_dicts(album_results, additional_albums)
                    
            
            # Remove duplicate albums
            album_results = {
                key: album
                for key, album in album_results.items()
                if album.get("title") != top_result["title"]
            }
            
            album_artist = get_artist_by_uri(uri)
            
            artist_results = append_dicts(album_artist, artist_results)
            
            
 

    return top_result, album_results, artist_results


def append_dicts(org_dict, new_dict): 
    new_key_offset = len(org_dict) + 1  
    for i, (key, value) in enumerate(new_dict.items()):
        org_dict[str(new_key_offset + i)] = value  
    
    return org_dict

# Get the top result based off the user input
def get_top_result(input):
    
    album_lookup = {}
    artist_lookup = {}

    album_results = spotify.search(q=f'album:{input}',type="album", limit=5)    
    artist_results = spotify.search(q=f'artist:{input}', type="artist", limit=5)

    
    album_items = album_results.get('albums', {}).get('items', [])
    artist_items = artist_results.get('artists', {}).get('items', [])
    
    
    popularity_check = True
    album_items = create_album_dict(album_lookup, album_items, popularity_check)
    artist_items = create_artist_dict(artist_lookup, artist_items)
    
    # Sort both dictionaries by the 'popularity' key in descending order (highest popularity first)
    sorted_album_items = dict(sorted(album_items.items(), key=lambda item: item[1]['popularity'], reverse=True))
    sorted_artist_items = dict(sorted(artist_items.items(), key=lambda item: item[1]['popularity'], reverse=True))
    
    highest_popularity_album = None
    highest_popularity_artist = None

    # Get the item with the highest popularity (the first item after sorting)
    if sorted_album_items:
        highest_popularity_album = list(sorted_album_items.values())[0] 

    if sorted_artist_items:
        highest_popularity_artist = list(sorted_artist_items.values())[0]
    
    # Compare the popularity of the highest album and artist and pick the highest    
    top_result = max(
        filter(None, [highest_popularity_album, highest_popularity_artist]),
        key=lambda x: x['popularity']
    )

        

    return top_result

# Get an artist albums from their uri
def get_artist_albums(uri,limit=20):
    album_lookup = {}
        
    results = spotify.artist_albums(uri, album_type='album,single', limit=limit)
    albums = results['items']
    
    album_lookup = create_album_dict(album_lookup, albums)        

    return album_lookup

def get_albums(input):
    album_lookup = {}

    album_results = spotify.search(q=f'album:{input}',type="album", limit=10)
    
    album_items = album_results.get('albums', {}).get('items', [])
    
    album_items = create_album_dict(album_lookup, album_items, popularity_check = False)

    return album_items

def get_artists(input):
    artist_lookup = {}
    
    artist_results = spotify.search(q=f'artist:{input}', type="artist", limit=10)
    
    artist_items = artist_results.get('artists', {}).get('items', [])
    
    artist_items = create_artist_dict(artist_lookup, artist_items)
    
    return artist_items

# Get an album's popularity
def get_album_popularity(id):
    results = spotify.album(id)
    return results["popularity"]


def get_artist_by_uri(uri):
    artist_lookup = {}
    
    results = spotify.artist(uri)
    
    id = results['id']
    name = results['name']
    uri = results['uri']
    image = results['images'][1]['url'] if results['images'] else default_image
        
    artist_lookup[1] = {
        'type': 'artist',
        'id': id,
        'name': name,
        'uri': uri,
        'image_url':image
    }
    
    
    return artist_lookup
    


# Create a dictionary of albums
def create_album_dict(album_lookup, album_items, popularity_check = False):
    for i, album_item in enumerate(album_items):
        id = album_item['id']
        uri = album_item['uri']
        title = album_item['name']
        popularity = get_album_popularity(album_item['id']) if popularity_check == True else None
        artist = album_item['artists'][0]['name']
        artist_uri = album_item['artists'][0]['uri']
        cover = album_item['images'][1]['url'] if album_item['images'] else default_image
        release_year = album_item['release_date'][:4]
        
        album_lookup[str(i + 1)] = {
            "type": "album",
            "id": id,
            "uri": uri,
            "popularity": popularity,
            "title": title,
            "artist": artist,
            "artist_uri": artist_uri,
            "release_year": release_year,
            "cover_url": cover
        }
        
    
        
    return album_lookup

# Create a dictionary of artists
def create_artist_dict(artist_lookup,artist_items):
    for i, artist_items in enumerate(artist_items):
            id = artist_items['id']
            name = artist_items['name']
            popularity = artist_items['popularity']
            uri = artist_items['uri']
            image = artist_items['images'][1]['url'] if artist_items['images'] else default_image
            
            artist_lookup[str(i + 1)] = {
                "type": "artist",
                "id": id,
                "popularity": popularity,
                "name": name,
                "uri": uri,
                "image_url": image
            }
    return artist_lookup

