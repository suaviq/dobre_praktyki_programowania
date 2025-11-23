from pydantic import BaseModel
from typing import Optional

class MovieBase(BaseModel):
    movieId: int
    title: str
    genres: Optional[str] = None

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    class Config:
        from_attributes = True

class LinkBase(BaseModel):
    movieId: int
    imdbId: Optional[str] = None
    tmdbId: Optional[str] = None

class LinkCreate(LinkBase):
    pass

class Link(LinkBase):
    class Config:
        from_attributes = True

class RatingBase(BaseModel):
    userId: int
    movieId: int
    rating: float
    timestamp: Optional[int] = None

class RatingCreate(RatingBase):
    pass

class Rating(RatingBase):
    id: int
    
    class Config:
        from_attributes = True

class TagBase(BaseModel):
    userId: int
    movieId: int
    tag: Optional[str] = None
    timestamp: Optional[int] = None

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    
    class Config:
        from_attributes = True