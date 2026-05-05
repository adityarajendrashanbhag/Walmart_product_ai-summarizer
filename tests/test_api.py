from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.routes.health import router as health_router
from backend.api.routes.products import router as products_router


def create_test_client() -> TestClient:
    app = FastAPI()
    app.include_router(health_router)
    app.include_router(products_router)
    return TestClient(app)


def test_health_endpoint_returns_ok():
    client = create_test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_extract_id_endpoint_returns_product_id():
    client = create_test_client()
    payload = {
        "url": (
            "https://www.walmart.com/ip/"
            "Apple-AirPods-Pro-2-Wireless-Earbuds/5689919121"
        )
    }

    response = client.post("/extract_id", json=payload)

    assert response.status_code == 200
    assert response.json() == {"product_id": "5689919121"}


def test_extract_id_endpoint_returns_400_for_invalid_url():
    client = create_test_client()

    response = client.post("/extract_id", json={"url": "https://www.example.com"})

    assert response.status_code == 400
    assert response.json() == {"detail": "Could not extract product ID"}
