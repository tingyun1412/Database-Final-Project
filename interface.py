from flask import Flask, render_template, request, jsonify
import csv
import mysql.connector
from collections import Counter

# Flask App Initialization
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'yourpassword',
    'database': 'final'
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
        cursor.execute(
            "SELECT p.song_name, p.singer_name, p.song_language,s.song_genre,s.song_timing FROM playlist p JOIN Song s ON s.song_name=p.song_name"
        )
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



if __name__ == '__main__':
    app.run(debug=True)
