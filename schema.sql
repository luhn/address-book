drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  forename string not null,
  surname string not null,
  email string,
  phone string
);

