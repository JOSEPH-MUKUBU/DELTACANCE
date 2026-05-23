# Script d'installation PowerShell pour PHP, Composer et dependances du projet
# Executez ce script en tant qu'administrateur

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation PHP, Composer et Symfony" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verifier si le script est execute en tant qu'administrateur
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERREUR : Ce script doit etre execute en tant qu'administrateur!" -ForegroundColor Red
    Write-Host "Fermez PowerShell, faites clic droit et selectionnez 'Executer en tant qu'administrateur'" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entree pour quitter"
    exit 1
}

# Verifier si Chocolatey est installe
Write-Host "Verification de Chocolatey..." -ForegroundColor Yellow
$chocoInstalled = Get-Command choco -ErrorAction SilentlyContinue

if (-not $chocoInstalled) {
    Write-Host "Chocolatey n'est pas installe. Installation..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    
    # Rafraichir l'environnement
    $env:ChocolateyInstall = Convert-Path "$((Get-Command choco).Path)\..\.."
    Import-Module "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1"
    refreshenv
} else {
    Write-Host "Chocolatey est deja installe." -ForegroundColor Green
}

# Verifier et installer PHP
Write-Host "`nVerification de PHP..." -ForegroundColor Yellow
$phpInstalled = Get-Command php -ErrorAction SilentlyContinue

if (-not $phpInstalled) {
    Write-Host "Installation de PHP..." -ForegroundColor Yellow
    choco install php -y
    
    # Rafraichir l'environnement
    refreshenv
} else {
    Write-Host "PHP est deja installe :" -ForegroundColor Green
    php -v
}

# Verifier et installer Composer
Write-Host "`nVerification de Composer..." -ForegroundColor Yellow
$composerInstalled = Get-Command composer -ErrorAction SilentlyContinue

if (-not $composerInstalled) {
    Write-Host "Installation de Composer..." -ForegroundColor Yellow
    choco install composer -y
    
    # Rafraichir l'environnement
    refreshenv
} else {
    Write-Host "Composer est deja installe :" -ForegroundColor Green
    composer --version
}

# Installer les dependances du projet
Write-Host "`nInstallation des dependances Symfony..." -ForegroundColor Yellow
$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path

if (Test-Path "$projectPath\composer.json") {
    Set-Location $projectPath
    Write-Host "Execution de: composer install" -ForegroundColor Cyan
    composer install
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nOK - Dependances Symfony installees avec succes!" -ForegroundColor Green
    } else {
        Write-Host "`nERREUR - Erreur lors de l'installation des dependances" -ForegroundColor Red
    }
} else {
    Write-Host "composer.json non trouve dans $projectPath" -ForegroundColor Red
}

# Installer les dependances Python
Write-Host "`nInstallation des dependances Python..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    if (Test-Path "$projectPath\python_scripts\requirements.txt") {
        Write-Host "Execution de: pip install -r python_scripts/requirements.txt" -ForegroundColor Cyan
        pip install -r "$projectPath\python_scripts\requirements.txt"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`nOK - Dependances Python installees avec succes!" -ForegroundColor Green
        } else {
            Write-Host "`nERREUR - Erreur lors de l'installation des dependances Python" -ForegroundColor Red
        }
    } else {
        Write-Host "requirements.txt non trouve" -ForegroundColor Yellow
    }
} else {
    Write-Host "Python n'est pas installe. Installez-le manuellement." -ForegroundColor Yellow
}

# Resume
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Installation terminee!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Verifications:" -ForegroundColor Yellow
Write-Host "  - PHP: " -NoNewline
if (Get-Command php -ErrorAction SilentlyContinue) {
    Write-Host "OK - Installe" -ForegroundColor Green
    php -v | Select-Object -First 1
} else {
    Write-Host "ERREUR - Non trouve (redemarrez le terminal)" -ForegroundColor Red
}

Write-Host "  - Composer: " -NoNewline
if (Get-Command composer -ErrorAction SilentlyContinue) {
    Write-Host "OK - Installe" -ForegroundColor Green
    composer --version
} else {
    Write-Host "ERREUR - Non trouve (redemarrez le terminal)" -ForegroundColor Red
}

Write-Host "`nPour demarrer le serveur Symfony:" -ForegroundColor Cyan
Write-Host "  php -S localhost:8000 -t public" -ForegroundColor White

Read-Host "`nAppuyez sur Entree pour quitter"
