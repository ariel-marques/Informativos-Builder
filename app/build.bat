@echo off
REM Build .exe com PyInstaller (instale Python 3.10+ e pip antes).
REM Execute este arquivo dentro da pasta 'app'.
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller
pyinstaller --noconsole --onefile --name InformativosBuilder main.py
echo.
echo Build finalizado. O executável estará em: dist\InformativosBuilder.exe
pause
