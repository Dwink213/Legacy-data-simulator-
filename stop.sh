#!/bin/bash

# Stop all services

echo "⏹️  Stopping SOAP-to-REST Transaction Viewer services..."
echo ""

# Read PIDs from files
if [ -f logs/soap.pid ]; then
    SOAP_PID=$(cat logs/soap.pid)
    echo "Stopping SOAP Service (PID: $SOAP_PID)..."
    kill $SOAP_PID 2>/dev/null
    rm logs/soap.pid
fi

if [ -f logs/gateway.pid ]; then
    GATEWAY_PID=$(cat logs/gateway.pid)
    echo "Stopping REST Gateway (PID: $GATEWAY_PID)..."
    kill $GATEWAY_PID 2>/dev/null
    rm logs/gateway.pid
fi

if [ -f logs/frontend.pid ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    echo "Stopping React Frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null
    rm logs/frontend.pid
fi

# Also kill any processes on these ports (backup)
echo ""
echo "Cleaning up any remaining processes on ports 3000, 5000, 5001..."
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:5000 | xargs kill -9 2>/dev/null
lsof -ti:5001 | xargs kill -9 2>/dev/null

echo ""
echo "✅ All services stopped!"
