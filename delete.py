import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    db.execute("DELETE FROM books WHERE ID = 1")
    db.commit()

if __name__ == '__main__':
    main()
