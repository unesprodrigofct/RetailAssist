"""Simple data preprocessing functions."""

from typing import Dict, List, Optional, Union

import pandas as pd
import numpy as np
from loguru import logger


def clean_text(text: str) -> str:
    """
    Clean and normalize text data.
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    if not isinstance(text, str):
        return ""
    
    # Basic text cleaning
    text = text.strip().lower()
    text = " ".join(text.split())  # Remove extra whitespace
    
    return text


def format_currency(amount: Union[float, int]) -> str:
    """
    Format currency values for display.
    
    Args:
        amount: Currency amount
        
    Returns:
        Formatted currency string
    """
    return f"R$ {amount:,.2f}"


def categorize_price(price: float) -> str:
    """
    Categorize products by price range.
    
    Args:
        price: Product price
        
    Returns:
        Price category
    """
    if price < 50:
        return "Budget"
    elif price < 200:
        return "Mid-range"
    elif price < 500:
        return "Premium"
    else:
        return "Luxury"


def categorize_customer_value(total_spent: float) -> str:
    """
    Categorize customers by total spending.
    
    Args:
        total_spent: Total amount spent by customer
        
    Returns:
        Customer value category
    """
    if total_spent < 100:
        return "Low Value"
    elif total_spent < 500:
        return "Medium Value"
    elif total_spent < 1000:
        return "High Value"
    else:
        return "VIP"


def get_stock_status(quantity: int) -> str:
    """
    Get stock status based on quantity.
    
    Args:
        quantity: Stock quantity
        
    Returns:
        Stock status
    """
    if quantity == 0:
        return "Out of Stock"
    elif quantity < 10:
        return "Low Stock"
    elif quantity < 50:
        return "Medium Stock"
    else:
        return "High Stock"


def preprocess_retail_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess retail data with additional features.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Preprocessed DataFrame
    """
    logger.info("Preprocessing retail data")
    
    df = df.copy()
    
    # Add price category
    if "price" in df.columns:
        df["price_category"] = df["price"].apply(categorize_price)
    
    # Add stock status
    if "stock_quantity" in df.columns:
        df["stock_status"] = df["stock_quantity"].apply(get_stock_status)
    
    # Clean product names
    if "product_name" in df.columns:
        df["product_name_clean"] = df["product_name"].apply(clean_text)
    
    logger.info("Retail data preprocessing completed")
    return df


def preprocess_customer_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess customer data with additional features.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Preprocessed DataFrame
    """
    logger.info("Preprocessing customer data")
    
    df = df.copy()
    
    # Add customer value category
    if "total_spent" in df.columns:
        df["customer_value"] = df["total_spent"].apply(categorize_customer_value)
    
    # Add age group
    if "age" in df.columns:
        df["age_group"] = pd.cut(
            df["age"], 
            bins=[0, 25, 35, 50, 65, 100], 
            labels=["18-25", "26-35", "36-50", "51-65", "65+"]
        )
    
    # Clean names
    if "name" in df.columns:
        df["name_clean"] = df["name"].apply(clean_text)
    
    logger.info("Customer data preprocessing completed")
    return df


def generate_summary_stats(df: pd.DataFrame, numeric_cols: Optional[List[str]] = None) -> Dict:
    """
    Generate summary statistics for a DataFrame.
    
    Args:
        df: Input DataFrame
        numeric_cols: List of numeric columns to analyze
        
    Returns:
        Summary statistics dictionary
    """
    logger.info("Generating summary statistics")
    
    if numeric_cols is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    summary = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "numeric_columns": len(numeric_cols),
        "missing_values": df.isnull().sum().to_dict(),
        "numeric_stats": {}
    }
    
    # Generate stats for numeric columns
    for col in numeric_cols:
        if col in df.columns:
            summary["numeric_stats"][col] = {
                "mean": df[col].mean(),
                "median": df[col].median(),
                "std": df[col].std(),
                "min": df[col].min(),
                "max": df[col].max(),
                "count": df[col].count()
            }
    
    logger.info("Summary statistics generated")
    return summary


if __name__ == "__main__":
    # Demo usage
    from .loaders import load_sample_retail_data, load_sample_customer_data
    
    # Load and preprocess data
    products = load_sample_retail_data()
    customers = load_sample_customer_data()
    
    products_processed = preprocess_retail_data(products)
    customers_processed = preprocess_customer_data(customers)
    
    # Generate summaries
    products_summary = generate_summary_stats(products_processed)
    customers_summary = generate_summary_stats(customers_processed)
    
    print("Data Preprocessing Completed:")
    print(f"Products: {products_summary['total_rows']} rows, {products_summary['total_columns']} columns")
    print(f"Customers: {customers_summary['total_rows']} rows, {customers_summary['total_columns']} columns")
