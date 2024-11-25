from flask import Flask, redirect, request
import webbrowser
import requests
import csv
from fuzzSearch import search_genius_lyrics, get_lyrics_from_genius, detect_lyrics_language

app = Flask(__name__)

CLIENT_ID = "afb4cadea90546dfac352aa53ea53256"
CLIENT_SECRET = "ae002b361fde40bd8505b15a2b9bc0ce"
REDIRECT_URI = "http://localhost:8888/callback"
SCOPE = "user-top-read"

def process_songs(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me/top/tracks", headers=headers)
    song_data = []

    if response.status_code == 200:
        favorite_tracks = response.json().get("items", [])
        for track in favorite_tracks:
            song_title = track['name']
            artist_name = [artist['name'] for artist in track['artists']]
            language = None
            
            song_url = search_genius_lyrics(song_title, artist_name)
            if song_url:
                lyrics = get_lyrics_from_genius(song_url)
                if lyrics:
                    language = detect_lyrics_language(lyrics)
            
            song_info = {
                "song_name": song_title,
                "singer_name": ", ".join(artist_name),
                "song_language": language if language else 'None'
            }
            song_data.append(song_info)
            
        with open("song_data.csv", mode="w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["song_name", "singer_name", "song_language"])
            writer.writeheader()
            writer.writerows(song_data)
        return True
    return False

@app.route("/")
def home():
    auth_url = (
        "https://accounts.spotify.com/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPE}"
        f"&show_dialog=true"
    )
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "授權失敗：未收到授權碼"

    # 獲取 access token
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    
    try:
        token_response = requests.post(token_url, data=payload)
        if token_response.status_code != 200:
            return f"獲取Token失敗：{token_response.json()}"
        
        access_token = token_response.json()["access_token"]
        if process_songs(access_token):
            return """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>處理完成</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            margin: 40px;
                            background-color: #1DB954;
                            color: white;
                        }
                        .container {
                            background-color: rgba(0,0,0,0.8);
                            padding: 30px;
                            border-radius: 8px;
                            max-width: 600px;
                            margin: 0 auto;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>成功！</h1>
                        <p>您的歌單已保存到 song_data.csv</p>
                    </div>
                </body>
                </html>
            """
    except Exception as e:
        return f"處理過程中發生錯誤：{str(e)}"

    return "處理失敗"

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:8888")
    app.run(port=8888, debug=True)