CREATE TABLE Song (
    song_id varchar(50),
    song_name varchar(200),
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
    PRIMARY KEY (song_name)
);
CREATE TABLE SongStaging (
    song_id varchar(50),
    song_name varchar(200),
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
    song_genre varchar(50)
);

LOAD DATA INFILE '/var/lib/mysql-files/Song.csv'
IGNORE INTO TABLE SongStaging
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(@dummy, @track_id, @dummy, @dummy, @track_name, @dummy, @dummy, @dummy, @dummy, @energy, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, @track_genre)
SET song_id = @track_id, 
    song_name = @track_name, 
    energy = @energy,
    song_genre = @track_genre;

INSERT INTO Song (song_id, song_name, energy, song_timing, song_genre)
SELECT song_id, song_name, energy, song_timing, song_genre
FROM SongStaging
ON DUPLICATE KEY UPDATE 
    song_id = VALUES(song_id),
    energy = VALUES(energy),
    song_timing = VALUES(song_timing)
    song_genre = VALUES(song_genre);
    
INSERT INTO Song (song_id, song_name, energy, song_genre)
SELECT song_id, song_name, energy, song_genre
FROM SongStaging
ON DUPLICATE KEY UPDATE 
    song_id = SongStaging.song_id,
    energy = SongStaging.energy,
    song_genre = SongStaging.song_genre;

(SELECT 'song_id', 'song_name', 'energy', 'song_timing', 'song_genre')
UNION ALL
(SELECT song_id, song_name, CAST(energy AS CHAR), song_timing, song_genre
FROM Song)
INTO OUTFILE '/var/lib/mysql-files/Song_output.csv'
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';