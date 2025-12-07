import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app
from models import Movie, Link, Rating, Tag

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Tworzy nową sesję bazy danych dla każdego testu"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Tworzy klienta testowego z nadpisaną zależnością bazy danych"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ==================== FIXTURES DLA MOVIES ====================

@pytest.fixture
def sample_movies(db_session):
    """Fixture tworzący przykładowe filmy w bazie"""
    movies = [
        Movie(movieId=1, title="Toy Story (1995)", genres="Adventure|Animation|Children|Comedy|Fantasy"),
        Movie(movieId=2, title="Jumanji (1995)", genres="Adventure|Children|Fantasy"),
        Movie(movieId=3, title="Grumpier Old Men (1995)", genres="Comedy|Romance"),
    ]
    for movie in movies:
        db_session.add(movie)
    db_session.commit()
    return movies


@pytest.fixture
def single_movie(db_session):
    """Fixture tworzący pojedynczy film"""
    movie = Movie(movieId=100, title="Test Movie", genres="Drama")
    db_session.add(movie)
    db_session.commit()
    return movie


# ==================== FIXTURES DLA LINKS ====================

@pytest.fixture
def sample_links(db_session):
    """Fixture tworzący przykładowe linki w bazie"""
    links = [
        Link(movieId=1, imdbId="0114709", tmdbId="862"),
        Link(movieId=2, imdbId="0113497", tmdbId="8844"),
        Link(movieId=3, imdbId="0113228", tmdbId="15602"),
    ]
    for link in links:
        db_session.add(link)
    db_session.commit()
    return links


@pytest.fixture
def single_link(db_session):
    """Fixture tworzący pojedynczy link"""
    link = Link(movieId=100, imdbId="9999999", tmdbId="99999")
    db_session.add(link)
    db_session.commit()
    return link


# ==================== FIXTURES DLA RATINGS ====================

@pytest.fixture
def sample_ratings(db_session):
    """Fixture tworzący przykładowe oceny w bazie"""
    ratings = [
        Rating(userId=1, movieId=1, rating=4.0, timestamp=964982703),
        Rating(userId=1, movieId=3, rating=4.0, timestamp=964981247),
        Rating(userId=2, movieId=1, rating=5.0, timestamp=964982224),
    ]
    for rating in ratings:
        db_session.add(rating)
    db_session.commit()
    for rating in ratings:
        db_session.refresh(rating)
    return ratings


@pytest.fixture
def single_rating(db_session):
    """Fixture tworzący pojedynczą ocenę"""
    rating = Rating(userId=99, movieId=99, rating=3.5, timestamp=1234567890)
    db_session.add(rating)
    db_session.commit()
    db_session.refresh(rating)
    return rating


# ==================== FIXTURES DLA TAGS ====================

@pytest.fixture
def sample_tags(db_session):
    """Fixture tworzący przykładowe tagi w bazie"""
    tags = [
        Tag(userId=2, movieId=60756, tag="funny", timestamp=1445714994),
        Tag(userId=2, movieId=60756, tag="Highly quotable", timestamp=1445714996),
        Tag(userId=2, movieId=89774, tag="Boxing story", timestamp=1445715207),
    ]
    for tag in tags:
        db_session.add(tag)
    db_session.commit()
    for tag in tags:
        db_session.refresh(tag)
    return tags


@pytest.fixture
def single_tag(db_session):
    """Fixture tworzący pojedynczy tag"""
    tag = Tag(userId=99, movieId=99, tag="test tag", timestamp=9999999999)
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    return tag
