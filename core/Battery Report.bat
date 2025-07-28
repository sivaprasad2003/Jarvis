@echo off
echo Generating battery report...
powercfg /batteryreport
timeout /t 2 >nul
echo Opening battery report...
start "" "C:\Users\sivap\battery-report.html"
exit
