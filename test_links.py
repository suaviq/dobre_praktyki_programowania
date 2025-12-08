import pytest


class TestLinksEndpoints:
    """Testy integracyjne dla endpointów /links"""

    # ==================== GET LIST ====================

    def test_get_links_returns_all_items(self, client, sample_links, auth_headers):
        """Test GET /links - zwraca wszystkie linki z bazy"""
        response = client.get("/links", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["movieId"] == 1
        assert data[0]["imdbId"] == "0114709"

    def test_get_links_empty_database(self, client, auth_headers):
        """Test GET /links - zwraca pustą listę gdy brak linków"""
        response = client.get("/links", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json() == []

    # ==================== GET ITEM ====================

    def test_get_link_by_movie_id_success(self, client, single_link, auth_headers):
        """Test GET /links/{movie_id} - zwraca link dla danego movie_id"""
        response = client.get(f"/links/{single_link.movieId}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["movieId"] == 100
        assert data["imdbId"] == "9999999"
        assert data["tmdbId"] == "99999"

    def test_get_link_not_found(self, client, auth_headers):
        """Test GET /links/{movie_id} - zwraca 404 dla nieistniejącego movie_id"""
        response = client.get("/links/99999", headers=auth_headers)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Link not found"

    # ==================== POST ====================

    def test_create_link_success(self, client, db_session, auth_headers):
        """Test POST /links - tworzy nowy link"""
        link_data = {
            "movieId": 999,
            "imdbId": "1234567",
            "tmdbId": "12345"
        }
        
        response = client.post("/links", json=link_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["movieId"] == 999
        assert data["imdbId"] == "1234567"
        assert data["tmdbId"] == "12345"
        
        verify_response = client.get("/links/999", headers=auth_headers)
        assert verify_response.status_code == 200

    def test_create_link_duplicate_movie_id(self, client, single_link, auth_headers):
        """Test POST /links - zwraca błąd dla duplikatu movie_id"""
        link_data = {
            "movieId": 100, 
            "imdbId": "0000000",
            "tmdbId": "00000"
        }
        
        response = client.post("/links", json=link_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    # ==================== PUT ====================

    def test_update_link_success(self, client, single_link, auth_headers):
        """Test PUT /links/{movie_id} - aktualizuje link"""
        update_data = {
            "imdbId": "7777777",
            "tmdbId": "77777"
        }
        
        response = client.put(f"/links/{single_link.movieId}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["imdbId"] == "7777777"
        assert data["tmdbId"] == "77777"
        
        verify_response = client.get(f"/links/{single_link.movieId}", headers=auth_headers)
        assert verify_response.json()["imdbId"] == "7777777"

    def test_update_link_not_found(self, client, auth_headers):
        """Test PUT /links/{movie_id} - zwraca 404 dla nieistniejącego movie_id"""
        update_data = {"imdbId": "0000000", "tmdbId": "00000"}
        
        response = client.put("/links/99999", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404

    # ==================== DELETE ====================

    def test_delete_link_success(self, client, single_link, auth_headers):
        """Test DELETE /links/{movie_id} - usuwa link"""
        response = client.delete(f"/links/{single_link.movieId}", headers=auth_headers)
        
        assert response.status_code == 204
        
        verify_response = client.get(f"/links/{single_link.movieId}", headers=auth_headers)
        assert verify_response.status_code == 404

    def test_delete_link_not_found(self, client, auth_headers):
        """Test DELETE /links/{movie_id} - zwraca 404 dla nieistniejącego movie_id"""
        response = client.delete("/links/99999", headers=auth_headers)
        
        assert response.status_code == 404
