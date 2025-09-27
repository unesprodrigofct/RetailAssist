"""Pydantic models for API requests and responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "0.1.0"


class RetailQueryRequest(BaseModel):
    """Request model for retail queries."""
    query: str = Field(..., description="Natural language query about retail data")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    
    @validator("query")
    def query_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class RetailQueryResponse(BaseModel):
    """Response model for retail queries."""
    query: str
    response: str
    data: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ProductRequest(BaseModel):
    """Request model for product operations."""
    product_name: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = Field(default=None, ge=0)
    max_price: Optional[float] = Field(default=None, ge=0)
    min_rating: Optional[float] = Field(default=None, ge=1, le=5)
    in_stock_only: bool = Field(default=True)
    
    @validator("max_price")
    def max_price_greater_than_min(cls, v, values):
        if v is not None and "min_price" in values and values["min_price"] is not None:
            if v < values["min_price"]:
                raise ValueError("max_price must be greater than min_price")
        return v


class ProductResponse(BaseModel):
    """Response model for product data."""
    products: List[Dict[str, Any]]
    total_count: int
    filters_applied: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


class CustomerRequest(BaseModel):
    """Request model for customer operations."""
    customer_id: Optional[str] = None
    city: Optional[str] = None
    min_age: Optional[int] = Field(default=None, ge=0, le=120)
    max_age: Optional[int] = Field(default=None, ge=0, le=120)
    customer_value: Optional[str] = Field(default=None, regex="^(Low Value|Medium Value|High Value|VIP)$")
    
    @validator("max_age")
    def max_age_greater_than_min(cls, v, values):
        if v is not None and "min_age" in values and values["min_age"] is not None:
            if v < values["min_age"]:
                raise ValueError("max_age must be greater than min_age")
        return v


class CustomerResponse(BaseModel):
    """Response model for customer data."""
    customers: List[Dict[str, Any]]
    total_count: int
    filters_applied: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


class SalesAnalyticsRequest(BaseModel):
    """Request model for sales analytics."""
    start_date: Optional[str] = Field(default=None, description="Start date in YYYY-MM-DD format")
    end_date: Optional[str] = Field(default=None, description="End date in YYYY-MM-DD format")
    category: Optional[str] = None
    payment_method: Optional[str] = None
    group_by: Optional[str] = Field(default="month", regex="^(day|week|month|year)$")
    
    @validator("start_date", "end_date")
    def validate_date_format(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class SalesAnalyticsResponse(BaseModel):
    """Response model for sales analytics."""
    analytics: Dict[str, Any]
    period: Dict[str, Optional[str]]
    filters_applied: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


class InsightsResponse(BaseModel):
    """Response model for retail insights."""
    insights: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Request model for chat interactions."""
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID for context")
    user_id: Optional[str] = Field(default=None, description="User ID")
    
    @validator("message")
    def message_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


class ChatResponse(BaseModel):
    """Response model for chat interactions."""
    message: str
    response: str
    conversation_id: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# Example data for API documentation
class Examples:
    """Example data for API documentation."""
    
    RETAIL_QUERY_REQUEST = {
        "query": "Show me the top 5 best-selling products in Electronics category",
        "context": {"user_role": "manager"}
    }
    
    PRODUCT_REQUEST = {
        "category": "Electronics",
        "min_price": 100,
        "max_price": 500,
        "min_rating": 4.0,
        "in_stock_only": True
    }
    
    CUSTOMER_REQUEST = {
        "city": "São Paulo",
        "min_age": 25,
        "max_age": 45,
        "customer_value": "High Value"
    }
    
    SALES_ANALYTICS_REQUEST = {
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "category": "Electronics",
        "group_by": "month"
    }
    
    CHAT_REQUEST = {
        "message": "What are the best products for customers in São Paulo?",
        "user_id": "user123"
    }
