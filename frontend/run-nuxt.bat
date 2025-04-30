@echo off
echo Setting up environment and starting Nuxt dev server...

REM ## Change directory to the Nuxt project root ##
cd /d %~dp0
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to change directory to %~dp0
    echo Please ensure this batch file is inside your Nuxt project root directory.
    pause
    exit /b 1
)
echo Changed directory to: %cd%

REM ## Set the backend API URL for the frontend to localhost (for local development reliability) ##
set NUXT_PUBLIC_API_BASE=http://localhost:5000
echo Setting NUXT_PUBLIC_API_BASE to: %NUXT_PUBLIC_API_BASE%

REM ## Start the Nuxt development server ##
REM    --host 0.0.0.0 allows access from other devices on the local network (if network & firewall permit)
REM    --port 3000 sets the frontend port
echo Running 'npm run dev -- --host 0.0.0.0 --port 3000'
npm run dev -- --host 0.0.0.0 --port 3000

REM Optional: Keep the console window open after process finishes (e.g., on error)
REM pause