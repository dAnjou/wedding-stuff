drop table if exists greets;
create table greets (
  id integer primary key autoincrement,
  author string not null,
  message string not null
);