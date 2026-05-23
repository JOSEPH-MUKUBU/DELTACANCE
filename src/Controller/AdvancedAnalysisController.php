<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

class AdvancedAnalysisController extends AbstractController
{
    #[Route('/advanced', name: 'advanced_analysis')]
    public function index(): Response
    {
        return $this->render('advanced/index.html.twig', [
            'title' => 'Analyse Avancée',
            'datasets' => [
                'breast_cancer' => 'Breast Cancer',
                'cancer' => 'Cancer Risk',
                'hybrid_cancer' => 'Hybrid Dataset (New)'
            ],
            'models' => ['random_forest' => 'Random Forest', 'svm' => 'SVM', 'neural_network' => 'Neural Network']
        ]);
    }

    private function runPythonAnalysis(string $action, string $dataset, string $model = 'random_forest'): array
    {
        $projectDir = dirname(__DIR__, 2);
        $scriptPath = $projectDir . '/python_scripts/advanced_analysis.py';

        $output = [];
        $returnVar = 0;
        $command = "python \"$scriptPath\" $action \"$dataset\" \"$model\" 2>&1";
        exec($command, $output, $returnVar);

        if ($returnVar === 0 && !empty($output)) {
            $outputString = implode('', $output);
            return json_decode($outputString, true) ?? [];
        }
        return ['error' => 'Erreur lors de l\'exécution du script Python.'];
    }

    #[Route('/advanced/importance/{dataset}', name: 'feature_importance')]
    public function featureImportance(string $dataset, Request $request): Response
    {
        $analysisData = $this->runPythonAnalysis('importance', $dataset);

        if ($request->isXmlHttpRequest()) {
            return new JsonResponse($analysisData);
        }

        return $this->render('advanced/importance.html.twig', [
            'title' => 'Feature Importance - ' . ucwords(str_replace('_', ' ', $dataset)),
            'dataset' => $dataset,
            'analysis' => $analysisData
        ]);
    }

    #[Route('/advanced/roc/{dataset}/{model}', name: 'roc_curves', defaults: ['model' => 'random_forest'])]
    public function rocCurves(string $dataset, string $model, Request $request): Response
    {
        $analysisData = $this->runPythonAnalysis('roc', $dataset, $model);

        if ($request->isXmlHttpRequest()) {
            return new JsonResponse($analysisData);
        }

        return $this->render('advanced/roc.html.twig', [
            'title' => 'Courbes ROC - ' . ucwords(str_replace('_', ' ', $model)),
            'dataset' => $dataset,
            'model' => $model,
            'analysis' => $analysisData,
            'models' => ['random_forest' => 'Random Forest', 'svm' => 'SVM', 'neural_network' => 'Neural Network']
        ]);
    }

    #[Route('/advanced/confusion/{dataset}/{model}', name: 'confusion_matrix', defaults: ['model' => 'random_forest'])]
    public function confusionMatrix(string $dataset, string $model, Request $request): Response
    {
        $analysisData = $this->runPythonAnalysis('confusion', $dataset, $model);

        if ($request->isXmlHttpRequest()) {
            return new JsonResponse($analysisData);
        }

        return $this->render('advanced/confusion.html.twig', [
            'title' => 'Matrice de Confusion - ' . ucwords(str_replace('_', ' ', $model)),
            'dataset' => $dataset,
            'model' => $model,
            'analysis' => $analysisData,
            'models' => ['random_forest' => 'Random Forest', 'svm' => 'SVM', 'neural_network' => 'Neural Network']
        ]);
    }

    #[Route('/advanced/crossval/{dataset}/{model}', name: 'cross_validation', defaults: ['model' => 'random_forest'])]
    public function crossValidation(string $dataset, string $model, Request $request): Response
    {
        $analysisData = $this->runPythonAnalysis('crossval', $dataset, $model);

        if ($request->isXmlHttpRequest()) {
            return new JsonResponse($analysisData);
        }

        return $this->render('advanced/crossval.html.twig', [
            'title' => 'Validation Croisée - ' . ucwords(str_replace('_', ' ', $model)),
            'dataset' => $dataset,
            'model' => $model,
            'analysis' => $analysisData,
            'models' => ['random_forest' => 'Random Forest', 'svm' => 'SVM', 'neural_network' => 'Neural Network']
        ]);
    }

    #[Route('/advanced/learning/{dataset}/{model}', name: 'learning_curves', defaults: ['model' => 'random_forest'])]
    public function learningCurves(string $dataset, string $model, Request $request): Response
    {
        $analysisData = $this->runPythonAnalysis('learning', $dataset, $model);

        if ($request->isXmlHttpRequest()) {
            return new JsonResponse($analysisData);
        }

        return $this->render('advanced/learning.html.twig', [
            'title' => 'Courbes d\'Apprentissage - ' . ucwords(str_replace('_', ' ', $model)),
            'dataset' => $dataset,
            'model' => $model,
            'analysis' => $analysisData,
            'models' => ['random_forest' => 'Random Forest', 'svm' => 'SVM', 'neural_network' => 'Neural Network']
        ]);
    }
}
