from sqlalchemy import Column, Integer, String, Float, Text
from database import Base

class Movie(Base):
    __tablename__ = "movies"
    
    movieId = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    genres = Column(String(255))

class Link(Base):
    __tablename__ = "links"
    
    movieId = Column(Integer, primary_key=True, index=True)
    imdbId = Column(String(20))
    tmdbId = Column(String(20))

class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, nullable=False)
    movieId = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)
    timestamp = Column(Integer)

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, nullable=False)
    movieId = Column(Integer, nullable=False)
    tag = Column(Text)
    timestamp = Column(Integer)
