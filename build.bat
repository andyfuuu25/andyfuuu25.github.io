@echo off
REM Rebuilds the site from content\site.toml. Double-click this file.
setlocal

cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo.
  echo Python was not found on this computer.
  echo Install it from https://www.python.org/downloads/ ^(tick "Add python.exe to PATH"^)
  echo then double-click this file again.
  echo.
  pause
  exit /b 1
)

python -c "import markdown" >nul 2>nul
if errorlevel 1 (
  echo Installing the one dependency ^(markdown^)...
  python -m pip install --quiet markdown
  if errorlevel 1 (
    echo.
    echo Could not install it. Try running this by hand:
    echo     python -m pip install markdown
    echo.
    pause
    exit /b 1
  )
)

echo.
python tools\build.py
set BUILD_STATUS=%errorlevel%
echo.

if %BUILD_STATUS% neq 0 (
  echo Build FAILED - see the message above. index.html was not changed.
  echo.
  pause
  exit /b %BUILD_STATUS%
)

echo Preview it:  open index.html, or run  python -m http.server 8000
echo Publish it:  git add -A ^&^& git commit -m "Update site" ^&^& git push
echo.
pause
