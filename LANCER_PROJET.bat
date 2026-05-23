@echo off
chcp 65001 >nul
echo ========================================
echo Lancement du projet Symfony
echo ========================================
echo.

REM Ajouter PHP au PATH pour cette session
set PATH=C:\Program Files\PHP;%PATH%

REM Vérifier PHP
php -v >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] PHP n'est pas trouve dans C:\Program Files\PHP
    echo Veuillez verifier le chemin d'installation de PHP
    pause
    exit /b 1
)

echo [OK] PHP detecte
echo.

REM Vérifier les dépendances
if not exist "vendor\autoload.php" (
    echo Installation des dependances Symfony...
    composer install
    echo.
)

REM Vérifier les dépendances Python
python -m pip show pandas >nul 2>&1
if errorlevel 1 (
    echo Installation des dependances Python...
    pip install -r python_scripts\requirements.txt
    echo.
)

echo ========================================
echo Demarrage du serveur Symfony
echo ========================================
echo.
echo Le serveur sera accessible sur: http://localhost:8000
echo Appuyez sur Ctrl+C pour arreter le serveur
echo.
echo.

REM Démarrer le serveur
php -S localhost:8000 -t public

pause


