import requests
from fuzzywuzzy import fuzz
from langid import classify
from bs4 import BeautifulSoup
import langid

# Genius API 設定
genius_access_token = 'mTFhullvxvc--JQf-ai9u9N33fw_fNDANvw3W7ogp7kFBGGocJFpgH4qEp4tJOCU'  # 替換為您的 Genius API 金鑰
genius_search_url = "https://api.genius.com/search"
genius_headers = {
    "Authorization": f"Bearer {genius_access_token}"
}

# 使用 Genius API 搜尋歌曲（允許部分相似搜尋）
def search_genius_lyrics(song_title, artist_name):
    params = {
        "q": f"{song_title} {artist_name}"
    }
    response = requests.get(genius_search_url, headers=genius_headers, params=params)
    if response.status_code == 200:
        results = response.json()['response']['hits']
        
        # 如果沒有結果，返回 None
        if not results:
            print("Genius 找不到對應的歌曲")
            return None
        
        # 計算相似度，選取最接近的結果
        best_match = None
        highest_score = 0
        for result in results:
            result_title = result['result']['title']
            result_artist = result['result']['primary_artist']['name']
            
            # 計算歌曲名稱和藝術家名稱的相似度
            if isinstance(artist_name, list):
                artist_name = " ".join(artist_name)
            title_score = fuzz.ratio(song_title.lower(), result_title.lower())
            artist_score = fuzz.ratio(artist_name.lower(), result_artist.lower())
            total_score = (title_score + artist_score) / 2
            
            # 更新最佳匹配
            if total_score > highest_score:
                highest_score = total_score
                best_match = result['result']
        
        # 如果找到足夠相似的結果，返回歌曲 URL
        if best_match and highest_score > 30:  # 設定相似度閾值，例如 70
            song_url = best_match['url']
            #print(f"找到最佳匹配: {best_match['title']} by {best_match['primary_artist']['name']} (相似度: {highest_score})")
            return song_url
        else:
            print("沒有找到足夠相似的歌曲")
            return None
    else:
        print("Genius API 請求失敗")
        return None

# 獲取歌詞（需要解析 Genius 網頁）
def get_lyrics_from_genius(song_url):
    # 使用 Genius 網頁中的 URL 獲取歌詞
    page = requests.get(song_url)
    soup = BeautifulSoup(page.text, 'html.parser')

    # 嘗試使用更通用的 class 選擇器來抓取歌詞
    lyrics = ""
    '''
    for div in soup.find_all("div", class_=lambda x: x and "Lyrics__Container" in x):
        lyrics += div.get_text(separator="\n")
    '''
    for div in soup.find_all("div", attrs={"data-lyrics-container": "true"}):
        lyrics += div.get_text(separator="\n")
    # 顯示解析出的歌詞
    if lyrics:

        print("成功取得歌詞")
        #
       # print("解析出的歌詞：")
        #print(lyrics)  # 顯示歌詞內容以供確認
        return lyrics
    else:
        print("無法取得歌詞")
        return None

# 判斷歌詞的語言
def detect_lyrics_language(lyrics):
    try:
        language, confidence = langid.classify(lyrics)
        #print(f"偵測到的語言: {language}")
        return language
    except:
        return "無法判斷語言"

