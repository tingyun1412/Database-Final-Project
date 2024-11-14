
import webbrowser

client_id = "01dfa2aba3384ac4ba4b278af29d2f6d"
redirect_uri = "http://localhost:8888/callback"  # 你設定的 Redirect URI
scope = "user-top-read"  # 設定需要的權限範圍

# 生成授權 URL
auth_url = (
    "https://accounts.spotify.com/authorize"
    f"?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"
)

# 打開瀏覽器訪問 URL
webbrowser.open(auth_url)




