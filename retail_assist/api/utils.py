"""Utility functions for the API."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from loguru import logger

from ..data.loaders import get_retail_insights, load_sample_retail_data, load_sample_customer_data, load_sample_sales_data
from ..data.preprocessing import preprocess_retail_data, preprocess_customer_data


class RetailDataManager:
    """Manager for retail data operations."""
    
    def __init__(self):
        """Initialize the data manager."""
        self._products_df: Optional[pd.DataFrame] = None
        self._customers_df: Optional[pd.DataFrame] = None
        self._sales_df: Optional[pd.DataFrame] = None
        self._last_loaded: Optional[datetime] = None
    
    def _ensure_data_loaded(self) -> None:
        """Ensure data is loaded and fresh."""
        if (
            self._products_df is None or 
            self._customers_df is None or 
            self._sales_df is None or
            self._last_loaded is None
        ):
            self._load_data()
    
    def _load_data(self) -> None:
        """Load all retail data."""
        logger.info("Loading retail data")
        
        self._products_df = preprocess_retail_data(load_sample_retail_data())
        self._customers_df = preprocess_customer_data(load_sample_customer_data())
        self._sales_df = load_sample_sales_data()
        self._last_loaded = datetime.now()
        
        logger.info("Retail data loaded successfully")
    
    def get_products(
        self,
        product_name: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        in_stock_only: bool = True,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get products with optional filtering.
        
        Args:
            product_name: Filter by product name (partial match)
            category: Filter by category
            min_price: Minimum price filter
            max_price: Maximum price filter
            min_rating: Minimum rating filter
            in_stock_only: Only show products in stock
            limit: Maximum number of results
            
        Returns:
            Dictionary with products and metadata
        """
        self._ensure_data_loaded()
        df = self._products_df.copy()
        
        # Apply filters
        filters_applied = {}
        
        if product_name:
            df = df[df["product_name"].str.contains(product_name, case=False, na=False)]
            filters_applied["product_name"] = product_name
        
        if category:
            df = df[df["category"] == category]
            filters_applied["category"] = category
        
        if min_price is not None:
            df = df[df["price"] >= min_price]
            filters_applied["min_price"] = min_price
        
        if max_price is not None:
            df = df[df["price"] <= max_price]
            filters_applied["max_price"] = max_price
        
        if min_rating is not None:
            df = df[df["rating"] >= min_rating]
            filters_applied["min_rating"] = min_rating
        
        if in_stock_only:
            df = df[df["stock_quantity"] > 0]
            filters_applied["in_stock_only"] = in_stock_only
        
        # Limit results
        df = df.head(limit)
        
        return {
            "products": df.to_dict("records"),
            "total_count": len(df),
            "filters_applied": filters_applied
        }
    
    def get_customers(
        self,
        customer_id: Optional[str] = None,
        city: Optional[str] = None,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        customer_value: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get customers with optional filtering.
        
        Args:
            customer_id: Specific customer ID
            city: Filter by city
            min_age: Minimum age filter
            max_age: Maximum age filter
            customer_value: Filter by customer value category
            limit: Maximum number of results
            
        Returns:
            Dictionary with customers and metadata
        """
        self._ensure_data_loaded()
        df = self._customers_df.copy()
        
        # Apply filters
        filters_applied = {}
        
        if customer_id:
            df = df[df["customer_id"] == customer_id]
            filters_applied["customer_id"] = customer_id
        
        if city:
            df = df[df["city"] == city]
            filters_applied["city"] = city
        
        if min_age is not None:
            df = df[df["age"] >= min_age]
            filters_applied["min_age"] = min_age
        
        if max_age is not None:
            df = df[df["age"] <= max_age]
            filters_applied["max_age"] = max_age
        
        if customer_value:
            df = df[df["customer_value"] == customer_value]
            filters_applied["customer_value"] = customer_value
        
        # Limit results
        df = df.head(limit)
        
        return {
            "customers": df.to_dict("records"),
            "total_count": len(df),
            "filters_applied": filters_applied
        }
    
    def get_sales_analytics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category: Optional[str] = None,
        payment_method: Optional[str] = None,
        group_by: str = "month"
    ) -> Dict[str, Any]:
        """
        Get sales analytics with optional filtering.
        
        Args:
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)
            category: Filter by product category
            payment_method: Filter by payment method
            group_by: Group results by period (day, week, month, year)
            
        Returns:
            Dictionary with analytics and metadata
        """
        self._ensure_data_loaded()
        df = self._sales_df.copy()
        
        # Apply filters
        filters_applied = {}
        
        if start_date:
            df = df[df["sale_date"] >= start_date]
            filters_applied["start_date"] = start_date
        
        if end_date:
            df = df[df["sale_date"] <= end_date]
            filters_applied["end_date"] = end_date
        
        if payment_method:
            df = df[df["payment_method"] == payment_method]
            filters_applied["payment_method"] = payment_method
        
        # Group by period
        if group_by == "day":
            df["period"] = df["sale_date"].dt.date
        elif group_by == "week":
            df["period"] = df["sale_date"].dt.to_period("W")
        elif group_by == "month":
            df["period"] = df["sale_date"].dt.to_period("M")
        elif group_by == "year":
            df["period"] = df["sale_date"].dt.to_period("Y")
        
        # Calculate analytics
        analytics = {
            "total_sales": len(df),
            "total_revenue": df["total_amount"].sum().round(2),
            "avg_order_value": df["total_amount"].mean().round(2),
            "sales_by_period": df.groupby("period")["total_amount"].sum().round(2).to_dict(),
            "top_payment_methods": df["payment_method"].value_counts().head(5).to_dict(),
        }
        
        return {
            "analytics": analytics,
            "period": {"start_date": start_date, "end_date": end_date},
            "filters_applied": filters_applied
        }
    
    def get_insights(self) -> Dict[str, Any]:
        """
        Get comprehensive retail insights.
        
        Returns:
            Dictionary with insights and recommendations
        """
        self._ensure_data_loaded()
        
        insights = get_retail_insights(
            self._products_df,
            self._customers_df,
            self._sales_df
        )
        
        # Generate recommendations based on insights
        recommendations = self._generate_recommendations(insights)
        
        return {
            "insights": insights,
            "recommendations": recommendations
        }
    
    def _generate_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """Generate business recommendations based on insights."""
        recommendations = []
        
        # Product recommendations
        if insights["products"]["low_stock_products"] > 0:
            recommendations.append(
                f"Consider restocking {insights['products']['low_stock_products']} products with low inventory."
            )
        
        # Customer recommendations
        avg_spent = insights["customers"]["avg_total_spent"]
        if avg_spent < 500:
            recommendations.append(
                "Focus on increasing customer lifetime value through loyalty programs."
            )
        
        # Sales recommendations
        avg_order = insights["sales"]["avg_order_value"]
        if avg_order < 100:
            recommendations.append(
                "Consider implementing upselling strategies to increase average order value."
            )
        
        # Category recommendations
        top_category = max(insights["products"]["categories"], key=insights["products"]["categories"].get)
        recommendations.append(
            f"Focus marketing efforts on {top_category} category as it has the most products."
        )
        
        return recommendations


def generate_conversation_id() -> str:
    """Generate a unique conversation ID."""
    return str(uuid.uuid4())


def format_response_for_chat(data: Dict[str, Any], query: str) -> str:
    """
    Format data response for chat interface.
    
    Args:
        data: Data to format
        query: Original query
        
    Returns:
        Formatted response string
    """
    if "products" in data:
        products = data["products"]
        if products:
            response = f"Found {len(products)} products:\n\n"
            for i, product in enumerate(products[:5], 1):
                response += f"{i}. {product['product_name']} - R$ {product['price']:.2f} ({product['category']})\n"
            if len(products) > 5:
                response += f"\n... and {len(products) - 5} more products."
        else:
            response = "No products found matching your criteria."
    
    elif "customers" in data:
        customers = data["customers"]
        if customers:
            response = f"Found {len(customers)} customers:\n\n"
            for i, customer in enumerate(customers[:5], 1):
                response += f"{i}. {customer['name']} - {customer['city']}, Age: {customer['age']}\n"
            if len(customers) > 5:
                response += f"\n... and {len(customers) - 5} more customers."
        else:
            response = "No customers found matching your criteria."
    
    elif "analytics" in data:
        analytics = data["analytics"]
        response = f"Sales Analytics:\n\n"
        response += f"• Total Sales: {analytics['total_sales']:,}\n"
        response += f"• Total Revenue: R$ {analytics['total_revenue']:,.2f}\n"
        response += f"• Average Order Value: R$ {analytics['avg_order_value']:.2f}\n"
    
    elif "insights" in data:
        insights = data["insights"]
        response = "Retail Insights:\n\n"
        response += f"• Total Products: {insights['products']['total_products']}\n"
        response += f"• Total Customers: {insights['customers']['total_customers']}\n"
        response += f"• Total Revenue: R$ {insights['sales']['total_revenue']:,.2f}\n"
        
        if "recommendations" in data:
            response += "\n\nRecommendations:\n"
            for i, rec in enumerate(data["recommendations"][:3], 1):
                response += f"{i}. {rec}\n"
    
    else:
        response = "I found some information, but I'm not sure how to present it. Could you be more specific?"
    
    return response


# Global data manager instance
data_manager = RetailDataManager()
