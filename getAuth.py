from flask import Flask, redirect, request, url_for
import requests
import urllib.parse

app = Flask(__name__)

# 您的應用程式的 Client ID 與重導向 URI
CLIENT_ID = "afb4cadea90546dfac352aa53ea53256"  # 您可以在這裡直接寫死
CLIENT_SECRET = "ae002b361fde40bd8505b15a2b9bc0ce"  # 在交換 token 時會用到
REDIRECT_URI = "http://localhost:8888/callback"
SCOPE = "user-top-read"  # 權限範圍

@app.route('/')
def login():
    # Spotify 授權頁面 URL
    auth_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "state": "random_state_string",  # 可用來防範 CSRF 攻擊
        "show_dialog": "true"  # 強制顯示授權對話框
    }
    # 將使用者導向 Spotify 授權頁面
    url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    print(url)
    return redirect(url)

@app.route('/callback')
def callback():
    # 從回傳的 URL 擷取 code
    code = request.args.get('code')
    if code:
        print("授權碼: ", code)
        # 您可以在這裡使用 code 進行後續操作（例如換取 access token）
        # 將授權碼寫入 auth_code.txt
        with open("auth_code.txt", "w") as file:
            file.write(code)
        return f"授權成功！授權碼為：{code}"
    else:
        return "未能取得授權碼，請重新授權。"

if __name__ == '__main__':
    app.run(port=8888)
