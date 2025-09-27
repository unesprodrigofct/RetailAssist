"""Simple data loading functions for the assistant."""

from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np
from loguru import logger

from ..infra.settings import settings


def load_sample_retail_data() -> pd.DataFrame:
    """
    Load sample retail data for demonstration.
    
    Returns:
        Sample retail DataFrame
    """
    logger.info("Loading sample retail data")
    
    np.random.seed(settings.DEFAULT_RANDOM_STATE)
    n_samples = 1000
    
    # Generate sample retail data
    data = {
        "product_id": [f"PROD_{i:04d}" for i in range(n_samples)],
        "product_name": [f"Product {i}" for i in range(n_samples)],
        "category": np.random.choice(
            ["Eletrônicos", "Moda", "Casa e Decoração", "Beleza", "Esportes"], 
            n_samples
        ),
        "price": np.random.uniform(10, 500, n_samples).round(2),
        "stock_quantity": np.random.randint(0, 100, n_samples),
        "rating": np.random.uniform(1, 5, n_samples).round(1),
        "sales_last_month": np.random.randint(0, 50, n_samples),
    }
    
    df = pd.DataFrame(data)
    logger.info(f"Loaded {len(df)} retail products")
    
    return df


def load_sample_customer_data() -> pd.DataFrame:
    """
    Load sample customer data for demonstration.
    
    Returns:
        Sample customer DataFrame
    """
    logger.info("Loading sample customer data")
    
    np.random.seed(settings.DEFAULT_RANDOM_STATE)
    n_customers = 500
    
    # Generate sample customer data
    data = {
        "customer_id": [f"CUST_{i:04d}" for i in range(n_customers)],
        "name": [f"Customer {i}" for i in range(n_customers)],
        "age": np.random.randint(18, 80, n_customers),
        "gender": np.random.choice(["M", "F", "Other"], n_customers),
        "city": np.random.choice(
            ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Salvador", "Brasília"], 
            n_customers
        ),
        "total_purchases": np.random.randint(0, 20, n_customers),
        "total_spent": np.random.uniform(0, 2000, n_customers).round(2),
        "preferred_category": np.random.choice(
            ["Eletrônicos", "Moda", "Casa e Decoração", "Beleza", "Esportes"], 
            n_customers
        ),
    }
    
    df = pd.DataFrame(data)
    logger.info(f"Loaded {len(df)} customers")
    
    return df


def load_sample_sales_data() -> pd.DataFrame:
    """
    Load sample sales data for demonstration.
    
    Returns:
        Sample sales DataFrame
    """
    logger.info("Loading sample sales data")
    
    np.random.seed(settings.DEFAULT_RANDOM_STATE)
    n_sales = 2000
    
    # Generate sample sales data
    data = {
        "sale_id": [f"SALE_{i:06d}" for i in range(n_sales)],
        "customer_id": [f"CUST_{np.random.randint(0, 500):04d}" for _ in range(n_sales)],
        "product_id": [f"PROD_{np.random.randint(0, 1000):04d}" for _ in range(n_sales)],
        "quantity": np.random.randint(1, 5, n_sales),
        "unit_price": np.random.uniform(10, 500, n_sales).round(2),
        "total_amount": 0,  # Will be calculated
        "sale_date": pd.date_range(
            start="2024-01-01", 
            end="2024-12-31", 
            periods=n_sales
        ),
        "payment_method": np.random.choice(
            ["PIX", "Cartão de Crédito", "Cartão de Débito", "Dinheiro", "Boleto"], 
            n_sales,
            p=[0.35, 0.30, 0.20, 0.10, 0.05]  # Probabilidades baseadas no mercado brasileiro
        ),
    }
    
    df = pd.DataFrame(data)
    df["total_amount"] = (df["quantity"] * df["unit_price"]).round(2)
    
    logger.info(f"Loaded {len(df)} sales records")
    
    return df


def get_retail_insights(
    products_df: Optional[pd.DataFrame] = None,
    customers_df: Optional[pd.DataFrame] = None,
    sales_df: Optional[pd.DataFrame] = None
) -> Dict[str, any]:
    """
    Generate retail insights from the data.
    
    Args:
        products_df: Products DataFrame
        customers_df: Customers DataFrame  
        sales_df: Sales DataFrame
        
    Returns:
        Dictionary with retail insights
    """
    logger.info("Generating retail insights")
    
    # Load data if not provided
    if products_df is None:
        products_df = load_sample_retail_data()
    if customers_df is None:
        customers_df = load_sample_customer_data()
    if sales_df is None:
        sales_df = load_sample_sales_data()
    
    insights = {
        "products": {
            "total_products": len(products_df),
            "categories": products_df["category"].value_counts().to_dict(),
            "avg_price": products_df["price"].mean().round(2),
            "avg_rating": products_df["rating"].mean().round(2),
            "low_stock_products": len(products_df[products_df["stock_quantity"] < 10]),
        },
        "customers": {
            "total_customers": len(customers_df),
            "avg_age": customers_df["age"].mean().round(1),
            "gender_distribution": customers_df["gender"].value_counts().to_dict(),
            "city_distribution": customers_df["city"].value_counts().to_dict(),
            "avg_total_spent": customers_df["total_spent"].mean().round(2),
        },
        "sales": {
            "total_sales": len(sales_df),
            "total_revenue": sales_df["total_amount"].sum().round(2),
            "avg_order_value": sales_df["total_amount"].mean().round(2),
            "payment_methods": sales_df["payment_method"].value_counts().to_dict(),
            "sales_by_month": sales_df.groupby(
                sales_df["sale_date"].dt.month
            )["total_amount"].sum().round(2).to_dict(),
        }
    }
    
    logger.info("Retail insights generated successfully")
    return insights


if __name__ == "__main__":
    # Demo usage
    products = load_sample_retail_data()
    customers = load_sample_customer_data()
    sales = load_sample_sales_data()
    
    insights = get_retail_insights(products, customers, sales)
    
    print("Retail Data Loaded:")
    print(f"Products: {len(products)}")
    print(f"Customers: {len(customers)}")
    print(f"Sales: {len(sales)}")
    print(f"\nInsights: {insights['products']['total_products']} products, {insights['sales']['total_revenue']} revenue")
