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
else:
    print("無法獲取 Access Token:", token_data)
