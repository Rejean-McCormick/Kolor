@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -m pip install --user --upgrade Pillow
  if errorlevel 1 goto :error
  where pyw >nul 2>nul
  if %errorlevel%==0 (
    start "" pyw "Kolor_Studio.pyw"
  ) else (
    start "" py "Kolor_Studio.pyw"
  )
  goto :eof
)
where python >nul 2>nul
if %errorlevel%==0 (
  python -m pip install --user --upgrade Pillow
  if errorlevel 1 goto :error
  start "" pythonw "Kolor_Studio.pyw"
  goto :eof
)
echo Python 3 est necessaire. Installe Python pour Windows, puis relance ce fichier.
pause
exit /b 1
:error
echo Impossible d'installer Pillow. Verifie ta connexion Internet et Python.
pause
exit /b 1
