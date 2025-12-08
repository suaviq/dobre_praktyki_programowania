import pytest


class TestMoviesEndpoints:
    """Testy integracyjne dla endpointów /movies"""

    # ==================== GET LIST ====================
    
    def test_get_movies_returns_all_items(self, client, sample_movies, auth_headers):
        """Test GET /movies - zwraca wszystkie filmy z bazy"""
        response = client.get("/movies", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["movieId"] == 1
        assert data[0]["title"] == "Toy Story (1995)"

    def test_get_movies_empty_database(self, client, auth_headers):
        """Test GET /movies - zwraca pustą listę gdy brak filmów"""
        response = client.get("/movies", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json() == []

    # ==================== GET ITEM ====================

    def test_get_movie_by_id_success(self, client, single_movie, auth_headers):
        """Test GET /movies/{movie_id} - zwraca film o podanym ID"""
        response = client.get(f"/movies/{single_movie.movieId}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["movieId"] == 100
        assert data["title"] == "Test Movie"
        assert data["genres"] == "Drama"

    def test_get_movie_not_found(self, client, auth_headers):
        """Test GET /movies/{movie_id} - zwraca 404 dla nieistniejącego ID"""
        response = client.get("/movies/99999", headers=auth_headers)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Movie not found"

    # ==================== POST ====================

    def test_create_movie_success(self, client, db_session, auth_headers):
        """Test POST /movies - tworzy nowy film"""
        movie_data = {
            "movieId": 999,
            "title": "New Test Movie",
            "genres": "Action|Thriller"
        }
        
        response = client.post("/movies", json=movie_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["movieId"] == 999
        assert data["title"] == "New Test Movie"
        assert data["genres"] == "Action|Thriller"
        
        verify_response = client.get("/movies/999", headers=auth_headers)
        assert verify_response.status_code == 200

    def test_create_movie_duplicate_id(self, client, single_movie, auth_headers):
        """Test POST /movies - zwraca błąd dla duplikatu ID"""
        movie_data = {
            "movieId": 100,
            "title": "Duplicate Movie",
            "genres": "Comedy"
        }
        
        response = client.post("/movies", json=movie_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    # ==================== PUT ====================

    def test_update_movie_success(self, client, single_movie, auth_headers):
        """Test PUT /movies/{movie_id} - aktualizuje film"""
        update_data = {
            "title": "Updated Title",
            "genres": "Comedy|Drama"
        }
        
        response = client.put(f"/movies/{single_movie.movieId}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["genres"] == "Comedy|Drama"
        
        verify_response = client.get(f"/movies/{single_movie.movieId}", headers=auth_headers)
        assert verify_response.json()["title"] == "Updated Title"

    def test_update_movie_not_found(self, client, auth_headers):
        """Test PUT /movies/{movie_id} - zwraca 404 dla nieistniejącego ID"""
        update_data = {"title": "Some Title", "genres": "Drama"}
        
        response = client.put("/movies/99999", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404

    # ==================== DELETE ====================

    def test_delete_movie_success(self, client, single_movie, auth_headers):
        """Test DELETE /movies/{movie_id} - usuwa film"""
        response = client.delete(f"/movies/{single_movie.movieId}", headers=auth_headers)
        
        assert response.status_code == 204
        
        verify_response = client.get(f"/movies/{single_movie.movieId}", headers=auth_headers)
        assert verify_response.status_code == 404

    def test_delete_movie_not_found(self, client, auth_headers):
        """Test DELETE /movies/{movie_id} - zwraca 404 dla nieistniejącego ID"""
        response = client.delete("/movies/99999", headers=auth_headers)
        
        assert response.status_code == 404
