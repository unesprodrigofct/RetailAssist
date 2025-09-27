# 🛍️ RetailAssist

**Um assistente inteligente para varejo com integração de IA e Telegram Bot**

RetailAssist é uma plataforma completa de assistência ao varejo que combina análise de dados, insights de negócio e um bot do Telegram inteligente para ajudar empresas de varejo a tomar decisões baseadas em dados.

## ✨ Características Principais

- 🤖 **Bot do Telegram Inteligente**: Assistente conversacional com integração LLM
- 📊 **API FastAPI**: Endpoints RESTful para análise de dados de varejo
- 📈 **Análise de Dados**: Insights sobre produtos, clientes e vendas
- 🔍 **Consultas em Linguagem Natural**: Faça perguntas sobre seu negócio
- 📦 **Gestão de Produtos**: Análise de estoque e categorias
- 👥 **Análise de Clientes**: Segmentação e perfis de consumidores
- 💰 **Relatórios de Vendas**: Métricas e tendências de performance
- 🎯 **Recomendações**: Sugestões baseadas em dados para melhorar o negócio

## 🏗️ Arquitetura do Projeto

```
retail_assist/
├── api/                    # FastAPI application
│   ├── app.py             # Aplicação principal
│   ├── models.py          # Modelos Pydantic
│   └── utils.py           # Utilitários da API
├── core/                  # Núcleo ML (simplificado para assistente)
│   ├── pipelines/         # Pipelines de processamento
│   ├── trainers/          # Treinadores de modelos
│   └── base.py           # Classes base
├── data/                  # Módulo de dados
│   ├── loaders.py        # Carregamento de dados
│   └── preprocessing.py   # Pré-processamento
├── infra/                 # Infraestrutura
│   ├── settings.py       # Configurações
│   └── logging.py        # Sistema de logs
├── bot/                   # Bot do Telegram
│   └── telegram_bot.py   # Bot principal com LLM
└── tests/                 # Testes automatizados
```

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.9+
- Poetry (recomendado) ou pip

### 1. Clone o repositório

```bash
git clone <repository-url>
cd RetailAssist
```

### 2. Instale as dependências

```bash
# Com Poetry (recomendado)
poetry install

# Ou com pip
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=seu_token_do_bot_telegram

# OpenAI (opcional, para LLM)
OPENAI_API_KEY=sua_chave_openai
OPENAI_MODEL=gpt-3.5-turbo

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
```

### 4. Como obter o Token do Telegram

1. Abra o Telegram e procure por `@BotFather`
2. Envie `/newbot` e siga as instruções
3. Copie o token fornecido para o arquivo `.env`

## 🎯 Como Usar

### 1. Executar a API

```bash
# Com Poetry
poetry run python -m retail_assist.api.app

# Ou diretamente
python -m retail_assist.api.app
```

A API estará disponível em `http://localhost:8000`

- **Documentação**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 2. Executar o Bot do Telegram

```bash
# Com Poetry
poetry run python -m retail_assist.bot.telegram_bot

# Ou diretamente
python -m retail_assist.bot.telegram_bot
```

### 3. Usar o Bot

1. Encontre seu bot no Telegram
2. Envie `/start` para começar
3. Use os comandos ou faça perguntas em linguagem natural:

**Comandos disponíveis:**
- `/start` - Iniciar o bot
- `/products` - Ver produtos
- `/customers` - Ver clientes  
- `/sales` - Análise de vendas
- `/insights` - Insights de negócio
- `/help` - Ajuda

**Exemplos de perguntas:**
- "Quais são os produtos mais vendidos?"
- "Mostre clientes de São Paulo"
- "Como estão as vendas este mês?"
- "Que produtos estão com estoque baixo?"

## 📡 Endpoints da API

### Produtos
- `POST /products` - Listar produtos com filtros
- `POST /customers` - Listar clientes com filtros
- `POST /analytics/sales` - Análise de vendas
- `GET /insights` - Insights de negócio

### Chat
- `POST /chat` - Interação com assistente
- `POST /query` - Consultas em linguagem natural

### Exemplos de Uso da API

```python
import requests

# Buscar produtos eletrônicos
response = requests.post("http://localhost:8000/products", json={
    "category": "Electronics",
    "min_price": 100,
    "in_stock_only": True
})

# Chat com o assistente
response = requests.post("http://localhost:8000/chat", json={
    "message": "Mostre os produtos mais vendidos",
    "user_id": "user123"
})
```

## 🧪 Executar Testes

```bash
# Com Poetry
poetry run pytest

# Com coverage
poetry run pytest --cov=retail_assist

# Testes específicos
poetry run pytest tests/test_api.py
```

## 🔧 Desenvolvimento

### Estrutura de Código

- **API**: FastAPI com Pydantic para validação
- **Bot**: python-telegram-bot com integração OpenAI
- **Dados**: Pandas para manipulação de dados
- **Testes**: pytest com cobertura
- **Qualidade**: Ruff para linting, Black para formatação

### Comandos de Desenvolvimento

```bash
# Formatação de código
poetry run black retail_assist/

# Linting
poetry run ruff retail_assist/

# Type checking
poetry run mypy retail_assist/
```

## 🌟 Funcionalidades do Bot

### Comandos Interativos
- Interface com botões inline
- Navegação intuitiva
- Respostas contextuais

### Integração LLM
- Suporte a OpenAI GPT-3.5/4
- Respostas em linguagem natural
- Contexto de conversa mantido

### Análises Disponíveis
- **Produtos**: Estoque, categorias, preços
- **Clientes**: Segmentação, localização, valor
- **Vendas**: Receita, métodos de pagamento, tendências
- **Insights**: Recomendações automáticas

## 📊 Dados de Exemplo

O projeto inclui dados sintéticos para demonstração:
- 1.000 produtos em 5 categorias
- 500 clientes em 5 cidades
- 2.000 transações de vendas
- Métricas e insights calculados automaticamente

## 🚀 Deploy

### Local
```bash
# API
uvicorn retail_assist.api.app:app --host 0.0.0.0 --port 8000

# Bot
python -m retail_assist.bot.telegram_bot
```

### Docker (futuro)
```bash
docker build -t retail-assist .
docker run -p 8000:8000 retail-assist
```

### Cloud (Heroku, Railway, etc.)
- Configure as variáveis de ambiente
- Use webhook para o bot do Telegram
- Configure `TELEGRAM_WEBHOOK_URL`

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- 📧 Email: seu.email@exemplo.com
- 💬 Telegram: @seu_usuario
- 🐛 Issues: [GitHub Issues](https://github.com/seu-usuario/RetailAssist/issues)

## 🎉 Agradecimentos

- FastAPI pela excelente framework
- python-telegram-bot pela integração Telegram
- OpenAI pela API de LLM
- Comunidade Python pelo ecossistema incrível

---

**RetailAssist** - Transformando dados de varejo em insights acionáveis! 🚀
