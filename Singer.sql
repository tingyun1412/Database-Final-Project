CREATE TABLE Singer (
    singer_name VARCHAR(255) PRIMARY KEY,
    singer_gender VARCHAR(10),
    singer_age INT,
    singer_type VARCHAR(50),
    singer_nation VARCHAR(50)
);

CREATE TABLE SingerStaging (
    singer_name VARCHAR(255),
    singer_gender VARCHAR(10),
    singer_age INT,
    singer_type VARCHAR(50),
    singer_nation VARCHAR(50)
);

LOAD DATA INFILE "C:\Users\User\Desktop\DBMS\Database-Final-Project\singer1114.csv"
INTO TABLE SingerStaging
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@dummy, @dummy, @artist, @gender, @age, @type, @country, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy)
SET singer_name = @artist, 
    singer_gender = @gender, 
    singer_age = NULLIF(@age, ''),
    singer_type = @type, 
    singer_nation = @country;

INSERT INTO Singer (singer_name, singer_gender, singer_age, singer_type, singer_nation)
SELECT singer_name, singer_gender, singer_age, singer_type, singer_nation
FROM SingerStaging
WHERE singer_age IS NOT NULL
ON DUPLICATE KEY UPDATE 
    singer_gender = VALUES(singer_gender),
    singer_age = VALUES(singer_age),
    singer_type = VALUES(singer_type),
    singer_nation = VALUES(singer_nation);
    
SELECT *
FROM Singer
INTO OUTFILE '/var/lib/mysql-files/Singer_output.csv'
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n';
