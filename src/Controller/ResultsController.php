<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

class ResultsController extends AbstractController
{
    #[Route('/results', name: 'results')]
    public function index(Request $request): Response
    {
        $projectDir = dirname(__DIR__, 2);
        $resultsPath = $projectDir . '/python_scripts/results.json';

        $results = [];
        if (file_exists($resultsPath)) {
            $results = json_decode(file_get_contents($resultsPath), true) ?? [];
        }

        if ($request->isXmlHttpRequest()) {
            return new JsonResponse($results);
        }

        return $this->render('results/index.html.twig', [
            'title' => 'Résultats des Modèles',
            'results' => $results
        ]);
    }
}

