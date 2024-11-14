from flask import Flask, redirect, request
import webbrowser

app = Flask(__name__)

client_id = "01dfa2aba3384ac4ba4b278af29d2f6d"
redirect_uri = "http://localhost:8888/callback"
scope = "user-top-read"

@app.route("/")
def home():
    auth_url = (
        "https://accounts.spotify.com/authorize"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope}"
        f"&show_dialog=true"  # 添加這行以強制顯示登入對話框
    )
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if code:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Spotify 授權成功</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    background-color: #1DB954;
                    color: white;
                }}
                .container {{
                    background-color: rgba(0,0,0,0.8);
                    padding: 30px;
                    border-radius: 8px;
                    max-width: 600px;
                    margin: 0 auto;
                }}
                .code {{
                    background-color: rgba(255,255,255,0.1);
                    padding: 15px;
                    border-radius: 4px;
                    word-break: break-all;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>授權成功！</h1>
                <p>您的授權碼是：</p>
                <div class="code">{code}</div>
            </div>
        </body>
        </html>
        """
    return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>授權失敗</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    background-color: #ff4444;
                    color: white;
                }}
                .container {{
                    background-color: rgba(0,0,0,0.8);
                    padding: 30px;
                    border-radius: 8px;
                    max-width: 600px;
                    margin: 0 auto;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>授權失敗</h1>
                <p>未收到授權碼。</p>
            </div>
        </body>
        </html>
    """
    

if __name__ == "__main__":

    webbrowser.open("http://127.0.0.1:8888")
    app.run(port=8888, debug=False) 