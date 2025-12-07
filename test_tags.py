import pytest


class TestTagsEndpoints:
    """Testy integracyjne dla endpointów /tags"""

    # ==================== GET LIST ====================

    def test_get_tags_returns_all_items(self, client, sample_tags):
        """Test GET /tags - zwraca wszystkie tagi z bazy"""
        response = client.get("/tags")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["userId"] == 2
        assert data[0]["tag"] == "funny"

    def test_get_tags_empty_database(self, client):
        """Test GET /tags - zwraca pustą listę gdy brak tagów"""
        response = client.get("/tags")
        
        assert response.status_code == 200
        assert response.json() == []

    # ==================== GET ITEM ====================

    def test_get_tag_by_id_success(self, client, single_tag):
        """Test GET /tags/{tag_id} - zwraca tag o podanym ID"""
        response = client.get(f"/tags/{single_tag.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == single_tag.id
        assert data["userId"] == 99
        assert data["movieId"] == 99
        assert data["tag"] == "test tag"

    def test_get_tag_not_found(self, client):
        """Test GET /tags/{tag_id} - zwraca 404 dla nieistniejącego ID"""
        response = client.get("/tags/99999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Tag not found"

    # ==================== POST ====================

    def test_create_tag_success(self, client, db_session):
        """Test POST /tags - tworzy nowy tag"""
        tag_data = {
            "userId": 10,
            "movieId": 20,
            "tag": "great movie",
            "timestamp": 1234567890
        }
        
        response = client.post("/tags", json=tag_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["userId"] == 10
        assert data["movieId"] == 20
        assert data["tag"] == "great movie"
        assert "id" in data 
        
        verify_response = client.get(f"/tags/{data['id']}")
        assert verify_response.status_code == 200

    def test_create_tag_without_optional_fields(self, client):
        """Test POST /tags - tworzy tag bez opcjonalnych pól"""
        tag_data = {
            "userId": 15,
            "movieId": 25
        }
        
        response = client.post("/tags", json=tag_data)
        
        assert response.status_code == 201
        assert response.json()["userId"] == 15

    # ==================== PUT ====================

    def test_update_tag_success(self, client, single_tag):
        """Test PUT /tags/{tag_id} - aktualizuje tag"""
        update_data = {
            "tag": "updated tag"
        }
        
        response = client.put(f"/tags/{single_tag.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["tag"] == "updated tag"
        
        verify_response = client.get(f"/tags/{single_tag.id}")
        assert verify_response.json()["tag"] == "updated tag"

    def test_update_tag_not_found(self, client):
        """Test PUT /tags/{tag_id} - zwraca 404 dla nieistniejącego ID"""
        update_data = {"tag": "new tag"}
        
        response = client.put("/tags/99999", json=update_data)
        
        assert response.status_code == 404

    # ==================== DELETE ====================

    def test_delete_tag_success(self, client, single_tag):
        """Test DELETE /tags/{tag_id} - usuwa tag"""
        response = client.delete(f"/tags/{single_tag.id}")
        
        assert response.status_code == 204
        
        verify_response = client.get(f"/tags/{single_tag.id}")
        assert verify_response.status_code == 404

    def test_delete_tag_not_found(self, client):
        """Test DELETE /tags/{tag_id} - zwraca 404 dla nieistniejącego ID"""
        response = client.delete("/tags/99999")
        
        assert response.status_code == 404
