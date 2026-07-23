@echo off
setlocal
set "PYTHON_EXE=C:\Users\felip\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
set "APP_URL=http://127.0.0.1:8876"
cd /d "%~dp0"

for /f "tokens=5" %%p in ('netstat -ano ^| findstr :8876 ^| findstr LISTENING') do (
  taskkill /PID %%p /F >nul 2>&1
)

echo Iniciando o Dashboard Passini...
start "Passini Dashboard Server" /D "%~dp0" "%PYTHON_EXE%" "%~dp0backend.py"
timeout /t 2 /nobreak >nul
start "" "%APP_URL%"
echo Navegador aberto em %APP_URL%
echo Se a porta ja estiver em uso, feche a janela antiga "Passini Dashboard Server" e execute novamente.
