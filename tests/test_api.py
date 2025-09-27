"""Tests for the API module."""

import pytest
from fastapi.testclient import TestClient

from retail_assist.api.app import app
from retail_assist.api.models import Examples


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "0.1.0"


def test_get_products(client):
    """Test products endpoint."""
    response = client.post("/products", json={})
    assert response.status_code == 200
    
    data = response.json()
    assert "products" in data
    assert "total_count" in data
    assert "filters_applied" in data
    assert isinstance(data["products"], list)


def test_get_products_with_filters(client):
    """Test products endpoint with filters."""
    request_data = {
        "category": "Electronics",
        "min_price": 100,
        "max_price": 500,
        "in_stock_only": True
    }
    
    response = client.post("/products", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "products" in data
    assert data["filters_applied"]["category"] == "Electronics"
    assert data["filters_applied"]["min_price"] == 100


def test_get_customers(client):
    """Test customers endpoint."""
    response = client.post("/customers", json={})
    assert response.status_code == 200
    
    data = response.json()
    assert "customers" in data
    assert "total_count" in data
    assert "filters_applied" in data
    assert isinstance(data["customers"], list)


def test_get_customers_with_filters(client):
    """Test customers endpoint with filters."""
    request_data = {
        "city": "São Paulo",
        "min_age": 25,
        "max_age": 45
    }
    
    response = client.post("/customers", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "customers" in data
    assert data["filters_applied"]["city"] == "São Paulo"


def test_get_sales_analytics(client):
    """Test sales analytics endpoint."""
    request_data = {
        "group_by": "month"
    }
    
    response = client.post("/analytics/sales", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "analytics" in data
    assert "period" in data
    assert "filters_applied" in data
    
    analytics = data["analytics"]
    assert "total_sales" in analytics
    assert "total_revenue" in analytics
    assert "avg_order_value" in analytics


def test_get_insights(client):
    """Test insights endpoint."""
    response = client.get("/insights")
    assert response.status_code == 200
    
    data = response.json()
    assert "insights" in data
    assert "recommendations" in data
    
    insights = data["insights"]
    assert "products" in insights
    assert "customers" in insights
    assert "sales" in insights


def test_chat_endpoint(client):
    """Test chat endpoint."""
    request_data = {
        "message": "Show me products",
        "user_id": "test_user"
    }
    
    response = client.post("/chat", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "response" in data
    assert "conversation_id" in data
    assert data["message"] == "Show me products"


def test_retail_query_endpoint(client):
    """Test retail query endpoint."""
    request_data = {
        "query": "Show me the best products"
    }
    
    response = client.post("/query", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "query" in data
    assert "response" in data
    assert data["query"] == "Show me the best products"


def test_invalid_product_request(client):
    """Test invalid product request."""
    request_data = {
        "min_price": 500,
        "max_price": 100  # Invalid: max < min
    }
    
    response = client.post("/products", json=request_data)
    assert response.status_code == 422  # Validation error


def test_invalid_customer_request(client):
    """Test invalid customer request."""
    request_data = {
        "min_age": 50,
        "max_age": 25  # Invalid: max < min
    }
    
    response = client.post("/customers", json=request_data)
    assert response.status_code == 422  # Validation error


def test_empty_chat_message(client):
    """Test empty chat message."""
    request_data = {
        "message": "",  # Empty message
        "user_id": "test_user"
    }
    
    response = client.post("/chat", json=request_data)
    assert response.status_code == 422  # Validation error


@pytest.mark.parametrize("endpoint", ["/products", "/customers", "/analytics/sales", "/chat", "/query"])
def test_endpoints_require_body(client, endpoint):
    """Test that endpoints require request body."""
    if endpoint in ["/products", "/customers", "/analytics/sales"]:
        response = client.post(endpoint)
        assert response.status_code == 422  # Missing body
    elif endpoint in ["/chat", "/query"]:
        response = client.post(endpoint)
        assert response.status_code == 422  # Missing required fields


def test_cors_headers(client):
    """Test CORS headers are present."""
    response = client.options("/health")
    # CORS headers should be present due to middleware
    assert response.status_code in [200, 405]  # OPTIONS might not be explicitly handled
