# Quick Start Guide

Get the SOAP-to-REST Transaction Viewer running in under 5 minutes!

## Prerequisites

- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **Claude API Key** (optional, for AI insights) - [Get one here](https://console.anthropic.com/)

## Installation

### Option 1: Automated Startup (Recommended)

#### Linux/Mac:
```bash
./start.sh
```

#### Windows:
```cmd
start.bat
```

The startup script will:
- ✅ Install all dependencies automatically
- ✅ Start all three services (SOAP, REST, Frontend)
- ✅ Open your browser to http://localhost:3000

### Option 2: Manual Setup

#### 1. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

#### 3. Configure Environment (Optional)
```bash
cp .env.example .env
# Edit .env and add your CLAUDE_API_KEY
```

#### 4. Start Services

**Terminal 1 - SOAP Service:**
```bash
python backend/soap_service.py
```

**Terminal 2 - REST Gateway:**
```bash
python backend/rest_gateway.py
```

**Terminal 3 - React Frontend:**
```bash
cd frontend
npm start
```

## Using the Application

1. **Open your browser** to http://localhost:3000
2. **Enter a customer ID** (try 1-100)
3. **Click "Get Transactions"**
4. **View the four panels:**
   - 📡 Raw SOAP XML
   - 🔄 Converted JSON
   - 🔒 Masked PII Data
   - 🤖 AI Insights (requires Claude API key)

## Sample Customer IDs to Try

- **42** - John Smith with varied spending
- **1** - First customer in the system
- **99** - High-value transactions
- Any number 1-100 will work!

## Troubleshooting

### Port Already in Use

If you see "port already in use" errors:

**Linux/Mac:**
```bash
./stop.sh  # Stop all services
./start.sh # Restart
```

**Windows:**
```cmd
# Find and kill processes on ports 3000, 5000, 5001
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Dependencies Not Installing

**Python issues:**
```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

**Node.js issues:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### AI Insights Not Working

This is expected if you haven't set up the Claude API key:

1. Copy `.env.example` to `.env`
2. Add your Claude API key: `CLAUDE_API_KEY=sk-ant-...`
3. Restart the REST Gateway service

Get a free API key at: https://console.anthropic.com/

## Stopping Services

**Linux/Mac:**
```bash
./stop.sh
```

**Windows:**
- Close each terminal window
- Or press `Ctrl+C` in each window

## What's Running?

- **Port 5000**: SOAP Service (legacy XML API)
- **Port 5001**: REST Gateway (modern JSON API with PII masking)
- **Port 3000**: React Frontend (web UI)

## Next Steps

- ✅ Try different customer IDs
- ✅ View the transformation from SOAP to REST
- ✅ See how PII masking works
- ✅ Add your Claude API key for AI insights
- ✅ Explore the code in `backend/` and `frontend/src/`

## Need Help?

Check the main README.md for:
- Full architecture documentation
- API endpoint details
- Project structure
- Portfolio highlights

Enjoy exploring the SOAP-to-REST transformation! 🚀
