<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

class AnalysisController extends AbstractController
{
    #[Route('/analysis', name: 'analysis')]
    public function index(): Response
    {
        return $this->render('analysis/index.html.twig', [
            'title' => 'Analyse des Datasets'
        ]);
    }

    #[Route('/analysis/{dataset}', name: 'analysis_dataset')]
    public function analyze(string $dataset, Request $request): Response
    {
        set_time_limit(300); // Augmenter le temps d'exécution à 5 minutes

        $projectDir = dirname(__DIR__, 2);
        $scriptPath = $projectDir . '/python_scripts/data_analysis.py';

        $output = [];
        $returnVar = 0;
        $errorOutput = [];

        // Use Python with full path or try python command
        $command = "python \"$scriptPath\" \"$dataset\" 2>&1";
        exec($command, $output, $returnVar);

        $analysisData = [];
        if ($returnVar === 0 && !empty($output)) {
            $outputString = implode('', $output);
            $analysisData = json_decode($outputString, true) ?? [];
        }

        // Log execution details for debugging
        error_log("Python Execution - Dataset: $dataset, Return Code: $returnVar, Output Lines: " . count($output));
        if (!empty($output)) {
            error_log("Output Sample: " . substr(implode('', $output), 0, 100));
        }

        if ($request->isXmlHttpRequest()) {
            return new JsonResponse($analysisData);
        }

        return $this->render('analysis/analyze.html.twig', [
            'title' => 'Analyse du Dataset: ' . $dataset,
            'dataset' => $dataset,
            'analysis' => $analysisData
        ]);
    }
}

