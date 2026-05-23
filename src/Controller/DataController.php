<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

class DataController extends AbstractController
{
    #[Route('/data', name: 'data_index')]
    public function index(): Response
    {
        // Redirige vers le premier dataset par défaut
        return $this->redirectToRoute('data_view', ['dataset' => 'breast_cancer']);
    }

    #[Route('/data/{dataset}', name: 'data_view')]
    public function view(string $dataset, Request $request): Response
    {
        $projectDir = dirname(__DIR__, 2);
        $scriptPath = $projectDir . '/python_scripts/dataset_info.py';

        $operation = $request->query->get('operation');

        if ($operation && in_array($operation, ['tail', 'columns', 'info', 'describe', 'sample', 'dtypes', 'isnull'])) {
            // Mode Opération Spécifique
            $command = "python \"$scriptPath\" operation \"$dataset\" \"$operation\" 2>&1";
        } else {
            // Mode Prévisualisation par défaut (head)
            $limit = $request->query->getInt('limit', 100);
            $limit = min(max($limit, 10), 5000);
            $command = "python \"$scriptPath\" preview \"$dataset\" $limit 2>&1";
        }

        $output = [];
        $returnVar = 0;
        exec($command, $output, $returnVar);

        $data = [];
        if ($returnVar === 0 && !empty($output)) {
            $jsonString = implode('', $output);
            $data = json_decode($jsonString, true);
            if (json_last_error() !== JSON_ERROR_NONE) {
                $data = ['error' => 'Erreur JSON: ' . json_last_error_msg() . '. Raw: ' . substr($jsonString, 0, 100) . '...'];
            }
        } else {
            $data = ['error' => 'Erreur lors de l\'exécution du script: ' . implode("\n", $output)];
        }

        return $this->render('data/index.html.twig', [
            'title' => 'Explorateur de Données',
            'current_dataset' => $dataset,
            'limit' => $request->query->getInt('limit', 100),
            'current_operation' => $operation ?? 'head',
            'data' => $data,
            'datasets' => [
                'breast_cancer' => 'Breast Cancer Dataset',
                'cancer' => 'Cancer Risk Dataset',
                'hybrid_cancer' => 'Hybrid Dataset (Fusion)'
            ]
        ]);
    }
}
