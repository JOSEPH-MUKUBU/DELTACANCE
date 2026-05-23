<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

class CompareController extends AbstractController
{
    #[Route('/compare', name: 'compare')]
    public function index(): Response
    {
        $projectDir = dirname(__DIR__, 2);
        $resultsPath = $projectDir . '/python_scripts/results.json';
        
        $results = [];
        if (file_exists($resultsPath)) {
            $results = json_decode(file_get_contents($resultsPath), true) ?? [];
        }
        
        return $this->render('compare/index.html.twig', [
            'title' => 'Comparaison des Modèles',
            'results' => $results
        ]);
    }
}

