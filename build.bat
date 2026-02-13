@echo off
echo =======================
echo   BUILD PROVISIONADOR 
echo =======================
echo.

:: 1. Instalar dependencias
echo [1/3] Verificando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Erro ao instalar dependencias.
    pause
    exit /b %errorlevel%
)

:: 2. Limpar builds anteriores
echo [2/3] Limpando arquivos temporarios...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

:: 3. Compilar
echo [3/3] Compilando executavel...
echo.
echo Executando PyInstaller...
pyinstaller --noconfirm ^
    --onefile ^
    --uac-admin ^
    --name "Provisionador" ^
    --hidden-import=rich ^
    --hidden-import=rich.live ^
    --hidden-import=rich.progress ^
    --hidden-import=rich.console ^
    --hidden-import=rich.panel ^
    --hidden-import=rich.table ^
    --hidden-import=rich.prompt ^
    --collect-all rich ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha na compilacao!
    pause
    exit /b %errorlevel%
)

echo.
echo ==========================================
echo   SUCESSO!
echo   Arquivo gerado em: dist\Provisionador.exe
echo ==========================================
pause
