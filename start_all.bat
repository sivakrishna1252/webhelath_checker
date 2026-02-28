@echo off
echo ==========================================
echo Starting Web Health Checker Dashboard...
echo ==========================================
start "Django Server" cmd /k "python manage.py runserver"

echo.
echo ==========================================
echo Starting Professional Background Monitor...
echo ==========================================
start "Health Monitor" cmd /k "python background_monitor.py"

echo.
echo Both services are now starting. 
echo - Dashboard: http://127.0.0.1:8000
echo - Monitoring: Active in background
echo.
pause




#.\start_all.bat
