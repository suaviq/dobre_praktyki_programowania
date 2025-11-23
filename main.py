from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import csv
import os
from typing import List

from database import engine, get_db, Base
from models import Movie, Link, Rating, Tag
from schemas import Movie as MovieSchema, Link as LinkSchema, Rating as RatingSchema, Tag as TagSchema

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
async def root():
    return {"hello": "world"}

# Endpointy API
@app.get("/movies", response_model=List[MovieSchema])
async def get_movies(db: Session = Depends(get_db)):
    movies = db.query(Movie).all()
    return movies

@app.get("/links", response_model=List[LinkSchema])
async def get_links(db: Session = Depends(get_db)):
    links = db.query(Link).all()
    return links

@app.get("/ratings", response_model=List[RatingSchema])
async def get_ratings(db: Session = Depends(get_db)):
    ratings = db.query(Rating).all()
    return ratings

@app.get("/tags", response_model=List[TagSchema])
async def get_tags(db: Session = Depends(get_db)):
    tags = db.query(Tag).all()
    return tags

def load_data_from_csv():
    db = next(get_db())
    try:
        if db.query(Movie).count() > 0:
            print("Dane już zostały załadowane do bazy.")
            return
        
        print("Ładowanie danych z plików CSV do bazy...")
        
        if os.path.exists('data/movies.csv'):
            with open('data/movies.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    movie = Movie(
                        movieId=int(row['movieId']),
                        title=row['title'],
                        genres=row['genres']
                    )
                    db.add(movie)
            db.commit()
            print("Filmy załadowane")
        
        if os.path.exists('data/links.csv'):
            with open('data/links.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    link = Link(
                        movieId=int(row['movieId']),
                        imdbId=row['imdbId'],
                        tmdbId=row['tmdbId'] if row['tmdbId'] else None
                    )
                    db.add(link)
            db.commit()
            print("Linki załadowane")
        
        if os.path.exists('data/ratings.csv'):
            with open('data/ratings.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for i, row in enumerate(reader):
                    rating = Rating(
                        userId=int(row['userId']),
                        movieId=int(row['movieId']),
                        rating=float(row['rating']),
                        timestamp=int(row['timestamp']) if row['timestamp'] else None
                    )
                    db.add(rating)
                    if i % 1000 == 0:
                        db.commit()
            db.commit()
            print("Oceny załadowane")
        
        if os.path.exists('data/tags.csv'):
            with open('data/tags.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    tag = Tag(
                        userId=int(row['userId']),
                        movieId=int(row['movieId']),
                        tag=row['tag'],
                        timestamp=int(row['timestamp']) if row['timestamp'] else None
                    )
                    db.add(tag)
            db.commit()
            print("Tagi załadowane")
            
        print("Wszystkie dane zostały załadowane do bazy!")
        
    except Exception as e:
        db.rollback()
        print(f"Błąd podczas ładowania danych: {e}")
    finally:
        db.close()

@app.post("/load-data")
async def load_data():
    load_data_from_csv()
    return {"message": "Dane załadowane do bazy"}

@app.on_event("startup")
async def startup_event():
    load_data_from_csv()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)