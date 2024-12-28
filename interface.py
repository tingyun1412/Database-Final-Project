from flask import Flask, render_template, request, jsonify, redirect, session, url_for, flash
import requests
import csv
import mysql.connector
from collections import Counter

CLIENT_ID = "01dfa2aba3384ac4ba4b278af29d2f6d"
CLIENT_SECRET = "e672de7d54d34ef4b745be950e084e5b"
REDIRECT_URI = "http://localhost:8888/spotify_callback"
SCOPE = "user-top-read playlist-modify-public playlist-modify-private"

# Flask App Initialization
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Ann940716',
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

            insert_query = "INSERT INTO playlist (song_name, singer_name, song_language) VALUES (%s, %s, %s)"
            
            for row in csv_reader:
                print(f"Row data: {row}")  # Print the row to check its contents
                cursor.execute(insert_query, (row['song_name'], row['singer_name'], row['song_language']))
            
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
insert_csv_data_into_playlist('playlist.csv')

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


# Flask Routes
@app.route('/')
def index():
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

@app.route('/create_spotify_playlist', methods=['POST'])
def create_spotify_playlist():
    try:
        filtered_songs = request.json.get('filtered_songs', [])
        if not filtered_songs:
            return jsonify({'error': '沒有選擇任何歌曲'}), 400
        
        if 'spotify_token' not in session:
            # 保存篩選後的歌曲到 session
            session['filtered_songs'] = filtered_songs
            auth_url = (
                "https://accounts.spotify.com/authorize"
                f"?client_id={CLIENT_ID}"
                "&response_type=code" 
                f"&redirect_uri={REDIRECT_URI}"
                f"&scope={SCOPE}"
                "&show_dialog=true"
            )
            return jsonify({'redirect': auth_url})
        
        # 直接使用 create_spotify_playlist_with_songs
        playlist_link = create_spotify_playlist_with_songs(session['spotify_token'], filtered_songs)
        return jsonify({'playlist_link': playlist_link})
        print("playlist link",playlist_link)
        
    except Exception as e:
        print(f"Error creating playlist: {str(e)}")
        return redirect(url_for('index'))


@app.route('/spotify_callback')
def spotify_callback():
    try:
        print("Received Spotify callback")  # Debug log
        # Get authorization code
        code = request.args.get("code")
        print(f"Received auth code: {code[:10]}...")  # 新增日誌
        
        if not code:
            print("No authorization code received")  # Debug log
            return redirect(url_for('index'))
            
        # Get access token
        print(f"Got authorization code: {code[:10]}...") 
        access_token = get_spotify_token(code)
        print("Successfully got access token")  # Debug log
        
        session['spotify_token'] = access_token
        # Create playlist and add songs
        filtered_songs = session.get('filtered_songs', [])
        playlist_link = create_spotify_playlist_with_songs(access_token,filtered_songs)
        
        # Render template with playlist
        return display_playlist_page(playlist_link)
        
    except Exception as e:
        print(f"Error in Spotify callback: {str(e)}")
        return redirect(url_for('index'))

def get_spotify_token(code):
    print("Requesting access token")  # Debug log
    try:
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI, 
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET
            }
        )
        response_data = response.json()
        
        if 'error' in response_data:
            raise Exception(f"Spotify API Error: {response_data['error']}")
            
        if 'access_token' not in response_data:
            raise Exception("No access token in response")
            
        return response_data["access_token"]
    except Exception as e:
        print(f"Error in get_spotify_token: {str(e)}")
        raise

def create_spotify_playlist_with_songs(access_token,filtered_songs):
    PLAYLIST_NAME = "My Filtered Playlist"
    PLAYLIST_DESC = "Filtered playlist"
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Get user ID
    user_response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    user_id = user_response.json()["id"]
    
    # Create playlist
    playlist = requests.post(
        f"https://api.spotify.com/v1/users/{user_id}/playlists",
        headers=headers,
        json={
            "name": PLAYLIST_NAME,
            "description": PLAYLIST_DESC,
            "public": True
        }
    ).json()
    
    
    # Add songs
    playlist_id = playlist["id"]
    playlist_data = fetch_playlist_data()
    
    
    filtered_playlist_data = [song for song in playlist_data if song['song_name'] in filtered_songs]
    for song in filtered_playlist_data:
        search_query = f"track:{song['song_name']} artist:{song['singer_name']}"
        search_response = requests.get(
            "https://api.spotify.com/v1/search",
            headers=headers,
            params={
                "q": search_query,
                "type": "track",
                "limit": 1
            }
        )
        print(search_response)
        
        if search_response.json()["tracks"]["items"]:
            track_uri = search_response.json()["tracks"]["items"][0]["uri"]
            requests.post(
                f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
                headers=headers,
                json={"uris": [track_uri]}
            )
            
    return playlist["external_urls"]["spotify"]

def display_playlist_page(playlist_link):
    playlist_data = fetch_playlist_data()
    return render_template('interface.html',
        playlist=playlist_data,
        genre_count=Counter(row['song_genre'] for row in playlist_data),
        language_count=Counter(row['song_language'] for row in playlist_data),
        singer_count=Counter(row['singer_name'] for row in playlist_data), 
        timing_count=Counter(row['song_timing'] for row in playlist_data),
        playlist_link=playlist_link
    )
    
@app.route('/show_playlist')
def show_playlist():
    playlist_data = fetch_playlist_data()
    return render_template('interface.html',
        playlist=playlist_data,
        genre_count=Counter(row['song_genre'] for row in playlist_data),
        language_count=Counter(row['song_language'] for row in playlist_data),
        singer_count=Counter(row['singer_name'] for row in playlist_data),
        timing_count=Counter(row['song_timing'] for row in playlist_data)
    )

if __name__ == '__main__':
    app.run(debug=True, port=8888)
