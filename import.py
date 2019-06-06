import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
#db.execute("insert into books(isbn, title, author, year) VALUES(12312,'safdf','sdfa','1239')")
#db.commit()
db.execute('CREATE TABLE IF NOT EXISTS books (isbn VARCHAR PRIMARY KEY, title VARCHAR, author VARCHAR, year VARCHAR)')
db.commit()


f = open("books.csv")
reader = csv.reader(f)
for isbn, title, author, year in reader:
    db.execute("insert into books(isbn, title, author, year) VALUES(:isbn,:title,:author,:year)",
    {"isbn": isbn,"title": title,"author": author,"year": year})
    print(f'{isbn}-{title}-{author}-{year}')
db.commit()
        