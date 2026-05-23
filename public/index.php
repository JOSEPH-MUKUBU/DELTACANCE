<?php

use App\Kernel;

require_once dirname(__DIR__).'/vendor/autoload_runtime.php';

return function (array $context) {
    // Valeurs par défaut si non définies
    $appEnv = $context['APP_ENV'] ?? 'dev';
    $appDebug = isset($context['APP_DEBUG']) ? (bool) $context['APP_DEBUG'] : true;
    
    return new Kernel($appEnv, $appDebug);
};

