# RetailAssist 🛍️

**An intelligent assistant for Brazilian retail with AI integration and Telegram Bot**

RetailAssist is a comprehensive retail assistance platform that combines data analysis, business insights, and an intelligent Telegram bot to help retail companies make data-driven decisions.

## ✨ Key Features

- 🤖 **Intelligent Telegram Bot**: Conversational assistant with LLM integration
- 📊 **FastAPI REST API**: RESTful endpoints for retail data analysis
- 📈 **Data Analysis**: Insights on products, customers, and sales
- 🔍 **Natural Language Queries**: Ask questions about your business
- 📦 **Product Management**: Inventory and category analysis
- 👥 **Customer Analysis**: Consumer segmentation and profiles
- 💰 **Sales Reports**: Performance metrics and trends
- 🎯 **Recommendations**: Data-driven suggestions to improve business

## 🏗️ Project Architecture

```
retail_assist/
├── api/                    # FastAPI application
│   ├── app.py             # Main application
│   ├── models.py          # Pydantic models
│   └── utils.py           # API utilities
├── core/                  # ML core (simplified for assistant)
│   ├── pipelines/         # Processing pipelines
│   ├── trainers/          # Model trainers
│   └── base.py           # Base classes
├── data/                  # Data module
│   ├── loaders.py        # Data loading
│   └── preprocessing.py   # Data preprocessing
├── infra/                 # Infrastructure
│   ├── settings.py       # Configuration
│   └── logging.py        # Logging system
├── bot/                   # Telegram bot
│   └── telegram_bot.py   # Main bot with LLM
└── tests/                 # Automated tests
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.9+
- Poetry (recommended) or pip

### 1. Clone the repository

```bash
git clone https://github.com/unesprodrigofct/RetailAssist.git
cd RetailAssist
```

### 2. Install dependencies

```bash
# With Poetry (recommended)
poetry install

# Or with pip
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# OpenAI (optional, for LLM)
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=500

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
```

### 4. How to get Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the instructions
3. Copy the provided token to your `.env` file

## 🎯 How to Use

### 1. Run the API

```bash
poetry run python run_api.py
# Access: http://localhost:8000/docs
```

### 2. Run the Telegram Bot

```bash
poetry run python run_bot.py
```

### 3. Bot Commands

- `/start` - Start the bot and see presentation
- `/products` - Product and inventory analysis
- `/customers` - Customer profile and segmentation
- `/sales` - Sales performance and metrics
- `/insights` - Strategic insights and recommendations
- `/help` - Complete help

### 4. Example Questions (in Portuguese)

- "Como preparar para a Black Friday?" (How to prepare for Black Friday?)
- "Quais produtos vendem mais no Nordeste?" (Which products sell most in Northeast?)
- "Estratégias para conquistar a classe C" (Strategies to win class C customers)
- "Como aumentar meu ticket médio?" (How to increase my average ticket?)
- "Análise de clientes VIP por região" (VIP customer analysis by region)


## 🇧🇷 Brazilian Market Context

RetailAssist was developed specifically for the Brazilian market, including:

### Payment Methods

- **PIX** (35% of transactions)
- **Credit Card** (30%)
- **Debit Card** (20%)
- **Cash** (10%)
- **Bank Slip** (5%)

### Seasonality

- Black Friday (November)
- Mother's Day (May)
- Father's Day (August)
- Christmas (December)
- Children's Day (October)

### Regional Segmentation

- **Southeast**: Higher purchasing power
- **Northeast**: 15% annual growth
- **South**: Higher average ticket
- **North/Central-West**: Expanding market

### Social Classes

- **Classes C and D**: 70% of Brazilian market
- **Mobile Commerce**: 65% of e-commerce
- **National Average Ticket**: R$ 85-120

## 📊 Sample Data

The system includes realistic synthetic data:

- **Products**: Prices in Brazilian Real, Brazilian categories, ratings
- **Customers**: Brazilian cities, regional consumption profiles
- **Sales**: Brazilian payment methods, seasonality patterns

## 🧪 Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=retail_assist

# Run specific tests
poetry run pytest tests/test_api.py
```

## 📚 API Documentation

After running the API, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

- `GET /products` - List products with filters
- `GET /customers` - List customers with filters
- `GET /sales/analytics` - Sales analytics
- `GET /insights` - Insights and recommendations
- `POST /chat` - Chat with natural language processing

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## 🛠️ Technologies Used

- **Backend**: FastAPI, Uvicorn
- **Bot**: python-telegram-bot
- **AI**: OpenAI GPT-3.5/4
- **Data**: Pandas, NumPy
- **ML**: Scikit-learn, XGBoost
- **Testing**: pytest, coverage
- **Quality**: Ruff, Black, MyPy
- **Config**: Pydantic Settings, python-dotenv
- **Logging**: Loguru

## 📞 Support

For questions or support:

- 📧 Email: unesprodrigofct@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/unesprodrigofct/RetailAssist/issues)

---

**RetailAssist** - Transforming data into strategic decisions for Brazilian retail! 🇧🇷🚀
