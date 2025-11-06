@echo off
REM SOAP-to-REST Transaction Viewer Startup Script (Windows)
REM Starts all services: SOAP service, REST gateway, and React frontend

echo.
echo Starting SOAP-to-REST Transaction Viewer...
echo.

REM Check if .env file exists
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo .env file created. Please add your CLAUDE_API_KEY if you want AI insights.
    echo.
)

REM Check if Python dependencies are installed
echo Checking Python dependencies...
pip install -r requirements.txt

REM Check if Node dependencies are installed
echo Checking Node.js dependencies...
if not exist frontend\node_modules (
    echo Installing Node.js dependencies...
    cd frontend
    call npm install
    cd ..
)

echo.
echo All dependencies installed!
echo.
echo Starting services...
echo ================================================
echo.

REM Create logs directory
if not exist logs mkdir logs

REM Start SOAP service
echo Starting SOAP Service on port 5000...
start "SOAP Service" python backend\soap_service.py

timeout /t 2 /nobreak > nul

REM Start REST gateway
echo Starting REST Gateway on port 5001...
start "REST Gateway" python backend\rest_gateway.py

timeout /t 2 /nobreak > nul

REM Start React frontend
echo Starting React Frontend on port 3000...
cd frontend
start "React Frontend" npm start
cd ..

echo.
echo ================================================
echo All services started!
echo.
echo Access the application:
echo   Frontend:     http://localhost:3000
echo   REST API:     http://localhost:5001/api
echo   SOAP Service: http://localhost:5000/soap
echo.
echo Logs available in: .\logs\
echo.
echo To stop services, close the terminal windows or press Ctrl+C in each.
echo.

timeout /t 3 /nobreak > nul
start http://localhost:3000

echo.
pause
