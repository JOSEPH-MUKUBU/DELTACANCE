<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

class PreprocessingController extends AbstractController
{
    #[Route('/preprocessing', name: 'preprocessing')]
    public function index(): Response
    {
        return $this->render('preprocessing/index.html.twig', [
            'title' => 'Nettoyage et Préparation des Données'
        ]);
    }
    
    #[Route('/preprocessing/{dataset}', name: 'preprocess_dataset')]
    public function preprocess(string $dataset, Request $request): Response
    {
        $projectDir = dirname(__DIR__, 2);
        $scriptPath = $projectDir . '/python_scripts/preprocessing.py';
        
        $output = [];
        $returnVar = 0;
        exec("python \"$scriptPath\" \"$dataset\"", $output, $returnVar);
        
        $preprocessingData = [];
        if ($returnVar === 0 && !empty($output)) {
            $preprocessingData = json_decode(implode('', $output), true) ?? [];
        }
        
        if ($request->isXmlHttpRequest()) {
            return new JsonResponse($preprocessingData);
        }
        
        return $this->render('preprocessing/preprocess.html.twig', [
            'title' => 'Préprocessing: ' . $dataset,
            'dataset' => $dataset,
            'preprocessing' => $preprocessingData
        ]);
    }
}

