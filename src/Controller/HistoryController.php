<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\BinaryFileResponse;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\ResponseHeaderBag;
use Symfony\Component\Routing\Annotation\Route;

class HistoryController extends AbstractController
{
    private function runPythonScript(string $action, ?string $dataFile = null): array
    {
        $projectDir = dirname(__DIR__, 2);
        $scriptPath = $projectDir . '/python_scripts/report_generator.py';

        $command = "python \"$scriptPath\" $action";
        if ($dataFile) {
            $command .= " \"$dataFile\"";
        }
        $command .= " 2>&1";

        $output = [];
        $returnVar = 0;
        exec($command, $output, $returnVar);

        $outputString = implode("\n", $output);

        if (!empty($outputString)) {
            $result = json_decode($outputString, true);
            if ($result !== null) {
                return $result;
            }
        }

        // Fallback pour get_history si erreur
        if ($action === 'get_history') {
            return ['history' => [], 'count' => 0];
        }

        return ['error' => 'Python error (code ' . $returnVar . '): ' . substr($outputString, 0, 500)];
    }

    #[Route('/history', name: 'prediction_history')]
    public function index(): Response
    {
        $history = $this->runPythonScript('get_history');

        return $this->render('history/index.html.twig', [
            'title' => 'Historique des Prédictions',
            'history' => $history['history'] ?? [],
            'count' => $history['count'] ?? 0
        ]);
    }

    #[Route('/history/clear', name: 'clear_history', methods: ['POST'])]
    public function clearHistory(): JsonResponse
    {
        $result = $this->runPythonScript('clear_history');
        return new JsonResponse($result, 200, [], JSON_UNESCAPED_UNICODE);
    }

    #[Route('/history/export', name: 'export_history')]
    public function exportHistory(): Response
    {
        $history = $this->runPythonScript('get_history');

        // Export as CSV with UTF-8 BOM for Excel compatibility
        $csv = "\xEF\xBB\xBF"; // UTF-8 BOM
        $csv .= "ID,Date,Dataset,Modele,Prediction,Probabilite\n";
        foreach ($history['history'] ?? [] as $entry) {
            $csv .= sprintf(
                "%d,%s,%s,%s,%s,%.1f%%\n",
                $entry['id'],
                $entry['timestamp'],
                $entry['dataset'] ?? 'N/A',
                $entry['model'] ?? 'N/A',
                $entry['prediction'] ?? 'N/A',
                ($entry['probability'] ?? 0) * 100
            );
        }

        $response = new Response($csv);
        $response->headers->set('Content-Type', 'text/csv; charset=UTF-8');
        $response->headers->set('Content-Disposition', 'attachment; filename="historique_predictions.csv"');

        return $response;
    }

    #[Route('/report/generate', name: 'generate_report', methods: ['POST'])]
    public function generateReport(Request $request): Response
    {
        $data = $request->request->all();

        // Decode input_data if it's a JSON string
        if (isset($data['input_data']) && is_string($data['input_data'])) {
            $data['input_data'] = json_decode($data['input_data'], true) ?? [];
        }

        $projectDir = dirname(__DIR__, 2);
        $tempFile = tempnam(sys_get_temp_dir(), 'report_');
        file_put_contents($tempFile, json_encode($data, JSON_UNESCAPED_UNICODE));

        $result = $this->runPythonScript('generate_pdf', $tempFile);

        if (file_exists($tempFile)) {
            unlink($tempFile);
        }

        if (isset($result['success']) && $result['success'] && isset($result['path'])) {
            if (file_exists($result['path'])) {
                $response = new BinaryFileResponse($result['path']);
                $response->setContentDisposition(
                    ResponseHeaderBag::DISPOSITION_ATTACHMENT,
                    $result['filename']
                );
                return $response;
            }
        }

        // Return plain Response instead of JsonResponse to avoid encoding issues
        $errorMsg = $result['error'] ?? 'Erreur de generation PDF';
        return new Response(
            '<html><body><h2>Erreur</h2><p>' . htmlspecialchars($errorMsg, ENT_QUOTES, 'UTF-8') . '</p><a href="javascript:history.back()">Retour</a></body></html>',
            500,
            ['Content-Type' => 'text/html; charset=UTF-8']
        );
    }

    #[Route('/api/save-prediction', name: 'save_prediction', methods: ['POST'])]
    public function savePrediction(Request $request): JsonResponse
    {
        $data = json_decode($request->getContent(), true) ?? $request->request->all();

        $projectDir = dirname(__DIR__, 2);
        $tempFile = tempnam(sys_get_temp_dir(), 'pred_');
        file_put_contents($tempFile, json_encode($data, JSON_UNESCAPED_UNICODE));

        $result = $this->runPythonScript('save_history', $tempFile);

        if (file_exists($tempFile)) {
            unlink($tempFile);
        }

        return new JsonResponse($result, 200, [], JSON_UNESCAPED_UNICODE);
    }
}
