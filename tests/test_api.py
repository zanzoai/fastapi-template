"""API smoke tests."""
import pytest
from httpx import ASGITransport, AsyncClient

# Import after conftest sets env
from main import app


@pytest.fixture
def client():
    """Create test client."""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_root(client):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Zanzo" in data["message"] or "Welcome" in data["message"]


@pytest.mark.asyncio
async def test_health(client):
    """Test health endpoint."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"
