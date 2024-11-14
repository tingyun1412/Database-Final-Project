CREATE TABLE Song (
    song_id varchar(50),
    song_name varchar(50),
    energy decimal(5,4),
    song_timing varchar(50) AS (
        CASE
            WHEN energy BETWEEN 0.0 AND 0.2 THEN 'calm'
            WHEN energy BETWEEN 0.2 AND 0.4 THEN 'mellow'
            WHEN energy BETWEEN 0.4 AND 0.6 THEN 'neutral'
            WHEN energy BETWEEN 0.6 AND 0.8 THEN 'energetic'
            WHEN energy BETWEEN 0.8 AND 1.0 THEN 'high energy'
        END
    ) STORED,
    song_genre varchar(50),
    song_language varchar(50) DEFAULT NULL,
    PRIMARY KEY (song_id)
);
LOAD DATA LOCAL INFILE 'your_file_path.csv'
INTO TABLE Song
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(song_id, @dummy, album_name, song_name, @dummy, @dummy, @dummy, @dummy, energy, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, song_genre);

create table Album(
    album_name varchar(50) primary key,
    song_id varchar(50),
    song_name varchar(50),
    singer_name varchar(50),
    foreign key(song_id) references Song(song_id),
    foreign key(singer_name) references Singer(singer_name)
)
LOAD DATA LOCAL INFILE 'your_file_path.csv'
INTO TABLE Album
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(song_id,song_name,@dummy,singer_name,album_name,@dummy,@dummy,@dummy);