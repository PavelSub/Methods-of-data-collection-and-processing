from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session
from sqlalchemy import (
        Column,
        Integer,
        ForeignKey,
        String,
        Table,
        DateTime,
)

Base = declarative_base()
association_table = Table('association_table', Base.metadata,
                          Column('news_id', Integer, ForeignKey('news.id')),
                          Column('comment_author_id', Integer, ForeignKey('comment_author.id')))


class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    com_quantity = Column(Integer, unique=False, nullable=True)
    pub_time = Column(DateTime, unique=False, nullable=False)
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship('Author', back_populates='news')
    comment_authors = relationship("CommentAuthor", secondary=association_table, backref="news")

    def __init__(self, title, url, com_quantity, pub_time, author, comment_authors):
        self.title = title
        self.url = url
        self.com_quantity = com_quantity
        self.pub_time = pub_time
        self.author = author
        self.comment_authors = comment_authors


class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    url = Column(String, unique=True, nullable=False)
    news = relationship('News', back_populates='author')

    def __init__(self, name, url):
        self.name = name
        self.url = url


class CommentAuthor(Base):
    __tablename__ = 'comment_author'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    url = Column(String, unique=True, nullable=False)

    def __init__(self, name, url):
        self.name = name
        self.url = url


def sel_unique(session, cl, name, url):
    query = session.query(cl)
    tmp = query.filter(cl.url == url)
    res = tmp.all()
    return cl(name, url) if len(res) == 0 or res is None else res[0]


def save_at_db(data):

    engine = create_engine('sqlite:///habr_news.db')
    Base.metadata.create_all(engine)
    session_db = sessionmaker(bind=engine)

    session = session_db()

    for d in data:
        au = sel_unique(session, Author, d['author']['name'], d['author']['url'])
        com_au = [sel_unique(session, CommentAuthor, au['name'], au['url']) for au in d['com_authors']]

        new = News(d['title'], d['url'], d['com_quantity'], d['pub_time'], au, com_au)
        session.add(new)

        try:
            session.commit()
        except Exception as e:
            session.rollback()
            print(e)




