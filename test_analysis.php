<?php
/**
 * Test script to verify analysis data generation
 */

$projectDir = __DIR__;
$scriptPath = $projectDir . '/python_scripts/data_analysis.py';

echo "Testing Python Analysis Script\n";
echo "================================\n\n";

// Test 1: Check if script exists
echo "1. Checking if script exists: " . (file_exists($scriptPath) ? "✓ YES" : "✗ NO") . "\n";

// Test 2: Try to execute for breast_cancer dataset
echo "2. Running analysis for breast_cancer dataset...\n\n";

$output = [];
$returnVar = 0;
$command = "python \"$scriptPath\" \"breast_cancer\" 2>&1";

echo "Command: $command\n\n";

exec($command, $output, $returnVar);

echo "Return Code: $returnVar\n";
echo "Output Lines: " . count($output) . "\n\n";

if (!empty($output)) {
    $outputStr = implode("\n", $output);
    
    // Try to parse as JSON
    $json = json_decode($outputStr, true);
    
    if ($json) {
        echo "✓ JSON parsing successful!\n";
        echo "\nTop-level keys:\n";
        foreach (array_keys($json) as $key) {
            echo "  - $key\n";
        }
        
        if (isset($json['plots'])) {
            echo "\nPlots found: " . count($json['plots']) . "\n";
            echo "Plot keys:\n";
            foreach (array_keys($json['plots']) as $key) {
                echo "  - $key\n";
            }
        }
    } else {
        echo "✗ JSON parsing failed!\n";
        echo "First 500 chars of output:\n";
        echo substr($outputStr, 0, 500) . "\n";
    }
} else {
    echo "✗ No output from script\n";
}

echo "\n3. Checking for common issues:\n";

// Check Python installation
$pythonCheck = [];
exec("python --version 2>&1", $pythonCheck);
echo "  Python: " . implode(" ", $pythonCheck) . "\n";

// Check if required modules are available
$modulesCheck = [];
exec("python -c \"import pandas, numpy, matplotlib, seaborn; print('All modules OK')\" 2>&1", $modulesCheck);
echo "  Modules: " . implode(" ", $modulesCheck) . "\n";

// Check dataset files
$brealtCancerCsv = $projectDir . '/Breast_Cancer.csv';
$cancerCsv = $projectDir . '/Cancer_Dataset.csv';

echo "\n4. Checking dataset files:\n";
echo "  Breast_Cancer.csv: " . (file_exists($brealtCancerCsv) ? "✓ YES" : "✗ NO") . "\n";
echo "  Cancer_Dataset.csv: " . (file_exists($cancerCsv) ? "✓ YES" : "✗ NO") . "\n";

if (file_exists($brealtCancerCsv)) {
    $lines = count(file($brealtCancerCsv));
    echo "    Rows: $lines\n";
}

echo "\nDone.\n";
?>
