from flask import Flask, render_template, request, jsonify
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

class CryptoAdvisor:
    def __init__(self):
        self.api_base = "https://api.coingecko.com/api/v3"
        self.setup_ai_services()
    
    def setup_ai_services(self):
        """Setup AI services with API keys"""
        self.ai_enabled = False
        self.ai_services = {}
        
        # OpenAI setup
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            try:
                self.ai_services['openai'] = OpenAI(api_key=openai_api_key)
                print("✅ OpenAI service configured")
            except Exception as e:
                print(f"❌ OpenAI setup failed: {e}")
        
        # DeepSeek setup
        deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        if deepseek_api_key:
            try:
                self.ai_services['deepseek'] = OpenAI(
                    api_key=deepseek_api_key,
                    base_url="https://api.deepseek.com/v1"
                )
                print("✅ DeepSeek service configured")
            except Exception as e:
                print(f"❌ DeepSeek setup failed: {e}")
        
        if self.ai_services:
            self.ai_enabled = True
            print("🤖 AI analysis features are ENABLED")

    def get_crypto_data(self, coin_id='bitcoin'):
        """Fetch current cryptocurrency data"""
        try:
            url = f"{self.api_base}/coins/{coin_id}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            return {
                'name': data.get('name', ''),
                'symbol': data.get('symbol', '').upper(),
                'current_price': data.get('market_data', {}).get('current_price', {}).get('usd', 0),
                'market_cap': data.get('market_data', {}).get('market_cap', {}).get('usd', 0),
                'price_change_24h': data.get('market_data', {}).get('price_change_percentage_24h', 0),
                'volume_24h': data.get('market_data', {}).get('total_volume', {}).get('usd', 0),
                'circulating_supply': data.get('market_data', {}).get('circulating_supply', 0),
                'image': data.get('image', {}).get('large', '')
            }
        except Exception as e:
            print(f"Error fetching data: {e}")
            return {}

    def get_top_cryptos(self, limit=20):
        """Get top cryptocurrencies by market cap"""
        try:
            url = f"{self.api_base}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': False
            }
            response = requests.get(url, params=params, timeout=10)
            return response.json()
        except Exception as e:
            print(f"Error fetching top cryptos: {e}")
            return []

    def analyze_market_sentiment(self, coin_data):
        """Analyze market sentiment"""
        price_change = coin_data.get('price_change_24h', 0)
        
        if price_change > 10:
            return "STRONG BULLISH", "success"
        elif price_change > 5:
            return "BULLISH", "info"
        elif price_change < -10:
            return "STRONG BEARISH", "danger"
        elif price_change < -5:
            return "BEARISH", "warning"
        else:
            return "NEUTRAL", "secondary"

# Initialize the advisor
advisor = CryptoAdvisor()

@app.route('/')
def index():
    """Home page with market overview"""
    top_cryptos = advisor.get_top_cryptos(10)
    
    # Add sentiment analysis to each crypto
    for crypto in top_cryptos:
        coin_data = {
            'price_change_24h': crypto.get('price_change_percentage_24h', 0)
        }
        sentiment, sentiment_color = advisor.analyze_market_sentiment(coin_data)
        crypto['sentiment'] = sentiment
        crypto['sentiment_color'] = sentiment_color
    
    return render_template('index.html', cryptos=top_cryptos, ai_enabled=advisor.ai_enabled)

@app.route('/analyze/<coin_id>')
def analyze_crypto(coin_id):
    """Analyze specific cryptocurrency"""
    coin_data = advisor.get_crypto_data(coin_id)
    
    if not coin_data:
        return "Cryptocurrency not found", 404
    
    sentiment, sentiment_color = advisor.analyze_market_sentiment(coin_data)
    
    return render_template('analysis.html', 
                         coin_data=coin_data,
                         sentiment=sentiment,
                         sentiment_color=sentiment_color,
                         ai_enabled=advisor.ai_enabled)

@app.route('/education')
def education():
    """Educational content page"""
    return render_template('education.html')

@app.route('/portfolio')
def portfolio():
    """Portfolio management page"""
    return render_template('portfolio.html')

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', message="Server error"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
