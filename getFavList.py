import requests
import csv
from fuzzSearch import search_genius_lyrics,get_lyrics_from_genius,detect_lyrics_language
from getAuth import login,callback
import subprocess
import time
import webbrowser

client_id = "afb4cadea90546dfac352aa53ea53256"
client_secret = "ae002b361fde40bd8505b15a2b9bc0ce"
redirect_uri = "http://localhost:8888/callback"  # 與之前設定的 URI 保持一致

# 啟動 Flask 伺服器（getAuth.py）
flask_process = subprocess.Popen(["python", "C:\\Users\\User\\Desktop\\DBMS\\final)project\\src\\getAuth.py"])

# 等待伺服器啟動
time.sleep(2)  # 可以調整等待時間以確保伺服器啟動完成

# 自動打開瀏覽器並訪問授權頁面
webbrowser.open("http://localhost:8888/")

# 等待使用者完成授權並取得授權碼
print("等待授權完成...")

# 檢查是否已取得授權碼，最多等待 60 秒
code = None
for _ in range(60):
    try:
        with open("auth_code.txt", "r") as file:
            code = file.read().strip()
            break  # 若取得 code 則跳出等待
    except FileNotFoundError:
        time.sleep(1)  # 每秒檢查一次

# 確認是否成功取得授權碼
if code:
    print("取得的授權碼:", code)
    # 在這裡進行後續操作，例如交換 access token
    # 可以使用 requests 庫向 Spotify 發送請求
else:
    print("未能取得授權碼，請檢查授權流程。")

# 關閉 Flask 伺服器
flask_process.terminate()

##
# 請求 token 的 URL 和參數
token_url = "https://accounts.spotify.com/api/token"
payload = {
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": redirect_uri,
    "client_id": client_id,
    "client_secret": client_secret,
}

# 發送 POST 請求取得 access token
response = requests.post(token_url, data=payload)
token_data = response.json()

if response.status_code == 200:
    access_token = token_data["access_token"]
    print("Access Token:", access_token)
else:
    print("無法獲取 Access Token:", token_data)
    
headers = {"Authorization": f"Bearer {access_token}"}

# 使用者最喜歡的歌曲
response = requests.get("https://api.spotify.com/v1/me/top/tracks", headers=headers)

song_data=[]


if response.status_code == 200:
    favorite_tracks = response.json().get("items", [])
    for track in favorite_tracks:
        language=None
        song_title=track['name']
        artist_name=[artist['name'] for artist in track['artists']]
        
        song_url = search_genius_lyrics(song_title, artist_name)
        if song_url:
            lyrics = get_lyrics_from_genius(song_url)
            if lyrics:
                language = detect_lyrics_language(lyrics)

                print(f"歌曲名稱: {track['name']}，歌手: {', '.join([artist['name'] for artist in track['artists']])}，語言：{language}")
            else:
                print(f"歌曲名稱: {track['name']}，歌手: {', '.join([artist['name'] for artist in track['artists']])}，語言：無法取得歌詞")
        else:
            print(f"歌曲名稱: {track['name']}，歌手: {', '.join([artist['name'] for artist in track['artists']])}，語言：無法找到歌曲")
        #寫入dictionary  
        artist_name=", ".join(artist_name)
        if language:
            song_info={
                "song_name":track['name'],
                "singer_name":artist_name,
                "song_language":language
            }
            song_data.append(song_info)
        else:
            song_info={
                "song_name":track['name'],
                "singer_name":artist_name,
                "song_language":'None'
            }
            song_data.append(song_info)
        #寫入csv
        # 定義要寫入的 CSV 檔案名稱
        csv_file_path = "song_data.csv"

        # 將資料寫入 CSV 檔案
        with open(csv_file_path, mode="w", newline="", encoding="utf-8-sig") as csv_file:
            fieldnames = ["song_name", "singer_name", "song_language"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            
            # 寫入表頭
            writer.writeheader()
            
            # 寫入歌曲資訊
            for song in song_data:
                writer.writerow(song)

       # print(f"已成功將歌曲資訊寫入 {csv_file_path}")    
        
    
else:
    print("無法獲取喜好歌曲:", response.json())
    
