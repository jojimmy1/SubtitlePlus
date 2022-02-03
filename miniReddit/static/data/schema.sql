CREATE TABLE users(
    first_name text,
    last_name text,
    userID text primary key,
    hashcode int,
	filename1 text
);

CREATE TABLE posts(
    post_id text primary key,
    title text,
    content text,
    create_time text,
    vote_count int,
    userID text,
    FOREIGN KEY (userID)
        REFERENCES users (userID)
);

CREATE TABLE vote(
    post_id text,
    userID text,
	idx int primary key,
	FOREIGN KEY (post_id)
        REFERENCES posts (post_id)
);