import pytest


class TestRatingsEndpoints:
    """Testy integracyjne dla endpointów /ratings"""

    # ==================== GET LIST ====================

    def test_get_ratings_returns_all_items(self, client, sample_ratings, auth_headers):
        """Test GET /ratings - zwraca wszystkie oceny z bazy"""
        response = client.get("/ratings", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["userId"] == 1
        assert data[0]["rating"] == 4.0

    def test_get_ratings_empty_database(self, client, auth_headers):
        """Test GET /ratings - zwraca pustą listę gdy brak ocen"""
        response = client.get("/ratings", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json() == []

    # ==================== GET ITEM ====================

    def test_get_rating_by_id_success(self, client, single_rating, auth_headers):
        """Test GET /ratings/{rating_id} - zwraca ocenę o podanym ID"""
        response = client.get(f"/ratings/{single_rating.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == single_rating.id
        assert data["userId"] == 99
        assert data["movieId"] == 99
        assert data["rating"] == 3.5

    def test_get_rating_not_found(self, client, auth_headers):
        """Test GET /ratings/{rating_id} - zwraca 404 dla nieistniejącego ID"""
        response = client.get("/ratings/99999", headers=auth_headers)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Rating not found"

    # ==================== POST ====================

    def test_create_rating_success(self, client, db_session, auth_headers):
        """Test POST /ratings - tworzy nową ocenę"""
        rating_data = {
            "userId": 10,
            "movieId": 20,
            "rating": 4.5,
            "timestamp": 1234567890
        }
        
        response = client.post("/ratings", json=rating_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["userId"] == 10
        assert data["movieId"] == 20
        assert data["rating"] == 4.5
        assert "id" in data  
        
        verify_response = client.get(f"/ratings/{data['id']}", headers=auth_headers)
        assert verify_response.status_code == 200

    def test_create_rating_without_timestamp(self, client, auth_headers):
        """Test POST /ratings - tworzy ocenę bez timestamp (opcjonalne pole)"""
        rating_data = {
            "userId": 15,
            "movieId": 25,
            "rating": 2.0
        }
        
        response = client.post("/ratings", json=rating_data, headers=auth_headers)
        
        assert response.status_code == 201
        assert response.json()["rating"] == 2.0

    # ==================== PUT ====================

    def test_update_rating_success(self, client, single_rating, auth_headers):
        """Test PUT /ratings/{rating_id} - aktualizuje ocenę"""
        update_data = {
            "rating": 5.0
        }
        
        response = client.put(f"/ratings/{single_rating.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == 5.0
        
        verify_response = client.get(f"/ratings/{single_rating.id}", headers=auth_headers)
        assert verify_response.json()["rating"] == 5.0

    def test_update_rating_not_found(self, client, auth_headers):
        """Test PUT /ratings/{rating_id} - zwraca 404 dla nieistniejącego ID"""
        update_data = {"rating": 3.0}
        
        response = client.put("/ratings/99999", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404

    # ==================== DELETE ====================

    def test_delete_rating_success(self, client, single_rating, auth_headers):
        """Test DELETE /ratings/{rating_id} - usuwa ocenę"""
        response = client.delete(f"/ratings/{single_rating.id}", headers=auth_headers)
        
        assert response.status_code == 204
        
        verify_response = client.get(f"/ratings/{single_rating.id}", headers=auth_headers)
        assert verify_response.status_code == 404

    def test_delete_rating_not_found(self, client, auth_headers):
        """Test DELETE /ratings/{rating_id} - zwraca 404 dla nieistniejącego ID"""
        response = client.delete("/ratings/99999", headers=auth_headers)
        
        assert response.status_code == 404
