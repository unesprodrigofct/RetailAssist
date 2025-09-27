"""Telegram bot for RetailAssist with LLM integration."""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

import httpx
from loguru import logger
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available. Using fallback responses.")

from ..infra.settings import settings
from ..api.utils import data_manager


class RetailAssistBot:
    """Telegram bot for retail assistance with LLM integration."""
    
    def __init__(self):
        """Initialize the bot."""
        self.application: Optional[Application] = None
        self.openai_client = None
        self.conversation_history: Dict[int, List[Dict]] = {}
        
        # Initialize OpenAI client if available
        if OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client initialized")
        else:
            logger.warning("OpenAI not available. Using fallback responses.")
    
    def setup_bot(self) -> Application:
        """Setup the Telegram bot application."""
        if not settings.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        
        # Create application
        self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("products", self.products_command))
        self.application.add_handler(CommandHandler("customers", self.customers_command))
        self.application.add_handler(CommandHandler("sales", self.sales_command))
        self.application.add_handler(CommandHandler("insights", self.insights_command))
        self.application.add_handler(CommandHandler("clear", self.clear_command))
        
        # Callback query handler for inline keyboards
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handler for general chat
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        
        logger.info("Bot handlers configured")
        return self.application
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        logger.info(f"User {user.id} ({user.first_name}) started the bot")
        
        welcome_message = f"""
🛍️ **Bem-vindo ao RetailAssist!**

Olá {user.first_name}! Eu sou seu consultor especializado em varejo brasileiro! 🇧🇷

**Como posso ajudar seu negócio:**
• 📦 Análise de produtos e mix ideal
• 👥 Perfil do consumidor brasileiro
• 📊 Performance de vendas e métricas
• 💡 Estratégias para o mercado nacional
• 🎯 Insights sazonais e regionais
• 💰 Otimização de ticket médio e conversão

**Comandos disponíveis:**
/products - Gestão de produtos
/customers - Análise de clientes
/sales - Performance de vendas
/insights - Estratégias de crescimento
/help - Ajuda completa

💬 **Exemplos de perguntas:**
• "Como preparar para a Black Friday?"
• "Estratégias para a classe C"
• "Produtos ideais para o Nordeste"

Fale comigo em linguagem natural! 🚀
        """
        
        # Create inline keyboard
        keyboard = [
            [
                InlineKeyboardButton("📦 Produtos", callback_data="products"),
                InlineKeyboardButton("👥 Clientes", callback_data="customers"),
            ],
            [
                InlineKeyboardButton("📊 Vendas", callback_data="sales"),
                InlineKeyboardButton("💡 Insights", callback_data="insights"),
            ],
            [InlineKeyboardButton("❓ Ajuda", callback_data="help")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = """
🆘 **Ajuda - RetailAssist**

**Comandos disponíveis:**

🔹 `/start` - Iniciar o bot
🔹 `/help` - Mostrar esta ajuda
🔹 `/products` - Listar produtos
🔹 `/customers` - Listar clientes
🔹 `/sales` - Análise de vendas
🔹 `/insights` - Insights de negócio
🔹 `/clear` - Limpar histórico de conversa

**Exemplos de perguntas:**
• "Quais são os produtos mais vendidos?"
• "Mostre clientes de São Paulo"
• "Como estão as vendas este mês?"
• "Que produtos estão com estoque baixo?"
• "Qual categoria vende mais?"

**Dicas:**
• Você pode fazer perguntas em linguagem natural
• Use os botões para navegação rápida
• O bot lembra do contexto da conversa
        """
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def products_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /products command."""
        try:
            # Get products data
            products_data = data_manager.get_products(limit=5)
            
            if products_data["products"]:
                message = "📦 **Produtos em Destaque:**\n\n"
                for i, product in enumerate(products_data["products"], 1):
                    message += f"{i}. **{product['product_name']}**\n"
                    message += f"   💰 R$ {product['price']:.2f}\n"
                    message += f"   📂 {product['category']}\n"
                    message += f"   ⭐ {product['rating']}/5\n"
                    message += f"   📦 Estoque: {product['stock_quantity']}\n\n"
                
                message += f"Total de produtos: {products_data['total_count']}"
            else:
                message = "❌ Nenhum produto encontrado."
            
            # Create keyboard for product actions
            keyboard = [
                [
                    InlineKeyboardButton("🔍 Buscar Produto", callback_data="search_product"),
                    InlineKeyboardButton("📊 Por Categoria", callback_data="products_by_category"),
                ],
                [InlineKeyboardButton("🔙 Menu Principal", callback_data="main_menu")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
        except Exception as e:
            logger.error(f"Error in products command: {e}")
            await update.message.reply_text("❌ Erro ao buscar produtos. Tente novamente.")
    
    async def customers_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /customers command."""
        try:
            # Get customers data
            customers_data = data_manager.get_customers(limit=5)
            
            if customers_data["customers"]:
                message = "👥 **Clientes Recentes:**\n\n"
                for i, customer in enumerate(customers_data["customers"], 1):
                    message += f"{i}. **{customer['name']}**\n"
                    message += f"   📍 {customer['city']}\n"
                    message += f"   🎂 {customer['age']} anos\n"
                    message += f"   💰 Total gasto: R$ {customer['total_spent']:.2f}\n"
                    message += f"   🏷️ {customer.get('customer_value', 'N/A')}\n\n"
                
                message += f"Total de clientes: {customers_data['total_count']}"
            else:
                message = "❌ Nenhum cliente encontrado."
            
            # Create keyboard for customer actions
            keyboard = [
                [
                    InlineKeyboardButton("🏙️ Por Cidade", callback_data="customers_by_city"),
                    InlineKeyboardButton("💎 VIPs", callback_data="vip_customers"),
                ],
                [InlineKeyboardButton("🔙 Menu Principal", callback_data="main_menu")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
        except Exception as e:
            logger.error(f"Error in customers command: {e}")
            await update.message.reply_text("❌ Erro ao buscar clientes. Tente novamente.")
    
    async def sales_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sales command."""
        try:
            # Get sales analytics
            sales_data = data_manager.get_sales_analytics()
            analytics = sales_data["analytics"]
            
            message = "📊 **Análise de Vendas:**\n\n"
            message += f"💰 **Receita Total:** R$ {analytics['total_revenue']:,.2f}\n"
            message += f"🛒 **Total de Vendas:** {analytics['total_sales']:,}\n"
            message += f"📈 **Ticket Médio:** R$ {analytics['avg_order_value']:.2f}\n\n"
            
            message += "💳 **Métodos de Pagamento:**\n"
            for method, count in list(analytics['top_payment_methods'].items())[:3]:
                message += f"• {method}: {count} vendas\n"
            
            # Create keyboard for sales actions
            keyboard = [
                [
                    InlineKeyboardButton("📅 Por Período", callback_data="sales_by_period"),
                    InlineKeyboardButton("📂 Por Categoria", callback_data="sales_by_category"),
                ],
                [InlineKeyboardButton("🔙 Menu Principal", callback_data="main_menu")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
        except Exception as e:
            logger.error(f"Error in sales command: {e}")
            await update.message.reply_text("❌ Erro ao buscar dados de vendas. Tente novamente.")
    
    async def insights_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /insights command."""
        try:
            # Get insights
            insights_data = data_manager.get_insights()
            insights = insights_data["insights"]
            recommendations = insights_data["recommendations"]
            
            message = "💡 **Insights de Negócio:**\n\n"
            
            # Products insights
            message += f"📦 **Produtos:** {insights['products']['total_products']} total\n"
            message += f"⚠️ **Estoque Baixo:** {insights['products']['low_stock_products']} produtos\n"
            message += f"⭐ **Avaliação Média:** {insights['products']['avg_rating']}/5\n\n"
            
            # Customer insights
            message += f"👥 **Clientes:** {insights['customers']['total_customers']} total\n"
            message += f"💰 **Gasto Médio:** R$ {insights['customers']['avg_total_spent']:.2f}\n\n"
            
            # Recommendations
            message += "🎯 **Recomendações:**\n"
            for i, rec in enumerate(recommendations[:3], 1):
                message += f"{i}. {rec}\n"
            
            # Create keyboard
            keyboard = [
                [InlineKeyboardButton("📈 Relatório Completo", callback_data="full_report")],
                [InlineKeyboardButton("🔙 Menu Principal", callback_data="main_menu")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
        except Exception as e:
            logger.error(f"Error in insights command: {e}")
            await update.message.reply_text("❌ Erro ao gerar insights. Tente novamente.")
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command."""
        user_id = update.effective_user.id
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
        
        await update.message.reply_text("🧹 Histórico de conversa limpo!")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button presses."""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "main_menu":
            await self.start_command(update, context)
        elif data == "help":
            await self.help_command(update, context)
        elif data == "products":
            await self.products_command(update, context)
        elif data == "customers":
            await self.customers_command(update, context)
        elif data == "sales":
            await self.sales_command(update, context)
        elif data == "insights":
            await self.insights_command(update, context)
        elif data == "vip_customers":
            await self._handle_vip_customers(query)
        elif data == "products_by_category":
            await self._handle_products_by_category(query)
        else:
            await query.edit_message_text("🔧 Funcionalidade em desenvolvimento...")
    
    async def _handle_vip_customers(self, query):
        """Handle VIP customers query."""
        try:
            customers_data = data_manager.get_customers(customer_value="VIP", limit=10)
            
            if customers_data["customers"]:
                message = "💎 **Clientes VIP:**\n\n"
                for i, customer in enumerate(customers_data["customers"], 1):
                    message += f"{i}. **{customer['name']}**\n"
                    message += f"   💰 R$ {customer['total_spent']:.2f}\n"
                    message += f"   📍 {customer['city']}\n\n"
            else:
                message = "❌ Nenhum cliente VIP encontrado."
            
            await query.edit_message_text(message, parse_mode='Markdown')
        
        except Exception as e:
            logger.error(f"Error handling VIP customers: {e}")
            await query.edit_message_text("❌ Erro ao buscar clientes VIP.")
    
    async def _handle_products_by_category(self, query):
        """Handle products by category query."""
        try:
            # Get products by Electronics category as example
            products_data = data_manager.get_products(category="Electronics", limit=5)
            
            if products_data["products"]:
                message = "📱 **Produtos - Eletrônicos:**\n\n"
                for i, product in enumerate(products_data["products"], 1):
                    message += f"{i}. **{product['product_name']}**\n"
                    message += f"   💰 R$ {product['price']:.2f}\n"
                    message += f"   ⭐ {product['rating']}/5\n\n"
            else:
                message = "❌ Nenhum produto encontrado na categoria."
            
            await query.edit_message_text(message, parse_mode='Markdown')
        
        except Exception as e:
            logger.error(f"Error handling products by category: {e}")
            await query.edit_message_text("❌ Erro ao buscar produtos por categoria.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle general text messages."""
        user_id = update.effective_user.id
        user_message = update.message.text
        
        logger.info(f"User {user_id} sent message: {user_message}")
        
        try:
            # Add to conversation history
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            self.conversation_history[user_id].append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Generate response
            response = await self.generate_response(user_message, user_id)
            
            # Add response to history
            self.conversation_history[user_id].append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
            await update.message.reply_text(response, parse_mode='Markdown')
        
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text("❌ Desculpe, ocorreu um erro. Tente novamente.")
    
    async def generate_response(self, message: str, user_id: int) -> str:
        """Generate response using LLM or fallback logic."""
        if self.openai_client:
            return await self._generate_llm_response(message, user_id)
        else:
            return await self._generate_fallback_response(message)
    
    async def _generate_llm_response(self, message: str, user_id: int) -> str:
        """Generate response using OpenAI LLM."""
        try:
            # Get conversation history
            history = self.conversation_history.get(user_id, [])
            
            # Prepare system message with Brazilian retail context
            system_message = """
Você é o RetailAssist, um consultor sênior especializado em varejo brasileiro com 15 anos de experiência. Você trabalhou com grandes redes como Magazine Luiza, Via Varejo, Lojas Americanas e ajudou centenas de pequenos e médios varejistas a crescer.

PERSONALIDADE:
- Consultor experiente, direto e prático
- Responde com insights específicos e acionáveis
- Não oferece listas genéricas de opções
- Interpreta a pergunta e dá uma resposta completa e útil
- Fala como um especialista que conhece o mercado brasileiro na prática

CONHECIMENTO PROFUNDO DO BRASIL:
- Classes C e D representam 70% do mercado brasileiro
- PIX revolucionou pagamentos (35% das transações)
- Consumidor brasileiro é sensível a preço mas valoriza parcelamento
- Black Friday, Dia das Mães e Natal são os picos sazonais
- Nordeste cresce 15% ao ano, Sul tem maior ticket médio
- Mobile representa 65% do e-commerce nacional
- Consumidor regional: Norte prefere eletrônicos, Sul prefere moda

COMO RESPONDER:
1. INTERPRETE a pergunta do usuário
2. DÊ UMA RESPOSTA DIRETA E ESPECÍFICA
3. INCLUA dados reais do mercado brasileiro
4. SUGIRA ações práticas e imediatas
5. USE exemplos de empresas brasileiras conhecidas
6. CONTEXTUALIZE com a realidade regional/sazonal
7. SEJA CONCISO mas COMPLETO

NUNCA:
- Ofereça listas genéricas de "posso ajudar com..."
- Diga "use o comando /alguma_coisa"
- Dê respostas vagas ou superficiais
- Liste opções sem dar uma recomendação clara

SEMPRE:
- Responda como se fosse uma consultoria paga
- Dê insights específicos e valiosos
- Inclua números e dados quando relevante
- Sugira próximos passos concretos

Você tem acesso a dados de 1000 produtos, 500 clientes e 2000 vendas de uma empresa brasileira típica. Use esses dados para dar exemplos práticos.
            """
            
            # Prepare messages for OpenAI
            messages = [{"role": "system", "content": system_message}]
            
            # Add recent conversation history (last 10 messages)
            for msg in history[-10:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Get relevant data based on the message
            context_data = await self._get_context_data(message)
            
            # Add current message with context
            user_message = message
            if context_data:
                user_message += f"\n\nDados disponíveis para análise:\n{context_data}"
            
            messages.append({"role": "user", "content": user_message})
            
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=0.7,
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return await self._generate_fallback_response(message)
    
    async def _get_context_data(self, message: str) -> str:
        """Get relevant context data based on the user message."""
        message_lower = message.lower()
        context_parts = []
        
        try:
            # If asking about products
            if any(word in message_lower for word in ["produto", "item", "estoque", "categoria"]):
                products_data = data_manager.get_products(limit=5)
                if products_data["products"]:
                    context_parts.append("📦 Produtos em destaque:")
                    for p in products_data["products"][:3]:
                        context_parts.append(f"- {p['product_name']}: R$ {p['price']:.2f} ({p['category']}, estoque: {p['stock_quantity']})")
                    context_parts.append(f"Total de produtos: {products_data['total_count']}")
            
            # If asking about customers
            if any(word in message_lower for word in ["cliente", "consumidor", "comprador"]):
                customers_data = data_manager.get_customers(limit=5)
                if customers_data["customers"]:
                    context_parts.append("👥 Perfil de clientes:")
                    cities = {}
                    total_spent = 0
                    for c in customers_data["customers"]:
                        cities[c['city']] = cities.get(c['city'], 0) + 1
                        total_spent += c['total_spent']
                    context_parts.append(f"- Cidades principais: {', '.join(cities.keys())}")
                    context_parts.append(f"- Gasto médio: R$ {total_spent/len(customers_data['customers']):.2f}")
                    context_parts.append(f"Total de clientes: {customers_data['total_count']}")
            
            # If asking about sales
            if any(word in message_lower for word in ["venda", "receita", "faturamento", "performance"]):
                sales_data = data_manager.get_sales_analytics()
                analytics = sales_data["analytics"]
                context_parts.append("📊 Performance de vendas:")
                context_parts.append(f"- Receita total: R$ {analytics['total_revenue']:,.2f}")
                context_parts.append(f"- Total de vendas: {analytics['total_sales']:,}")
                context_parts.append(f"- Ticket médio: R$ {analytics['avg_order_value']:.2f}")
                context_parts.append(f"- Métodos de pagamento populares: {', '.join(list(analytics['top_payment_methods'].keys())[:3])}")
            
            # If asking for insights or recommendations
            if any(word in message_lower for word in ["insight", "recomendação", "estratégia", "dica", "conselho"]):
                insights_data = data_manager.get_insights()
                insights = insights_data["insights"]
                context_parts.append("💡 Dados para insights:")
                context_parts.append(f"- {insights['products']['low_stock_products']} produtos com estoque baixo")
                context_parts.append(f"- Avaliação média dos produtos: {insights['products']['avg_rating']:.1f}/5")
                context_parts.append(f"- Gasto médio por cliente: R$ {insights['customers']['avg_total_spent']:.2f}")
                
                if insights_data["recommendations"]:
                    context_parts.append("Recomendações atuais:")
                    for rec in insights_data["recommendations"][:2]:
                        context_parts.append(f"- {rec}")
        
        except Exception as e:
            logger.error(f"Error getting context data: {e}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    async def _generate_fallback_response(self, message: str) -> str:
        """Generate fallback response without LLM."""
        message_lower = message.lower()
        
        # Product-related queries
        if any(word in message_lower for word in ["produto", "item", "mercadoria", "estoque"]):
            return """
📦 **Análise de Produtos - Varejo Brasileiro:**

Use `/products` para ver produtos em destaque ou pergunte:
• "Quais produtos estão com estoque baixo?" 
• "Mostre eletrônicos mais vendidos"
• "Produtos ideais para Black Friday"
• "Itens com melhor margem de lucro"

💡 **Dicas para o varejo brasileiro:**
- Considere sazonalidades (Dia das Mães, Natal)
- Analise produtos por região (Sul vs Nordeste)
- Foque em categorias populares: moda, eletrônicos, casa

Posso ajudar com estratégias de mix de produtos! 🛍️
            """
        
        # Customer-related queries
        elif any(word in message_lower for word in ["cliente", "consumidor", "comprador"]):
            return """
👥 **Análise de Clientes - Consumidor Brasileiro:**

Use `/customers` para ver dados de clientes ou pergunte:
• "Clientes VIP por região"
• "Perfil de compradores da classe C"
• "Clientes que preferem PIX"
• "Consumidores de São Paulo vs Interior"

🇧🇷 **Insights do consumidor brasileiro:**
- Classes C e D representam 70% do mercado
- PIX revolucionou os pagamentos
- Consumidor regional tem preferências distintas
- Mobile commerce cresce 25% ao ano

Posso ajudar com segmentação e estratégias regionais! 📊
            """
        
        # Sales-related queries
        elif any(word in message_lower for word in ["venda", "receita", "faturamento", "vendas"]):
            return """
📊 **Performance de Vendas - Mercado Brasileiro:**

Use `/sales` para análise de vendas ou pergunte:
• "Performance vs Black Friday do ano passado"
• "Vendas por método de pagamento (PIX, cartão)"
• "Comparativo regional de vendas"
• "Ticket médio por classe social"

💰 **Métricas importantes no Brasil:**
- Ticket médio nacional: R$ 85-120
- PIX representa 35% dos pagamentos
- Sazonalidades impactam 40% das vendas
- Mobile representa 60% do e-commerce

Posso ajudar com estratégias de crescimento! 📈
            """
        
        # Insights-related queries
        elif any(word in message_lower for word in ["insight", "análise", "relatório", "recomendação"]):
            return """
💡 **Insights Estratégicos - Varejo Brasileiro:**

Use `/insights` para análises completas ou pergunte:
• "Estratégias para aumentar conversão"
• "Como aproveitar a sazonalidade brasileira"
• "Oportunidades no mercado regional"
• "Tendências do consumidor brasileiro"

🎯 **Estratégias para o mercado nacional:**
- Aproveite datas comemorativas brasileiras
- Adapte produtos por região (clima, cultura)
- Invista em omnichannel (físico + digital)
- Foque na experiência mobile-first

Posso criar planos de ação personalizados! 🚀
            """
        
        # Bot presentation queries
        elif any(phrase in message_lower for phrase in ["quem é você", "o que você faz", "quem você é", "se apresente", "apresentação", "sobre você"]):
            return """
🤖 **Apresentação - RetailAssist**

**Quem sou eu:**
Sou o RetailAssist, um assistente de inteligência artificial especializado em varejo brasileiro. Fui criado para ser seu consultor pessoal de negócios!

**🎯 Minha especialidade:**
Varejo no Brasil - conheço profundamente o comportamento do consumidor brasileiro, sazonalidades, métodos de pagamento, diferenças regionais e estratégias que funcionam no nosso mercado.

**🧠 O que sei sobre o mercado brasileiro:**
• Classes sociais A, B, C, D, E e suas características
• PIX, cartão, boleto e preferências de pagamento
• Sazonalidades: Black Friday, Dia das Mães, Natal, etc.
• Diferenças regionais: Sudeste, Nordeste, Sul, Norte
• Tendências do e-commerce e varejo físico nacional

**💼 Como posso ajudar seu negócio:**
• Análise de dados de vendas e performance
• Estratégias de produtos e mix ideal
• Segmentação e perfil de clientes
• Campanhas sazonais e promocionais
• Insights para aumentar conversão e ticket médio
• Recomendações personalizadas para seu negócio

**🚀 Meu diferencial:**
Não sou apenas um chatbot - sou um consultor que entende a realidade do varejo brasileiro e posso te dar conselhos práticos e estratégias que realmente funcionam no nosso mercado.

**Pronto para começar?** Me conte sobre seu negócio ou faça uma pergunta! 🇧🇷
            """
        
        # Greeting
        elif any(word in message_lower for word in ["oi", "olá", "hello", "bom dia", "boa tarde", "boa noite"]):
            return """
👋 **Olá! Seja bem-vindo ao RetailAssist!**

🤖 Eu sou seu consultor especializado em **varejo brasileiro**! 

**🎯 Minha missão:**
Ajudar você a tomar decisões estratégicas baseadas em dados para fazer seu negócio crescer no mercado brasileiro.

**🚀 O que posso fazer por você:**
• 📊 **Análise de Performance** - Vendas, métricas e KPIs
• 📦 **Gestão de Produtos** - Mix ideal, estoque, categorias
• 👥 **Perfil de Clientes** - Segmentação por região e classe social
• 💰 **Estratégias de Preço** - Otimização para o mercado nacional
• 🎯 **Campanhas Sazonais** - Black Friday, Dia das Mães, Natal
• 🏪 **Omnichannel** - Integração físico + digital

**💬 Exemplos do que você pode me perguntar:**
• "Como preparar minha loja para a Black Friday?"
• "Quais produtos vendem mais na região Nordeste?"
• "Estratégias para conquistar a classe C"
• "Como aumentar meu ticket médio?"

**⚡ Comandos rápidos:**
• `/products` - Análise de produtos
• `/customers` - Perfil de clientes  
• `/sales` - Performance de vendas
• `/insights` - Estratégias de crescimento

Pode falar comigo em linguagem natural! Estou aqui para ajudar seu varejo a crescer! 🇧🇷✨
            """
        
        # Default response
        else:
            return """
🤔 **Hmm, não entendi sua pergunta, mas posso te ajudar!**

🤖 **Sou o RetailAssist, seu consultor de varejo brasileiro!**

**💡 Aqui estão algumas sugestões do que posso fazer:**

📊 **Análises que posso gerar:**
• Performance de vendas por período
• Produtos com melhor margem
• Perfil de clientes por região
• Comparativos sazonais

🎯 **Estratégias que posso sugerir:**
• Preparação para datas comemorativas
• Otimização de mix de produtos
• Campanhas para diferentes classes sociais
• Expansão regional

**💬 Experimente perguntar:**
• "Mostre os produtos mais vendidos"
• "Como estão as vendas este mês?"
• "Quais clientes compram mais?"
• "Dicas para aumentar vendas"

**⚡ Ou use os comandos:**
• `/products` - Gestão de produtos
• `/customers` - Análise de clientes
• `/sales` - Performance de vendas
• `/insights` - Estratégias de crescimento

Fale comigo como se fosse seu consultor pessoal! 🚀
            """
    
if __name__ == "__main__":
    # This file should be imported, not run directly
    # Use run_bot.py to start the bot
    print("Use 'python run_bot.py' to start the bot")
