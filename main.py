import json
from dotenv import load_dotenv
import os
import base64
from requests import post, get

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    LIMIT = 1
    query = f"q={artist_name}&type=artist&limit={LIMIT}"
    
    query_url = f"{url}?{query}"
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    
    if "error" in json_result:
        return None
    else:
        json_result = json.loads(result.content)["artists"]["items"]

    return json_result[0]

def get_songs_by_artist(token, artist_id):
    COUNTRY = "CA"
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market={COUNTRY}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]

    return json_result

def get_albums_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    
    all_items = json_result["items"]
    albums = []
    singles = []
    for x in all_items:
        if x['album_type'] == "album":
            albums.append(x["name"])
        elif x['album_type'] == "single":
            singles.append(x["name"])
    
    return albums, singles



token = get_token()
while True:
    user_input = input("Which artist do you want to see top tracks for?: ").lower()
    artist = search_for_artist(token, user_input)
    if artist is not None:
        print("1 = Top 10 Songs")
        print("2 = Albums")
        user_input_2 = input("What would you like to see?: ")
        while user_input_2 not in ['1', '2']:
            user_input_2 = input("Invalid input. Try again: ")
        artist_id = artist["id"]
        
        if user_input_2 == "1":
            songs = get_songs_by_artist(token, artist_id)
            print(f"Top 10 Tracks for {artist['name']}")
            for song_num, song in enumerate(songs):
                print(f"{song_num + 1:2}. {song['name']}")
        elif user_input_2 == "2":
            artist_albums, artist_singles = get_albums_by_artist(token, artist_id)

            print(f"\n{artist['name']}'s Albums:")
            for album_num, album in enumerate(artist_albums):
                print(f"{album_num + 1:2}. {album}")

            # print(f"\n{artist['name']}'s Singles:")
            # for singles_num, single in enumerate(artist_singles):
            #     print(f"{singles_num + 1:2}. {single}")
    else:
        print(f"'{user_input}' does not exist")
    user_quit = input("Enter 'y' to quit: ").lower()
    if user_quit == 'y':
        break