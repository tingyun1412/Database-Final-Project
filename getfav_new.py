import requests

client_id = "01dfa2aba3384ac4ba4b278af29d2f6d"
client_secret = "e672de7d54d34ef4b745be950e084e5b"
redirect_uri = "http://localhost:8888/callback"  # 與之前設定的 URI 保持一致
code = "AQByu_XePqsXe2n9ebhuTOv5C0JYTV1jy3nH8r6pgvQ8s40V9FEwfqr2BaDrv9Ib1_6VZxo_ctPzoxa2itdkdd7IVI8wxSlFmA7AmxlZeEUqw9HgcuLZJO10E0y9PU4g3EykE1tFJdD0ztlnUvH158bG3s1xcydxGEj1qmCmRVOgcqrPntzjzDEWmAlyp_31GA"  # 用剛才取得的授權碼替換這裡

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
    url = 'https://api.spotify.com/v1/me/tracks?limit=50&time_range=long_term'
    headers = {"Authorization": f"Bearer {access_token}"}

    # 使用者最喜歡的歌曲
    favorite_tracks = []  # 用來儲存所有最愛歌曲

    # 需要進行分頁請求
    while url:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            # 將返回的歌曲加入到列表
            favorite_tracks.extend(data['items'])
            # 檢查是否有下一頁
            url = data.get('next')
        else:
            print("無法獲取喜好歌曲:", response.json())
            break

    if favorite_tracks:
        print("最愛歌曲：")
        for track in favorite_tracks:
            print(f"歌曲名稱: {track['name']}，歌手: {', '.join([artist['name'] for artist in track['artists']])}")
    else:
        print("沒有返回最愛歌曲")
else:
    print("無法獲取 Access Token:", token_data)
