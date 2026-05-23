# Script pour corriger l'erreur HTTP 500
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Correction de l'erreur HTTP 500" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Ajouter PHP au PATH
$env:Path = "C:\Program Files\PHP;$env:Path"

# Vérifier si vendor existe
if (-not (Test-Path "vendor")) {
    Write-Host "[ERREUR] Le dossier vendor n'existe pas!" -ForegroundColor Red
    Write-Host "Installation des dépendances Symfony..." -ForegroundColor Yellow
    Write-Host ""
    
    try {
        composer install --no-interaction
        Write-Host ""
        Write-Host "[OK] Dépendances installées" -ForegroundColor Green
    } catch {
        Write-Host "[ERREUR] Échec de l'installation des dépendances" -ForegroundColor Red
        Write-Host "Veuillez exécuter manuellement: composer install" -ForegroundColor Yellow
        Read-Host "`nAppuyez sur Entrée pour quitter"
        exit 1
    }
} else {
    Write-Host "[OK] Le dossier vendor existe" -ForegroundColor Green
}

# Créer le fichier .env s'il n'existe pas
if (-not (Test-Path ".env")) {
    Write-Host "Création du fichier .env..." -ForegroundColor Yellow
    @"
###> symfony/framework-bundle ###
APP_ENV=dev
APP_SECRET=change-this-secret-key-to-a-random-string-123456789
###< symfony/framework-bundle ###

###> symfony/twig-bundle ###
TWIG_DEFAULT_PATH=%kernel.project_dir%/templates
###< symfony/twig-bundle ###
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "[OK] Fichier .env créé" -ForegroundColor Green
} else {
    Write-Host "[OK] Le fichier .env existe" -ForegroundColor Green
}

# Vérifier si autoload existe
if (-not (Test-Path "vendor\autoload.php")) {
    Write-Host "[ERREUR] vendor\autoload.php n'existe pas!" -ForegroundColor Red
    Write-Host "Réinstallation des dépendances..." -ForegroundColor Yellow
    composer install --no-interaction
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Corrections terminées" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Vous pouvez maintenant relancer le serveur avec:" -ForegroundColor Yellow
Write-Host "  .\start.ps1" -ForegroundColor Cyan
Write-Host "ou" -ForegroundColor White
Write-Host "  php -S localhost:8000 -t public" -ForegroundColor Cyan
Write-Host ""

Read-Host "Appuyez sur Entrée pour continuer"


