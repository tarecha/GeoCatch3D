@echo off
cd /d "%~dp0"
echo Menjalankan GeoCatch 3D Server dan merekam log...

powershell -Command "python -u -X utf8 mainVUEv3.py --server 2>&1 | tee log_server.txt"

pause