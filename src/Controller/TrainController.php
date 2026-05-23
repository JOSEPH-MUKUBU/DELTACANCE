<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

class TrainController extends AbstractController
{
    #[Route('/train', name: 'train')]
    public function index(): Response
    {
        return $this->render('train/index.html.twig', [
            'title' => 'Entraînement des Modèles ML',
            'models' => [
                'random_forest' => 'Random Forest',
                'svm' => 'Support Vector Machine',
                'neural_network' => 'Réseau de Neurones'
            ]
        ]);
    }
    
    #[Route('/train/{model}', name: 'train_model')]
    public function train(string $model, Request $request): Response
    {
        $projectDir = dirname(__DIR__, 2);
        $scriptPath = $projectDir . '/python_scripts/train_model.py';
        
        $dataset = $request->query->get('dataset', 'breast_cancer');
        
        $output = [];
        $returnVar = 0;
        exec("python \"$scriptPath\" \"$model\" \"$dataset\"", $output, $returnVar);
        
        $trainingData = [];
        if ($returnVar === 0 && !empty($output)) {
            $trainingData = json_decode(implode('', $output), true) ?? [];
        }
        
        if ($request->isXmlHttpRequest()) {
            return new JsonResponse($trainingData);
        }
        
        return $this->render('train/train_model.html.twig', [
            'title' => 'Entraînement: ' . $model,
            'model' => $model,
            'dataset' => $dataset,
            'training' => $trainingData
        ]);
    }
}

