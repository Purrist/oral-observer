@echo off
echo Setting up environment and starting Nuxt dev server for LAN access...

REM ## Change directory to the Nuxt project root ##
cd /d %~dp0
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to change directory to %~dp0
    echo Please ensure this batch file is inside your Nuxt project root directory.
    pause
    exit /b 1
)
echo Changed directory to: %cd%

REM ## Manually Set the backend API URL for the frontend to the LAN IP ##
REM    !!! IMPORTANT !!! Replace 222.240.52.9 with YOUR computer's actual LAN IP.
REM    You can find this IP by running 'ipconfig' in Command Prompt (CMD) or PowerShell.
set NUXT_PUBLIC_API_BASE=http://222.240.52.9:5000
echo Setting NUXT_PUBLIC_API_BASE to: %NUXT_PUBLIC_API_BASE%

REM ## Start the Nuxt development server ##
REM    --host 0.0.0.0 allows access from other devices on the local network
REM    --port 3000 sets the frontend port
echo Running 'npm run dev -- --host 0.0.0.0 --port 3000'

REM --- Direct execution in the current terminal ---
npm run dev -- --host 0.0.0.0 --port 3000

REM Optional: Keep the console window open after process finishes (e.g., on error)
REM pause