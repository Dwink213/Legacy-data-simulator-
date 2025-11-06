#!/bin/bash

# SOAP-to-REST Transaction Viewer Startup Script
# Starts all services: SOAP service, REST gateway, and React frontend

echo "🚀 Starting SOAP-to-REST Transaction Viewer..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please add your CLAUDE_API_KEY if you want AI insights."
    echo ""
fi

# Check if Python dependencies are installed
echo "📦 Checking Python dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Check if Node dependencies are installed
echo "📦 Checking Node.js dependencies..."
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing Node.js dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "✅ All dependencies installed!"
echo ""
echo "Starting services..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create logs directory
mkdir -p logs

# Start SOAP service in background
echo "🔷 Starting SOAP Service on port 5000..."
python3 backend/soap_service.py > logs/soap_service.log 2>&1 &
SOAP_PID=$!
echo "   PID: $SOAP_PID"

# Wait a moment for SOAP service to start
sleep 2

# Start REST gateway in background
echo "🔷 Starting REST Gateway on port 5001..."
python3 backend/rest_gateway.py > logs/rest_gateway.log 2>&1 &
GATEWAY_PID=$!
echo "   PID: $GATEWAY_PID"

# Wait a moment for gateway to start
sleep 2

# Start React frontend in background
echo "🔷 Starting React Frontend on port 3000..."
cd frontend
npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "   PID: $FRONTEND_PID"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All services started!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend:     http://localhost:3000"
echo "   REST API:     http://localhost:5001/api"
echo "   SOAP Service: http://localhost:5000/soap"
echo ""
echo "📋 Process IDs:"
echo "   SOAP Service: $SOAP_PID"
echo "   REST Gateway: $GATEWAY_PID"
echo "   Frontend:     $FRONTEND_PID"
echo ""
echo "📝 Logs available in: ./logs/"
echo ""
echo "⏹️  To stop all services, run: ./stop.sh"
echo "   Or press Ctrl+C and run: kill $SOAP_PID $GATEWAY_PID $FRONTEND_PID"
echo ""

# Save PIDs to file for stop script
echo "$SOAP_PID" > logs/soap.pid
echo "$GATEWAY_PID" > logs/gateway.pid
echo "$FRONTEND_PID" > logs/frontend.pid

echo "Waiting for services to initialize..."
sleep 5

# Open browser (optional)
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:3000
elif command -v open > /dev/null; then
    open http://localhost:3000
fi

echo ""
echo "Press Ctrl+C to view this message again, or use ./stop.sh to stop all services."
echo ""

# Keep script running
wait
