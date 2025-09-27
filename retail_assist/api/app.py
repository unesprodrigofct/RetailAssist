"""FastAPI application for RetailAssist."""

from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .models import (
    HealthResponse,
    RetailQueryRequest,
    RetailQueryResponse,
    ProductRequest,
    ProductResponse,
    CustomerRequest,
    CustomerResponse,
    SalesAnalyticsRequest,
    SalesAnalyticsResponse,
    InsightsResponse,
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    Examples,
)
from .utils import data_manager, generate_conversation_id, format_response_for_chat
from ..infra.settings import settings
from ..infra.logging import logger as app_logger

# Initialize FastAPI app
app = FastAPI(
    title="RetailAssist API",
    description="A comprehensive retail assistance API with ML capabilities",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    app_logger.info("Starting RetailAssist API")
    app_logger.info(f"API will be available at http://{settings.API_HOST}:{settings.API_PORT}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    app_logger.info("Shutting down RetailAssist API")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    app_logger.error(f"Unhandled exception: {exc}")
    return ErrorResponse(
        error="Internal server error",
        detail=str(exc) if settings.LOG_LEVEL == "DEBUG" else None
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse()


# Products endpoints
@app.post("/products", response_model=ProductResponse, tags=["Products"])
async def get_products(request: ProductRequest):
    """
    Get products with optional filtering.
    
    Example request:
    ```json
    {
        "category": "Electronics",
        "min_price": 100,
        "max_price": 500,
        "min_rating": 4.0,
        "in_stock_only": true
    }
    ```
    """
    try:
        app_logger.info(f"Getting products with filters: {request.dict()}")
        
        result = data_manager.get_products(
            product_name=request.product_name,
            category=request.category,
            min_price=request.min_price,
            max_price=request.max_price,
            min_rating=request.min_rating,
            in_stock_only=request.in_stock_only,
        )
        
        return ProductResponse(**result)
    
    except Exception as e:
        app_logger.error(f"Error getting products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Customers endpoints
@app.post("/customers", response_model=CustomerResponse, tags=["Customers"])
async def get_customers(request: CustomerRequest):
    """
    Get customers with optional filtering.
    
    Example request:
    ```json
    {
        "city": "São Paulo",
        "min_age": 25,
        "max_age": 45,
        "customer_value": "High Value"
    }
    ```
    """
    try:
        app_logger.info(f"Getting customers with filters: {request.dict()}")
        
        result = data_manager.get_customers(
            customer_id=request.customer_id,
            city=request.city,
            min_age=request.min_age,
            max_age=request.max_age,
            customer_value=request.customer_value,
        )
        
        return CustomerResponse(**result)
    
    except Exception as e:
        app_logger.error(f"Error getting customers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Sales analytics endpoints
@app.post("/analytics/sales", response_model=SalesAnalyticsResponse, tags=["Analytics"])
async def get_sales_analytics(request: SalesAnalyticsRequest):
    """
    Get sales analytics with optional filtering.
    
    Example request:
    ```json
    {
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "category": "Electronics",
        "group_by": "month"
    }
    ```
    """
    try:
        app_logger.info(f"Getting sales analytics with filters: {request.dict()}")
        
        result = data_manager.get_sales_analytics(
            start_date=request.start_date,
            end_date=request.end_date,
            category=request.category,
            payment_method=request.payment_method,
            group_by=request.group_by,
        )
        
        return SalesAnalyticsResponse(**result)
    
    except Exception as e:
        app_logger.error(f"Error getting sales analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Insights endpoint
@app.get("/insights", response_model=InsightsResponse, tags=["Analytics"])
async def get_insights():
    """
    Get comprehensive retail insights and recommendations.
    """
    try:
        app_logger.info("Getting retail insights")
        
        result = data_manager.get_insights()
        
        return InsightsResponse(**result)
    
    except Exception as e:
        app_logger.error(f"Error getting insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Chat endpoint for natural language queries
@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Process natural language queries about retail data.
    
    Example request:
    ```json
    {
        "message": "Show me the best products for customers in São Paulo",
        "user_id": "user123"
    }
    ```
    """
    try:
        app_logger.info(f"Processing chat message: {request.message}")
        
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or generate_conversation_id()
        
        # Simple query processing (can be enhanced with NLP/LLM)
        response_text, data = await process_natural_language_query(request.message)
        
        return ChatResponse(
            message=request.message,
            response=response_text,
            conversation_id=conversation_id,
            data=data,
        )
    
    except Exception as e:
        app_logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Legacy query endpoint (for backward compatibility)
@app.post("/query", response_model=RetailQueryResponse, tags=["Query"])
async def retail_query(request: RetailQueryRequest):
    """
    Process retail queries (legacy endpoint).
    
    Example request:
    ```json
    {
        "query": "Show me the top 5 best-selling products in Electronics category",
        "context": {"user_role": "manager"}
    }
    ```
    """
    try:
        app_logger.info(f"Processing retail query: {request.query}")
        
        response_text, data = await process_natural_language_query(request.query)
        
        return RetailQueryResponse(
            query=request.query,
            response=response_text,
            data=data,
        )
    
    except Exception as e:
        app_logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_natural_language_query(query: str) -> tuple[str, Dict[str, Any]]:
    """
    Process natural language queries and return appropriate responses.
    
    This is a simplified implementation. In a real application, you would
    integrate with an LLM or NLP service for better query understanding.
    
    Args:
        query: Natural language query
        
    Returns:
        Tuple of (response_text, data)
    """
    query_lower = query.lower()
    
    # Product queries
    if any(word in query_lower for word in ["product", "item", "merchandise"]):
        if "electronics" in query_lower:
            data = data_manager.get_products(category="Electronics")
        elif "clothing" in query_lower:
            data = data_manager.get_products(category="Clothing")
        elif "expensive" in query_lower or "premium" in query_lower:
            data = data_manager.get_products(min_price=200)
        elif "cheap" in query_lower or "budget" in query_lower:
            data = data_manager.get_products(max_price=50)
        else:
            data = data_manager.get_products()
        
        response_text = format_response_for_chat(data, query)
    
    # Customer queries
    elif any(word in query_lower for word in ["customer", "client", "user"]):
        if "são paulo" in query_lower:
            data = data_manager.get_customers(city="São Paulo")
        elif "rio" in query_lower:
            data = data_manager.get_customers(city="Rio de Janeiro")
        elif "vip" in query_lower:
            data = data_manager.get_customers(customer_value="VIP")
        else:
            data = data_manager.get_customers()
        
        response_text = format_response_for_chat(data, query)
    
    # Sales/Analytics queries
    elif any(word in query_lower for word in ["sales", "revenue", "analytics", "performance"]):
        data = data_manager.get_sales_analytics()
        response_text = format_response_for_chat(data, query)
    
    # Insights queries
    elif any(word in query_lower for word in ["insight", "recommendation", "advice", "suggest"]):
        data = data_manager.get_insights()
        response_text = format_response_for_chat(data, query)
    
    # Default response
    else:
        data = data_manager.get_insights()
        response_text = (
            "I'm not sure exactly what you're looking for. Here are some general insights about your retail business:\n\n" +
            format_response_for_chat(data, query)
        )
    
    return response_text, data


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "retail_assist.api.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
