--- people table
CREATE TABLE people (
    person_id SERIAL PRIMARY KEY,
    full_name TEXT,
    team TEXT,
    badge_uid TEXT UNIQUE
);

COPY people (person_id, full_name, team, badge_uid)
FROM '/data/people.csv'
DELIMITER ','
CSV HEADER;

--- purchases table
CREATE TABLE purchases (
    purchase_id INT PRIMARY KEY,
    badge_uid TEXT,
    location TEXT,
    product TEXT,
    qty INT,
    ts TIMESTAMP,
    FOREIGN KEY (badge_uid) REFERENCES people(badge_uid)
);


COPY purchases (purchase_id, badge_uid, location, product, qty, ts)
FROM '/data/purchases.csv'
DELIMITER ','
CSV HEADER;


--- sessions table
CREATE TABLE sessions (
    session_code TEXT PRIMARY KEY,
    session_name TEXT
);


COPY sessions (session_code, session_name)
FROM '/data/sessions.csv'
DELIMITER ','
CSV HEADER;

--- swipes table
CREATE TABLE swipes (
    badge_uid TEXT,
    session_code TEXT,
    ts TIMESTAMP
);


COPY swipes (badge_uid, session_code, ts)
FROM '/data/swipes.csv'
DELIMITER ','
CSV HEADER;
