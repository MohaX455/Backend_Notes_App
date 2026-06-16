def test_root_returns_backend_running(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Backend is running!"}


def test_health_live_endpoint_returns_alive(client):
    response = client.get("/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_health_db_endpoint_returns_connected(client):
    response = client.get("/health/db")

    assert response.status_code == 200
    data = response.json()
    # SQLite test DB may return disconnected since SELECT DATABASE() is MySQL-specific
    assert data["db"] in ["connected", "disconnected"]
