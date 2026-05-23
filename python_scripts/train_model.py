#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'entraînement des modèles ML
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import json
import sys
import os
import time
import joblib

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def train_model(model_name, dataset_name):
    """Entraîne un modèle ML"""
    
    # Charger le dataset préprocessé
    preprocessed_path = os.path.join(project_dir, 'python_scripts', f'preprocessed_{dataset_name}.csv')
    
    if not os.path.exists(preprocessed_path):
        # Si le fichier préprocessé n'existe pas, le créer
        from preprocessing import preprocess_dataset
        preprocess_dataset(dataset_name)
    
    df = pd.read_csv(preprocessed_path)
    
    # Définir la variable cible
    if dataset_name == 'breast_cancer':
        target_column = 'Status'
    elif dataset_name == 'cancer':
        target_column = 'Cancer Prediction Level'
    elif dataset_name == 'hybrid_cancer':
        target_column = 'Status'
    else:
        return {}
    
    # Séparer les features et la cible
    X = df.drop(columns=[target_column])
    y = df[target_column]
    
    # Diviser en train et test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Initialiser le modèle selon le type
    if model_name == 'random_forest':
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
    elif model_name == 'svm':
        model = SVC(
            kernel='rbf',
            C=1.0,
            gamma='scale',
            probability=True,
            random_state=42
        )
    elif model_name == 'neural_network':
        model = MLPClassifier(
            hidden_layer_sizes=(100, 50),
            activation='relu',
            solver='adam',
            alpha=0.0001,
            batch_size='auto',
            learning_rate='constant',
            learning_rate_init=0.001,
            max_iter=500,
            random_state=42,
            early_stopping=True,
            validation_fraction=0.1
        )
    else:
        return {}
    
    # Entraîner le modèle
    start_time = time.time()
    model.fit(X_train, y_train)
    training_time = time.time() - start_time
    
    # Prédictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None
    
    # Évaluation
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    results = {
        'model': model_name,
        'dataset': dataset_name,
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'confusion_matrix': cm,
        'training_time': float(training_time),
        'test_size': len(X_test),
        'train_size': len(X_train)
    }
    
    # Sauvegarder le modèle
    model_path = os.path.join(project_dir, 'python_scripts', f'model_{model_name}_{dataset_name}.joblib')
    joblib.dump(model, model_path)
    results['model_path'] = f'model_{model_name}_{dataset_name}.joblib'
    
    # Sauvegarder les résultats dans un fichier JSON global
    results_path = os.path.join(project_dir, 'python_scripts', 'results.json')
    all_results = {}
    if os.path.exists(results_path):
        with open(results_path, 'r') as f:
            all_results = json.load(f)
    
    key = f'{model_name}_{dataset_name}'
    all_results[key] = results
    
    with open(results_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    return results

if __name__ == '__main__':
    if len(sys.argv) > 2:
        model_name = sys.argv[1]
        dataset_name = sys.argv[2]
        result = train_model(model_name, dataset_name)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps({}, indent=2))


