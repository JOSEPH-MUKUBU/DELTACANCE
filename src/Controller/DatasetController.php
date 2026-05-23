<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

class DatasetController extends AbstractController
{
    #[Route('/dataset', name: 'dataset')]
    public function index(): Response
    {
        // Exécuter le script Python pour obtenir les informations sur les datasets
        $datasetsInfo = $this->getDatasetsInfo();
        
        return $this->render('dataset/index.html.twig', [
            'title' => 'Description des Datasets',
            'datasets' => $datasetsInfo
        ]);
    }
    
    private function getDatasetsInfo(): array
    {
        $projectDir = dirname(__DIR__, 2);
        $scriptPath = $projectDir . '/python_scripts/dataset_info.py';
        
        $output = [];
        $returnVar = 0;
        exec("python \"$scriptPath\"", $output, $returnVar);
        
        if ($returnVar === 0 && !empty($output)) {
            return json_decode(implode('', $output), true) ?? [];
        }
        
        return [
            'breast_cancer' => [
                'name' => 'Breast Cancer Dataset',
                'file' => 'Breast_Cancer.csv',
                'description' => 'Dataset sur le cancer du sein avec caractéristiques cliniques et pathologiques'
            ],
            'cancer' => [
                'name' => 'Cancer Dataset',
                'file' => 'Cancer_Dataset.csv',
                'description' => 'Dataset sur les patients avec facteurs de risque et niveau de prédiction'
            ]
        ];
    }
}

