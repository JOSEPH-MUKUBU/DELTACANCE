# Script PowerShell pour démarrer le projet
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Démarrage du projet Symfony" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Ajouter PHP au PATH pour cette session
$env:Path = "C:\Program Files\PHP;$env:Path"

# Vérifier PHP
try {
    $phpVersion = php -v 2>&1 | Select-Object -First 1
    Write-Host "[OK] PHP: $phpVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] PHP n'est pas trouvé dans C:\Program Files\PHP" -ForegroundColor Red
    Write-Host "Veuillez vérifier le chemin d'installation de PHP" -ForegroundColor Yellow
    Read-Host "`nAppuyez sur Entrée pour quitter"
    exit 1
}

# Vérifier Composer
try {
    $composerVersion = composer --version 2>&1 | Select-Object -First 1
    Write-Host "[OK] Composer: $composerVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] Composer n'est pas dans le PATH" -ForegroundColor Red
    Write-Host "Assurez-vous que Composer est installé et dans le PATH" -ForegroundColor Yellow
    Read-Host "`nAppuyez sur Entrée pour quitter"
    exit 1
}

Write-Host ""

# Vérifier et installer les dépendances Symfony
if (-not (Test-Path "vendor\autoload.php")) {
    Write-Host "Installation des dépendances Symfony..." -ForegroundColor Yellow
    composer install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERREUR] Échec de l'installation des dépendances" -ForegroundColor Red
        Read-Host "`nAppuyez sur Entrée pour quitter"
        exit 1
    }
    Write-Host ""
} else {
    Write-Host "[OK] Dépendances Symfony déjà installées" -ForegroundColor Green
    Write-Host ""
}

# Vérifier et installer les dépendances Python
try {
    $pythonInstalled = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonInstalled) {
        $pandasInstalled = python -m pip show pandas 2>&1 | Select-String "Name: pandas" -Quiet
        if (-not $pandasInstalled) {
            Write-Host "Installation des dépendances Python..." -ForegroundColor Yellow
            pip install -r python_scripts\requirements.txt
            Write-Host ""
        } else {
            Write-Host "[OK] Dépendances Python déjà installées" -ForegroundColor Green
            Write-Host ""
        }
    }
} catch {
    Write-Host "[INFO] Python n'est pas installé (optionnel pour certaines fonctionnalités)" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Démarrage du serveur Symfony" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Le serveur sera accessible sur: " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur" -ForegroundColor Yellow
Write-Host ""

# Démarrer le serveur
php -S localhost:8000 -t public
