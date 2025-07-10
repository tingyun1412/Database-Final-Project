# 🎧 Database Final Project：Spotify Music Analyzing & Create a Playlist

## 📌 Project Purpose

This application utilizes the Spotify API to collect a user's top 20 most-listened-to tracks in the past six months. It analyzes the data (such as song language, genre, artist, timing, gender, etc.), visualizes the statistics, and allows users to **filter and generate customized Spotify playlists** based on their preferences.

---

## 💾 Data Sources

| Table    | Source |
|----------|--------|
| `Album`  | Album dataset |
| `Singer` | Spotify Artist Metadata (Top 10k) |
| `Song`   | Spotify Tracks Dataset |
| `Playlist` | Spotify API |

- **ER diagram** and schema are detailed in the project report (`Database_Project_Team04.pdf`)

---
## 🔧 Application Workflow

### 🔐 1. Login (Spotify Authorization)
- User clicks to authorize with Spotify
- Application retrieves access token
- Fetches top 20 tracks via Spotify API
- Song lyrics are analyzed with **Genius API** to detect language
- Data is saved to `playlist.csv`

---

### 📊 2. Data Analysis
- CSV data is imported into MySQL (`Playlist` table)
- Joined with `Song`, `Singer`, and `Album` tables
- Returns info like:
  - Genre
  - Emotion
  - Album name
  - Singer gender
- Data is displayed in HTML tables + **pie charts**

---

### 🎼 3. Playlist Creation
- User selects filtering options (genre/language/etc.)
- Application uses selected options to filter songs
- Sends request to Spotify API to generate a new playlist
- Playlist link is returned and displayed

---
## 🔗 Links

- **GitHub Repository**:  
  [https://github.com/tingyun1412/Database-Final-Project](https://github.com/tingyun1412/Database-Final-Project)

- **Demo Video**:  
  [https://youtu.be/Xta4iSIw7hg?si=5s8pI2CYruIfi_Oq](https://youtu.be/Xta4iSIw7hg?si=5s8pI2CYruIfi_Oq)

