# Crypto Advisory Pro 🤖

A comprehensive cryptocurrency advisory web application providing AI-powered market analysis, investment recommendations, and educational content.

## Features

- 📊 **Real-time Market Data** - Live cryptocurrency prices and market analysis
- 🤖 **AI-Powered Analysis** - Deep insights using OpenAI and DeepSeek
- 🎯 **Investment Recommendations** - Buy/hold/sell advice with risk assessment
- 📚 **Educational Content** - Crypto investing guides and risk management
- 💼 **Portfolio Tracking** - Manage and track your cryptocurrency investments
- 🔍 **Advanced Search** - Find and analyze any cryptocurrency

## Deployment on Render

### Prerequisites
- GitHub account
- Render account
- OpenAI API key (optional)
- DeepSeek API key (optional)

### Deployment Steps

1. **Fork this repository** to your GitHub account

2. **Create a new Web Service on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" and select "Web Service"
   - Connect your GitHub account and select the repository
   - Use the following settings:
     - **Name**: `crypto-advisory-app`
     - **Environment**: `Python`
     - **Region**: Choose closest to you
     - **Branch**: `main`
     - **Root Directory**: (leave empty)
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`

3. **Add Environment Variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key (optional)
   - `DEEPSEEK_API_KEY`: Your DeepSeek API key (optional)
   - `SECRET_KEY`: A random secret key for Flask sessions

4. **Deploy**:
   - Click "Create Web Service"
   - Render will automatically build and deploy your application

## Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/crypto-advisory-app.git
   cd crypto-advisory-app