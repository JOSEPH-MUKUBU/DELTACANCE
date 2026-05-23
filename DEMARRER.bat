@echo off
chcp 65001 >nul
echo ========================================
echo Démarrage du projet Symfony
echo ========================================
echo.

REM Vérifier si PHP est installé
php -v >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] PHP n'est pas installé ou n'est pas dans le PATH
    echo.
    echo Veuillez installer PHP en suivant les instructions dans INSTALLATION_RAPIDE.md
    echo Ou exécutez en PowerShell administrateur:
    echo   choco install php composer -y
    echo.
    pause
    exit /b 1
)

REM Vérifier si Composer est installé
composer --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Composer n'est pas installé ou n'est pas dans le PATH
    echo.
    echo Veuillez installer Composer en suivant les instructions dans INSTALLATION_RAPIDE.md
    echo.
    pause
    exit /b 1
)

echo [OK] PHP et Composer sont installés
echo.

REM Vérifier si les dépendances sont installées
if not exist "vendor" (
    echo Installation des dépendances Symfony...
    echo.
    composer install
    if errorlevel 1 (
        echo [ERREUR] Échec de l'installation des dépendances
        pause
        exit /b 1
    )
    echo.
) else (
    echo [OK] Dépendances Symfony déjà installées
    echo.
)

REM Vérifier si les dépendances Python sont installées
echo Vérification des dépendances Python...
python -m pip show pandas >nul 2>&1
if errorlevel 1 (
    echo Installation des dépendances Python...
    pip install -r python_scripts\requirements.txt
    echo.
) else (
    echo [OK] Dépendances Python déjà installées
    echo.
)

echo ========================================
echo Démarrage du serveur Symfony
echo ========================================
echo.
echo Le serveur sera accessible sur: http://localhost:8000
echo Appuyez sur Ctrl+C pour arrêter le serveur
echo.
echo.

REM Démarrer le serveur
php -S localhost:8000 -t public

pause


