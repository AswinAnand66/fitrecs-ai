@echo off
SETLOCAL EnableDelayedExpansion

echo Checking FitRecs AI dependencies...
echo.

REM Check Python installation
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found. Please install Python 3.10 or higher.
    exit /b 1
) else (
    python -c "import sys; print(f'[OK] Python {sys.version_info.major}.{sys.version_info.minor} installed')"
)

REM Check Node.js installation
node --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not found. Please install Node.js 18 or higher.
    exit /b 1
) else (
    for /f "tokens=1 delims=v" %%a in ('node --version') do set NODE_VERSION=%%a
    echo [OK] Node.js !NODE_VERSION! installed
)

REM Check Docker installation
docker --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker not found. Please install Docker Desktop.
    exit /b 1
) else (
    for /f "tokens=3" %%a in ('docker --version') do set DOCKER_VERSION=%%a
    echo [OK] Docker !DOCKER_VERSION! installed
)

REM Check Docker Compose installation
docker-compose --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker Compose not found. Please install Docker Compose.
    exit /b 1
) else (
    for /f "tokens=4" %%a in ('docker-compose --version') do set COMPOSE_VERSION=%%a
    echo [OK] Docker Compose !COMPOSE_VERSION! installed
)

REM Check environment files
if not exist ".env" (
    echo [WARNING] Root .env file missing. Creating from .env.example...
    if exist ".env.example" (
        copy ".env.example" ".env" > nul
        echo [OK] Created .env from .env.example
    ) else (
        echo [ERROR] .env.example not found
        exit /b 1
    )
)

if not exist "backend\.env" (
    echo [WARNING] Backend .env file missing. Creating from .env.example...
    if exist "backend\.env.example" (
        copy "backend\.env.example" "backend\.env" > nul
        echo [OK] Created backend/.env from .env.example
    ) else (
        echo [ERROR] backend/.env.example not found
        exit /b 1
    )
)

if not exist "frontend\.env" (
    echo [WARNING] Frontend .env file missing. Creating from .env.example...
    if exist "frontend\.env.example" (
        copy "frontend\.env.example" "frontend\.env" > nul
        echo [OK] Created frontend/.env from .env.example
    ) else (
        echo [ERROR] frontend/.env.example not found
        exit /b 1
    )
)

REM Check for OpenAI API key in .env
findstr /C:"OPENAI_API_KEY=sk-" .env > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] OpenAI API key not found in .env
    echo Please add your OpenAI API key to .env:
    echo OPENAI_API_KEY=sk-your-key-here
)

REM Check if ports are available
set PORTS_IN_USE=0
netstat -an | findstr ":5173" > nul
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Port 5173 is in use
    set /A PORTS_IN_USE+=1
)
netstat -an | findstr ":8000" > nul
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Port 8000 is in use
    set /A PORTS_IN_USE+=1
)
netstat -an | findstr ":5432" > nul
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Port 5432 is in use
    set /A PORTS_IN_USE+=1
)
netstat -an | findstr ":6379" > nul
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Port 6379 is in use
    set /A PORTS_IN_USE+=1
)

if !PORTS_IN_USE! GTR 0 (
    echo.
    echo [WARNING] Some required ports are in use. Please stop other services using these ports:
    echo - Frontend: 5173
    echo - Backend: 8000
    echo - Database: 5432
    echo - Redis: 6379
)

echo.
echo Dependency check complete.
if !PORTS_IN_USE! EQU 0 (
    echo [OK] All required ports are available
    echo [OK] Ready to start FitRecs AI
    exit /b 0
) else (
    echo [WARNING] Please resolve port conflicts before starting
    exit /b 1
)
