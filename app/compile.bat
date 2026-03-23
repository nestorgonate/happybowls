@echo off
pyinstaller --onefile ^
 --add-data "app/dist;app/dist" ^
 main.py

echo.
echo Codigo python compilado a exe
pause