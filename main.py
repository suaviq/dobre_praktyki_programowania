from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import engine, get_db, Base
from models import Movie, Link, Rating, Tag, User
from schemas import (
    Movie as MovieSchema, MovieCreate, MovieUpdate,
    Link as LinkSchema, LinkCreate, LinkUpdate,
    Rating as RatingSchema, RatingCreate, RatingUpdate,
    Tag as TagSchema, TagCreate, TagUpdate,
    UserCreate, User as UserSchema, LoginRequest, Token
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, require_admin
)

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
async def root():
    return {"hello": "world"}

# ==================== AUTH ENDPOINTS ====================

@app.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Endpoint do logowania - zwraca JWT token"""
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    roles = user.roles.split(",") if user.roles else ["ROLE_USER"]
    token = create_access_token(user.username, roles)
    
    return {"access_token": token, "token_type": "bearer"}


@app.post("/users", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Tworzy nowego użytkownika - tylko dla ROLE_ADMIN"""
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    db_user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        roles=",".join(user_data.roles) if user_data.roles else "ROLE_USER"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "id": db_user.id,
        "username": db_user.username,
        "roles": db_user.roles.split(",") if db_user.roles else ["ROLE_USER"]
    }


@app.get("/user_details")
async def get_user_details(current_user: dict = Depends(get_current_user)):
    """Zwraca dane użytkownika z payloadu JWT"""
    return {
        "username": current_user["username"],
        "roles": current_user["roles"]
    }

# ==================== MOVIES ENDPOINTS ====================

@app.get("/movies", response_model=List[MovieSchema])
async def get_movies(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """GET - lista wszystkich filmów"""
    movies = db.query(Movie).all()
    return movies

@app.get("/movies/{movie_id}", response_model=MovieSchema)
async def get_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """GET - pojedynczy film po ID"""
    movie = db.query(Movie).filter(Movie.movieId == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@app.post("/movies", response_model=MovieSchema, status_code=status.HTTP_201_CREATED)
async def create_movie(
    movie: MovieCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """POST - tworzenie nowego filmu"""
    existing = db.query(Movie).filter(Movie.movieId == movie.movieId).first()
    if existing:
        raise HTTPException(status_code=400, detail="Movie with this ID already exists")
    
    db_movie = Movie(**movie.model_dump())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

@app.put("/movies/{movie_id}", response_model=MovieSchema)
async def update_movie(
    movie_id: int,
    movie: MovieUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """PUT - aktualizacja filmu"""
    db_movie = db.query(Movie).filter(Movie.movieId == movie_id).first()
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    update_data = movie.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_movie, key, value)
    
    db.commit()
    db.refresh(db_movie)
    return db_movie

@app.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """DELETE - usuwanie filmu"""
    db_movie = db.query(Movie).filter(Movie.movieId == movie_id).first()
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    db.delete(db_movie)
    db.commit()
    return None

# ==================== LINKS ENDPOINTS ====================

@app.get("/links", response_model=List[LinkSchema])
async def get_links(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """GET - lista wszystkich linków"""
    links = db.query(Link).all()
    return links

@app.get("/links/{movie_id}", response_model=LinkSchema)
async def get_link(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """GET - pojedynczy link po movie_id"""
    link = db.query(Link).filter(Link.movieId == movie_id).first()
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return link

@app.post("/links", response_model=LinkSchema, status_code=status.HTTP_201_CREATED)
async def create_link(
    link: LinkCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """POST - tworzenie nowego linku"""
    existing = db.query(Link).filter(Link.movieId == link.movieId).first()
    if existing:
        raise HTTPException(status_code=400, detail="Link for this movie already exists")
    
    db_link = Link(**link.model_dump())
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

@app.put("/links/{movie_id}", response_model=LinkSchema)
async def update_link(
    movie_id: int,
    link: LinkUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """PUT - aktualizacja linku"""
    db_link = db.query(Link).filter(Link.movieId == movie_id).first()
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    
    update_data = link.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_link, key, value)
    
    db.commit()
    db.refresh(db_link)
    return db_link

@app.delete("/links/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """DELETE - usuwanie linku"""
    db_link = db.query(Link).filter(Link.movieId == movie_id).first()
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    
    db.delete(db_link)
    db.commit()
    return None

# ==================== RATINGS ENDPOINTS ====================

@app.get("/ratings", response_model=List[RatingSchema])
async def get_ratings(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """GET - lista wszystkich ocen"""
    ratings = db.query(Rating).all()
    return ratings

@app.get("/ratings/{rating_id}", response_model=RatingSchema)
async def get_rating(
    rating_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """GET - pojedyncza ocena po ID"""
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating

@app.post("/ratings", response_model=RatingSchema, status_code=status.HTTP_201_CREATED)
async def create_rating(
    rating: RatingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """POST - tworzenie nowej oceny"""
    db_rating = Rating(**rating.model_dump())
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating

@app.put("/ratings/{rating_id}", response_model=RatingSchema)
async def update_rating(
    rating_id: int,
    rating: RatingUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """PUT - aktualizacja oceny"""
    db_rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if db_rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")
    
    update_data = rating.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_rating, key, value)
    
    db.commit()
    db.refresh(db_rating)
    return db_rating

@app.delete("/ratings/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rating(
    rating_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """DELETE - usuwanie oceny"""
    db_rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if db_rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")
    
    db.delete(db_rating)
    db.commit()
    return None

# ==================== TAGS ENDPOINTS ====================

@app.get("/tags", response_model=List[TagSchema])
async def get_tags(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """GET - lista wszystkich tagów"""
    tags = db.query(Tag).all()
    return tags

@app.get("/tags/{tag_id}", response_model=TagSchema)
async def get_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """GET - pojedynczy tag po ID"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

@app.post("/tags", response_model=TagSchema, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """POST - tworzenie nowego tagu"""
    db_tag = Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@app.put("/tags/{tag_id}", response_model=TagSchema)
async def update_tag(
    tag_id: int,
    tag: TagUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """PUT - aktualizacja tagu"""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    update_data = tag.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tag, key, value)
    
    db.commit()
    db.refresh(db_tag)
    return db_tag

@app.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """DELETE - usuwanie tagu"""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    db.delete(db_tag)
    db.commit()
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
