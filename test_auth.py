import pytest


class TestLogin:
    """Testy dla endpointu /login"""
    
    def test_login_success(self, client, regular_user):
        """Test poprawnego logowania"""
        response = client.post("/login", json={
            "username": "user",
            "password": "userpass"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, regular_user):
        """Test logowania z błędnym hasłem"""
        response = client.post("/login", json={
            "username": "user",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid username or password"
    
    def test_login_nonexistent_user(self, client):
        """Test logowania nieistniejącego użytkownika"""
        response = client.post("/login", json={
            "username": "nonexistent",
            "password": "password"
        })
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid username or password"
    
    def test_login_admin_success(self, client, admin_user):
        """Test poprawnego logowania admina"""
        response = client.post("/login", json={
            "username": "admin",
            "password": "adminpass"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data


class TestCreateUser:
    """Testy dla endpointu POST /users"""
    
    def test_create_user_as_admin(self, client, admin_headers):
        """Test tworzenia użytkownika przez admina"""
        response = client.post("/users", json={
            "username": "newuser",
            "password": "newpass",
            "roles": ["ROLE_USER"]
        }, headers=admin_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert "ROLE_USER" in data["roles"]
    
    def test_create_user_as_regular_user(self, client, auth_headers):
        """Test tworzenia użytkownika przez zwykłego użytkownika - powinno być zabronione"""
        response = client.post("/users", json={
            "username": "newuser",
            "password": "newpass"
        }, headers=auth_headers)
        assert response.status_code == 403
        assert response.json()["detail"] == "Admin access required"
    
    def test_create_user_without_token(self, client):
        """Test tworzenia użytkownika bez tokena"""
        response = client.post("/users", json={
            "username": "newuser",
            "password": "newpass"
        })
        assert response.status_code == 403
    
    def test_create_duplicate_user(self, client, admin_headers, regular_user):
        """Test tworzenia użytkownika o istniejącej nazwie"""
        response = client.post("/users", json={
            "username": "user",
            "password": "newpass"
        }, headers=admin_headers)
        assert response.status_code == 400
        assert response.json()["detail"] == "Username already exists"


class TestUserDetails:
    """Testy dla endpointu /user_details"""
    
    def test_get_user_details_success(self, client, auth_headers):
        """Test pobierania szczegółów użytkownika z poprawnym tokenem"""
        response = client.get("/user_details", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "user"
        assert "ROLE_USER" in data["roles"]
    
    def test_get_user_details_admin(self, client, admin_headers):
        """Test pobierania szczegółów admina"""
        response = client.get("/user_details", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert "ROLE_ADMIN" in data["roles"]
    
    def test_get_user_details_without_token(self, client):
        """Test pobierania szczegółów bez tokena"""
        response = client.get("/user_details")
        assert response.status_code == 403
    
    def test_get_user_details_invalid_token(self, client):
        """Test z nieprawidłowym tokenem"""
        response = client.get("/user_details", headers={
            "Authorization": "Bearer invalid_token"
        })
        assert response.status_code == 401


class TestProtectedEndpoints:
    """Testy sprawdzające czy endpointy są zabezpieczone"""
    
    def test_movies_requires_auth(self, client):
        """Test że /movies wymaga autoryzacji"""
        response = client.get("/movies")
        assert response.status_code == 403
    
    def test_movies_with_auth(self, client, auth_headers):
        """Test że /movies działa z autoryzacją"""
        response = client.get("/movies", headers=auth_headers)
        assert response.status_code == 200
    
    def test_links_requires_auth(self, client):
        """Test że /links wymaga autoryzacji"""
        response = client.get("/links")
        assert response.status_code == 403
    
    def test_ratings_requires_auth(self, client):
        """Test że /ratings wymaga autoryzacji"""
        response = client.get("/ratings")
        assert response.status_code == 403
    
    def test_tags_requires_auth(self, client):
        """Test że /tags wymaga autoryzacji"""
        response = client.get("/tags")
        assert response.status_code == 403
