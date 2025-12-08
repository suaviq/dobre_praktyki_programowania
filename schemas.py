from pydantic import BaseModel
from typing import Optional, List

# Movie schemas
class MovieBase(BaseModel):
    title: str
    genres: Optional[str] = None

class MovieCreate(MovieBase):
    movieId: int

class MovieUpdate(MovieBase):
    pass

class Movie(MovieBase):
    movieId: int
    
    class Config:
        from_attributes = True

# Link schemas
class LinkBase(BaseModel):
    imdbId: Optional[str] = None
    tmdbId: Optional[str] = None

class LinkCreate(LinkBase):
    movieId: int

class LinkUpdate(LinkBase):
    pass

class Link(LinkBase):
    movieId: int
    
    class Config:
        from_attributes = True

# Rating schemas
class RatingBase(BaseModel):
    userId: int
    movieId: int
    rating: float
    timestamp: Optional[int] = None

class RatingCreate(RatingBase):
    pass

class RatingUpdate(BaseModel):
    userId: Optional[int] = None
    movieId: Optional[int] = None
    rating: Optional[float] = None
    timestamp: Optional[int] = None

class Rating(RatingBase):
    id: int
    
    class Config:
        from_attributes = True

# Tag schemas
class TagBase(BaseModel):
    userId: int
    movieId: int
    tag: Optional[str] = None
    timestamp: Optional[int] = None

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    userId: Optional[int] = None
    movieId: Optional[int] = None
    tag: Optional[str] = None
    timestamp: Optional[int] = None

class Tag(TagBase):
    id: int
    
    class Config:
        from_attributes = True

# User schemas
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    roles: Optional[List[str]] = ["ROLE_USER"]

class User(UserBase):
    id: int
    roles: List[str]
    
    class Config:
        from_attributes = True

class UserInDB(User):
    password_hash: str

# Login and Token schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str  # username
    roles: List[str]
    exp: int
