@echo off
chcp 65001 >nul
echo ========================================
echo Correction de l'erreur HTTP 500
echo ========================================
echo.

REM Ajouter PHP et Composer au PATH
set PATH=C:\Program Files\PHP;%PATH%

REM Vérifier si vendor existe
if not exist "vendor" (
    echo [ERREUR] Le dossier vendor n'existe pas!
    echo Installation des dependances Symfony...
    echo.
    composer install
    echo.
    if errorlevel 1 (
        echo [ERREUR] Echec de l'installation des dependances
        echo Veuillez executer manuellement: composer install
        pause
        exit /b 1
    )
) else (
    echo [OK] Le dossier vendor existe
)

REM Créer le fichier .env s'il n'existe pas
if not exist ".env" (
    echo Creation du fichier .env...
    (
        echo ###^> symfony/framework-bundle ###
        echo APP_ENV=dev
        echo APP_SECRET=change-this-secret-key-to-a-random-string-123456789
        echo ###^< symfony/framework-bundle ###
        echo.
        echo ###^> symfony/twig-bundle ###
        echo TWIG_DEFAULT_PATH=%%kernel.project_dir%%/templates
        echo ###^< symfony/twig-bundle ###
    ) > .env
    echo [OK] Fichier .env cree
) else (
    echo [OK] Le fichier .env existe
)

echo.
echo ========================================
echo Corrections terminees
echo ========================================
echo.
echo Vous pouvez maintenant relancer le serveur avec:
echo   .\start.ps1
echo ou
echo   php -S localhost:8000 -t public
echo.
pause


