from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-12345')

class CryptoAdvisor:
    def __init__(self):
        self.api_base = "https://api.coingecko.com/api/v3"
        self.ai_enabled = False
        self.setup_ai_services()
    
    def setup_ai_services(self):
        """Setup AI services with API keys - with error handling"""
        try:
            # Try to import OpenAI
            from openai import OpenAI
            
            # OpenAI setup
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if openai_api_key:
                self.ai_services = {'openai': OpenAI(api_key=openai_api_key)}
                self.ai_enabled = True
                print("✅ AI services configured")
            else:
                print("ℹ️  OpenAI API key not found - AI features disabled")
                self.ai_enabled = False
                
        except ImportError:
            print("⚠️  OpenAI module not available - AI features disabled")
            self.ai_enabled = False
        except Exception as e:
            print(f"⚠️  AI setup failed: {e} - AI features disabled")
            self.ai_enabled = False

    def get_ai_analysis(self, coin_data):
        """Get AI analysis with error handling"""
        if not self.ai_enabled:
            return "AI analysis is currently unavailable. Please check if OpenAI package is installed and API keys are configured."
        
        try:
            prompt = f"""
            Analyze {coin_data.get('name')} ({coin_data.get('symbol')}) for investment purposes:
            - Current Price: ${coin_data.get('current_price', 0):,.2f}
            - 24h Change: {coin_data.get('price_change_24h', 0):.2f}%
            - Market Cap: ${coin_data.get('market_cap', 0)/1e9:.2f}B
            
            Provide brief investment analysis.
            """
            
            response = self.ai_services['openai'].chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI analysis temporarily unavailable: {str(e)}"

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

    def get_top_cryptos(self, limit=10):
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
        return render_template('error.html', message="Cryptocurrency not found"), 404
    
    sentiment, sentiment_color = advisor.analyze_market_sentiment(coin_data)
    
    # Get AI analysis if available
    ai_analysis = None
    if advisor.ai_enabled:
        ai_analysis = advisor.get_ai_analysis(coin_data)
    
    return render_template('analysis.html', 
                         coin_data=coin_data,
                         sentiment=sentiment,
                         sentiment_color=sentiment_color,
                         ai_analysis=ai_analysis,
                         ai_enabled=advisor.ai_enabled)

@app.route('/education')
def education():
    """Educational content page"""
    return render_template('education.html')

@app.route('/portfolio')
def portfolio():
    """Portfolio management page"""
    return render_template('portfolio.html')

@app.route('/api/market-data')
def api_market_data():
    """API endpoint for market data"""
    cryptos = advisor.get_top_cryptos(20)
    return jsonify(cryptos)

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', message="Server error"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
