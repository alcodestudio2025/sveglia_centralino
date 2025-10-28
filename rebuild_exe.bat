@echo off
echo ========================================
echo   Rigenerazione SvegliaCentralino.exe
echo ========================================
echo.
echo Questo script ricostruira' l'exe con la nuova icona
echo.
pause
echo.
echo Pulizia file precedenti...
pyinstaller build_exe.spec --clean --noconfirm
echo.
echo ========================================
echo   Completato!
echo ========================================
echo.
echo Il nuovo exe si trova in: dist\SvegliaCentralino.exe
echo.
pause

