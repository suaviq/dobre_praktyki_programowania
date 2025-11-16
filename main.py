from fastapi import FastAPI
from pydantic import BaseModel
import csv
from typing import List

app = FastAPI()

@app.get("/")
async def root():
    return {"hello": "world"}

class Movie(BaseModel):
    movieId: int
    title: str
    genres: str

class Link(BaseModel):
    movieId: int
    imdbId: str
    tmdbId: str

class Rating(BaseModel):
    userId: int
    movieId: int
    rating: float
    timestamp: int

class Tag(BaseModel):
    userId: int
    movieId: int
    tag: str
    timestamp: int

def load_movies():
    movies = []
    with open('database/movies.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            movies.append(Movie(
                movieId=int(row['movieId']),
                title=row['title'],
                genres=row['genres']
            ))
    return movies

def load_links():
    links = []
    with open('database/links.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            links.append(Link(
                movieId=int(row['movieId']),
                imdbId=row['imdbId'],
                tmdbId=row['tmdbId'] if row['tmdbId'] else ""
            ))
    return links

def load_ratings():
    ratings = []
    with open('database/ratings.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            ratings.append(Rating(
                userId=int(row['userId']),
                movieId=int(row['movieId']),
                rating=float(row['rating']),
                timestamp=int(row['timestamp'])
            ))
    return ratings

def load_tags():
    tags = []
    with open('database/tags.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            tags.append(Tag(
                userId=int(row['userId']),
                movieId=int(row['movieId']),
                tag=row['tag'],
                timestamp=int(row['timestamp'])
            ))
    return tags

@app.get("/movies", response_model=List[Movie])
async def get_movies():
    return load_movies()

@app.get("/links", response_model=List[Link])
async def get_links():
    return load_links()

@app.get("/ratings", response_model=List[Rating])
async def get_ratings():
    return load_ratings()

@app.get("/tags", response_model=List[Tag])
async def get_tags():
    return load_tags()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)