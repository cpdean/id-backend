drop table if exists Post;
create table post (
        post_id integer primary key autoincrement,
        date TIMESTAMP,
        title string,
        body  string,
        image_path string
);
