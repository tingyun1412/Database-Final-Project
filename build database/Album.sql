CREATE TABLE Album (
    album_name VARCHAR(255),
    song_id VARCHAR(50),
    song_name VARCHAR(255),
    singer_name VARCHAR(255),
    PRIMARY KEY(album_name, song_id, singer_name)
);

CREATE TABLE AlbumStaging (
    album_name VARCHAR(255),
    song_id VARCHAR(50),
    song_name VARCHAR(255),
    singer_name VARCHAR(255)
);

LOAD DATA INFILE '/var/lib/mysql-files/album.csv'
INTO TABLE AlbumStaging
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS

(@id, @name, @dummy, @artists, @album, @dummy, @dummy, @dummy)
SET album_name = @album, 
    song_id = @id, 
    song_name = @name,
    singer_name = @artists;

INSERT IGNORE INTO Album (album_name, song_id, song_name, singer_name)
SELECT album_name, song_id, song_name, singer_name
FROM AlbumStaging;

SELECT *
FROM Album
INTO OUTFILE '/var/lib/mysql-files/Album_output.csv'
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n';
