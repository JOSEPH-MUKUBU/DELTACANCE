<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

class PredictionController extends AbstractController
{
    #[Route('/prediction', name: 'prediction', methods: ['GET', 'POST'])]
    public function index(Request $request): Response
    {
        $prediction = null;

        if ($request->isMethod('POST')) {
            $projectDir = dirname(__DIR__, 2);
            $scriptPath = $projectDir . '/python_scripts/predict.py';

            $data = $request->request->all();
            $jsonData = json_encode($data);
            $tempFile = tempnam(sys_get_temp_dir(), 'pred_');
            file_put_contents($tempFile, $jsonData);

            $output = [];
            $returnVar = 0;
            $command = "python \"$scriptPath\" \"$tempFile\" 2>&1";
            exec($command, $output, $returnVar);

            if ($returnVar === 0 && !empty($output)) {
                $outputString = implode('', $output);
                $prediction = json_decode($outputString, true) ?? ['error' => 'Parsing error'];

                // Sauvegarder dans l'historique
                if (!isset($prediction['error'])) {
                    $this->savePredictionToHistory($prediction, $data);
                }
            } else {
                $prediction = ['error' => 'Erreur lors de la prédiction'];
            }

            if (file_exists($tempFile)) {
                unlink($tempFile);
            }
        }

        return $this->render('prediction/index.html.twig', [
            'title' => 'Prédiction',
            'prediction' => $prediction
        ]);
    }

    private function savePredictionToHistory(array $prediction, array $inputData): void
    {
        $projectDir = dirname(__DIR__, 2);
        $scriptPath = $projectDir . '/python_scripts/report_generator.py';

        $historyData = [
            'prediction' => $prediction['prediction'] ?? null,
            'probability' => $prediction['probability'] ?? 0,
            'model' => $inputData['model'] ?? 'random_forest',
            'dataset' => $inputData['dataset'] ?? 'breast_cancer',
            'input_data' => $inputData
        ];

        $tempFile = tempnam(sys_get_temp_dir(), 'hist_');
        file_put_contents($tempFile, json_encode($historyData));

        exec("python \"$scriptPath\" save_history \"$tempFile\" 2>&1");

        if (file_exists($tempFile)) {
            unlink($tempFile);
        }
    }
}

