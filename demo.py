#!/usr/bin/env python3
"""Demo script to showcase RetailAssist functionality."""

import asyncio
import json
from retail_assist.data.loaders import load_sample_retail_data, load_sample_customer_data, get_retail_insights
from retail_assist.api.utils import data_manager
from retail_assist.infra.logging import logger

def demo_data_loading():
    """Demonstrate data loading functionality."""
    print("🔄 Loading sample retail data...")
    
    # Load sample data
    products = load_sample_retail_data()
    customers = load_sample_customer_data()
    
    print(f"✅ Loaded {len(products)} products")
    print(f"✅ Loaded {len(customers)} customers")
    
    # Show sample products
    print("\n📦 Sample Products:")
    for i, product in products.head(3).iterrows():
        print(f"  • {product['product_name']} - R$ {product['price']:.2f} ({product['category']})")
    
    # Show sample customers
    print("\n👥 Sample Customers:")
    for i, customer in customers.head(3).iterrows():
        print(f"  • {customer['name']} - {customer['city']}, {customer['age']} years old")
    
    return products, customers

def demo_api_functionality():
    """Demonstrate API functionality."""
    print("\n🔄 Testing API functionality...")
    
    # Test product filtering
    products_data = data_manager.get_products(category="Electronics", limit=3)
    print(f"✅ Found {products_data['total_count']} Electronics products")
    
    # Test customer filtering
    customers_data = data_manager.get_customers(city="São Paulo", limit=3)
    print(f"✅ Found {customers_data['total_count']} customers in São Paulo")
    
    # Test sales analytics
    sales_data = data_manager.get_sales_analytics()
    analytics = sales_data["analytics"]
    print(f"✅ Sales Analytics: R$ {analytics['total_revenue']:,.2f} revenue from {analytics['total_sales']} sales")
    
    # Test insights
    insights_data = data_manager.get_insights()
    print(f"✅ Generated {len(insights_data['recommendations'])} business recommendations")
    
    return insights_data

def demo_chat_responses():
    """Demonstrate chat response functionality."""
    print("\n🔄 Testing chat responses...")
    
    from retail_assist.api.app import process_natural_language_query
    
    # Test queries
    test_queries = [
        "Show me products in Electronics category",
        "Who are the customers in São Paulo?",
        "How are sales performing?",
        "Give me business insights"
    ]
    
    for query in test_queries:
        try:
            # This would normally be async, but for demo we'll simulate
            print(f"❓ Query: {query}")
            print(f"💬 Response: [Simulated response for '{query}']")
        except Exception as e:
            print(f"❌ Error processing query: {e}")

def demo_business_insights():
    """Show business insights from the data."""
    print("\n🔄 Generating business insights...")
    
    insights_data = data_manager.get_insights()
    insights = insights_data["insights"]
    recommendations = insights_data["recommendations"]
    
    print("\n📊 Business Overview:")
    print(f"  • Products: {insights['products']['total_products']} total")
    print(f"  • Customers: {insights['customers']['total_customers']} total")
    print(f"  • Revenue: R$ {insights['sales']['total_revenue']:,.2f}")
    print(f"  • Average Rating: {insights['products']['avg_rating']:.1f}/5")
    print(f"  • Low Stock Items: {insights['products']['low_stock_products']}")
    
    print("\n🎯 Top Recommendations:")
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"  {i}. {rec}")

def demo_telegram_bot_features():
    """Show Telegram bot features."""
    print("\n🔄 Telegram Bot Features:")
    print("🤖 The RetailAssist bot provides:")
    print("  • Interactive commands (/start, /products, /customers, /sales, /insights)")
    print("  • Natural language queries")
    print("  • Inline keyboard navigation")
    print("  • LLM integration (if OpenAI API key is provided)")
    print("  • Context-aware conversations")
    print("  • Business insights and recommendations")
    
    print("\n📱 To use the bot:")
    print("  1. Set TELEGRAM_BOT_TOKEN in your .env file")
    print("  2. Run: python run_bot.py")
    print("  3. Find your bot on Telegram and send /start")

def main():
    """Run the complete demo."""
    print("🛍️ RetailAssist Demo")
    print("=" * 50)
    
    try:
        # Demo data loading
        products, customers = demo_data_loading()
        
        # Demo API functionality
        insights_data = demo_api_functionality()
        
        # Demo chat responses
        demo_chat_responses()
        
        # Demo business insights
        demo_business_insights()
        
        # Demo Telegram bot features
        demo_telegram_bot_features()
        
        print("\n✅ Demo completed successfully!")
        print("\n🚀 Next steps:")
        print("  1. Configure your .env file with tokens")
        print("  2. Run the API: python run_api.py")
        print("  3. Run the bot: python run_bot.py")
        print("  4. Test the API at http://localhost:8000/docs")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    main()
