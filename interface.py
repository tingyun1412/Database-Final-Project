from flask import Flask, render_template, request, jsonify, session, redirect, url_for 
import csv
import mysql.connector
from collections import Counter
import requests #
import urllib.parse #
import subprocess
import os
# Flask App Initialization
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Spotify API Configuration
CLIENT_ID = "01dfa2aba3384ac4ba4b278af29d2f6d"
CLIENT_SECRET = "e672de7d54d34ef4b745be950e084e5b"
REDIRECT_URI = "http://localhost:8888/callback"
SCOPE = "user-top-read"

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '20050616',
    'database': 'final_project'
}

# Database Connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Function to reset the table
def reset_table():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        # Truncate the 'playlist' table to remove all rows and reset auto-increment
        cursor.execute("TRUNCATE TABLE playlist")
        connection.commit()
        print("Table 'playlist' has been reset.")
    except mysql.connector.Error as e:
        print(f"Database Error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

def insert_csv_data_into_playlist(csv_file):
    reset_table()
    try:
        with open(csv_file, mode='r', encoding='utf-8-sig') as file:
            csv_reader = csv.DictReader(file)

            # Print the fieldnames (headers) to ensure they're correct
            print(f"CSV Headers: {csv_reader.fieldnames}")

            connection = get_db_connection()
            cursor = connection.cursor()

            insert_query = "INSERT INTO playlist (song_name, singer_name, song_language, track_id) VALUES (%s, %s, %s,%s)"
            
            for row in csv_reader:
                print(f"Row data: {row}")  # Print the row to check its contents
                cursor.execute(insert_query, (row['song_name'], row['singer_name'], row['song_language'],row['track_id']))
            
            connection.commit()
            print(f"Data from {csv_file} inserted successfully.")
    
    except mysql.connector.Error as e:
        print(f"Database Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

# Call the function to insert data from the CSV
#insert_csv_data_into_playlist('playlist.csv')
@app.route('/generate_playlist', methods=['POST'])
def generate_playlist():
    try:
        subprocess.run(['python', 'favList_into_csv.py'], check=True)
        # 等待 Spotify 授權完成，並檢查 playlist.csv 是否生成
        import time
        timeout = 60
        elapsed_time = 0
        while not os.path.exists('playlist.csv') and elapsed_time < timeout:
            time.sleep(2)
            elapsed_time += 2
        if os.path.exists('playlist.csv'):
            insert_csv_data_into_playlist('playlist.csv')
            requests.post('http://localhost:8890/shutdown')
            return jsonify({"message": "Playlist generated and updated successfully!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error generating playlist: {e}"}), 500
    
 # Fetch data from the 'playlist' table
def fetch_playlist_data():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query='''
            SELECT p.song_name, p.singer_name,
            CASE 
                WHEN p.singer_name IN (SELECT singer_name FROM Singer) THEN 
                    (SELECT singer_gender FROM Singer WHERE Singer.singer_name = p.singer_name LIMIT 1)
                ELSE 
                    'unknown'
            END AS singer_gender,
            p.song_language,
            CASE 
                WHEN p.song_name IN (SELECT song_name FROM Song) THEN 
                    (SELECT song_genre FROM Song WHERE Song.song_name = p.song_name LIMIT 1)
                ELSE 
                    'unknown'
            END AS song_genre,
            CASE 
                WHEN p.song_name IN (SELECT song_name FROM Song) THEN 
                    (SELECT song_timing FROM Song WHERE Song.song_name = p.song_name LIMIT 1)
                ELSE 
                    'unknown'
            END AS song_timing,
            CASE 
                WHEN p.song_name IN (SELECT song_name FROM Album) THEN 
                    (SELECT album_name FROM Album WHERE Album.song_name = p.song_name LIMIT 1)
                ELSE 
                    'unknown'
            END AS album_name
            FROM playlist p
        '''
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Database Error: {e}")
        return []
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
##
def create_spotify_playlist(access_token, playlist_name, track_ids):
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    create_playlist_url = "https://api.spotify.com/v1/me/playlists"
    playlist_data = {
        "name": playlist_name,
        "description": "Playlist created from filtered songs",
        "public": False
    }
    response = requests.post(create_playlist_url, headers=headers, json=playlist_data)
    if response.status_code == 201:
        playlist_id = response.json().get("id")
        add_tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        track_uris = [f"spotify:track:{track_id}" for track_id in track_ids]
        requests.post(add_tracks_url, headers=headers, json={"uris": track_uris})
        return True
    return False

# Flask Routes
@app.route('/')
def index():
    #
    '''
    playlist_data = fetch_playlist_data()
    return render_template('interface.html', playlist=playlist_data)
    '''
    # Fetch playlist data
    playlist_data = fetch_playlist_data()# Prepare data for the pie charts
    genres = [row['song_genre'] for row in playlist_data]
    languages = [row['song_language'] for row in playlist_data]
    singers = [row['singer_name'] for row in playlist_data]
    timings = [row['song_timing'] for row in playlist_data]
    
    # Count occurrences for each category
    genre_count = Counter(genres)
    language_count = Counter(languages)
    singer_count = Counter(singers)
    timing_count = Counter(timings)
    
    # Pass the data to the template
    return render_template('interface.html', 
                           playlist=playlist_data,
                           genre_count=genre_count,
                           language_count=language_count,
                           singer_count=singer_count,
                           timing_count=timing_count)
    

##
@app.route('/spotify_auth')
def spotify_auth():
    auth_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "show_dialog": "true"
    }
    url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    return redirect(url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "授權失敗，請重新嘗試。"

    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(token_url, data=payload)
    if response.status_code == 200:
        token_data = response.json()
        session['access_token'] = token_data['access_token']
        return redirect('/')
    else:
        return "授權失敗：無法取得 Access Token。"

@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"message": "未授權 Spotify，請先授權！"}), 403

    selected_songs = request.json.get('selected_songs', [])
    playlist_name = "Filtered Playlist"

    track_ids = []
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT track_id FROM playlist WHERE song_name IN (%s)"
        format_strings = ','.join(['%s'] * len(selected_songs))
        cursor.execute(query % format_strings, tuple(selected_songs))
        track_ids = [row['track_id'] for row in cursor.fetchall()]
        #
        print(track_ids)
    finally:
        if connection.is_connected():
            connection.close()

    if create_spotify_playlist(access_token, playlist_name, track_ids):
        return jsonify({"message": "Playlist created successfully!"}), 200
    return jsonify({"message": "Failed to create playlist."}), 500


if __name__ == '__main__':
    app.run(port=8888,debug=True)