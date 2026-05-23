#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour générer les visualisations avancées:
- Feature Importance
- Courbes ROC
- Matrice de Confusion
- Validation Croisée (K-Fold)
- Courbes d'Apprentissage
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split, cross_val_score, learning_curve
from sklearn.metrics import roc_curve, auc, confusion_matrix, classification_report
from sklearn.preprocessing import LabelEncoder, label_binarize
import json
import sys
import os
import base64
from io import BytesIO
import joblib

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_plot_base64():
    """Convertit le plot courant en base64"""
    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()
    return plot_url

def get_feature_importance(dataset_name):
    """Calcule et visualise l'importance des features avec Random Forest"""
    
    # Charger le dataset préprocessé
    preprocessed_path = os.path.join(project_dir, 'python_scripts', f'preprocessed_{dataset_name}.csv')
    
    if not os.path.exists(preprocessed_path):
        return {'error': 'Dataset préprocessé non trouvé. Veuillez d\'abord exécuter le preprocessing.'}
    
    df = pd.read_csv(preprocessed_path)
    
    # Définir la cible et les classes
    if dataset_name == 'breast_cancer' or dataset_name == 'hybrid_cancer':
        target_column = 'Status'
        classes = ['Alive', 'Dead']
    else:
        target_column = 'Cancer Prediction Level'
        classes = ['Low', 'Medium', 'High']
    if target_column not in df.columns:
        return {'error': f'Colonne cible {target_column} non trouvée.'}
    
    X = df.drop(columns=[target_column])
    y = df[target_column]
    
    # Entraîner un Random Forest pour obtenir les importances
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X, y)
    
    # Récupérer les importances
    importances = rf.feature_importances_
    feature_names = X.columns.tolist()
    
    # Trier par importance
    indices = np.argsort(importances)[::-1]
    sorted_features = [feature_names[i] for i in indices]
    sorted_importances = [importances[i] for i in indices]
    
    # Créer le graphique
    plt.figure(figsize=(12, 8))
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(sorted_features)))
    bars = plt.barh(range(len(sorted_features)), sorted_importances[::-1], color=colors)
    plt.yticks(range(len(sorted_features)), sorted_features[::-1])
    plt.xlabel('Importance', fontsize=12)
    plt.ylabel('Features', fontsize=12)
    plt.title(f'Feature Importance - {dataset_name.replace("_", " ").title()}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    plot_base64 = get_plot_base64()
    
    # Préparer les données pour le retour
    importance_data = [
        {'feature': f, 'importance': round(imp * 100, 2)}
        for f, imp in zip(sorted_features, sorted_importances)
    ]
    
    return {
        'plot': plot_base64,
        'data': importance_data,
        'dataset': dataset_name,
        'top_features': sorted_features[:5]
    }


def get_roc_curves(dataset_name, model_name='random_forest'):
    """Génère les courbes ROC pour un modèle donné"""
    
    preprocessed_path = os.path.join(project_dir, 'python_scripts', f'preprocessed_{dataset_name}.csv')
    
    if not os.path.exists(preprocessed_path):
        return {'error': 'Dataset préprocessé non trouvé.'}
    
    df = pd.read_csv(preprocessed_path)
    
    # Définir la cible
    if dataset_name == 'breast_cancer':
        target_column = 'Status'
    else:
        target_column = 'Cancer Prediction Level'
    
    X = df.drop(columns=[target_column])
    y = df[target_column]
    
    # Charger le modèle entraîné
    model_path = os.path.join(project_dir, 'python_scripts', f'model_{model_name}_{dataset_name}.joblib')
    
    if os.path.exists(model_path):
        model = joblib.load(model_path)
    else:
        # Si pas de modèle, en entraîner un
        if model_name == 'random_forest':
            model = RandomForestClassifier(n_estimators=100, random_state=42)
        else:
            return {'error': f'Modèle {model_name} non trouvé.'}
        model.fit(X, y)
    
    # Split pour évaluation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Obtenir les probabilités
    y_score = model.predict_proba(X_test)
    
    # Binariser les classes pour ROC multiclasse
    classes = np.unique(y)
    n_classes = len(classes)
    y_test_bin = label_binarize(y_test, classes=classes)
    
    # Calculer ROC pour chaque classe
    plt.figure(figsize=(10, 8))
    
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#9b59b6', '#f39c12']
    auc_scores = {}
    
    if n_classes == 2:
        # Cas binaire
        fpr, tpr, _ = roc_curve(y_test_bin.ravel(), y_score[:, 1])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, color=colors[0], lw=2, label=f'ROC (AUC = {roc_auc:.3f})')
        auc_scores['global'] = round(roc_auc, 3)
    else:
        # Cas multiclasse
        for i, (cls, color) in enumerate(zip(classes, colors[:n_classes])):
            if y_test_bin.shape[1] > i:
                fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_score[:, i])
                roc_auc = auc(fpr, tpr)
                plt.plot(fpr, tpr, color=color, lw=2, label=f'Classe {cls} (AUC = {roc_auc:.3f})')
                auc_scores[str(cls)] = round(roc_auc, 3)
    
    # Ligne de référence (random classifier)
    plt.plot([0, 1], [0, 1], 'k--', lw=1, label='Random (AUC = 0.5)')
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Taux de Faux Positifs (FPR)', fontsize=12)
    plt.ylabel('Taux de Vrais Positifs (TPR)', fontsize=12)
    plt.title(f'Courbes ROC - {model_name.replace("_", " ").title()} sur {dataset_name.replace("_", " ").title()}', 
              fontsize=14, fontweight='bold')
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plot_base64 = get_plot_base64()
    
    return {
        'plot': plot_base64,
        'auc_scores': auc_scores,
        'dataset': dataset_name,
        'model': model_name,
        'n_classes': n_classes
    }


def get_model(model_name, dataset_name):
    """Charge ou crée un modèle"""
    model_path = os.path.join(project_dir, 'python_scripts', f'model_{model_name}_{dataset_name}.joblib')
    
    if os.path.exists(model_path):
        return joblib.load(model_path)
    
    # Créer un nouveau modèle si non trouvé
    if model_name == 'random_forest':
        return RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    elif model_name == 'svm':
        return SVC(kernel='rbf', probability=True, random_state=42)
    elif model_name == 'neural_network':
        return MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
    else:
        return RandomForestClassifier(n_estimators=100, random_state=42)


def get_confusion_matrix(dataset_name, model_name='random_forest'):
    """Génère la matrice de confusion pour un modèle"""
    
    preprocessed_path = os.path.join(project_dir, 'python_scripts', f'preprocessed_{dataset_name}.csv')
    
    if not os.path.exists(preprocessed_path):
        return {'error': 'Dataset préprocessé non trouvé.'}
    
    df = pd.read_csv(preprocessed_path)
    
    # Définir la cible
    if dataset_name == 'breast_cancer':
        target_column = 'Status'
    else:
        target_column = 'Cancer Prediction Level'
    
    X = df.drop(columns=[target_column])
    y = df[target_column]
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Charger ou entraîner le modèle
    model = get_model(model_name, dataset_name)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    # Calculer la matrice de confusion
    cm = confusion_matrix(y_test, y_pred)
    classes = np.unique(y)
    
    # Créer le graphique
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=classes, yticklabels=classes)
    plt.xlabel('Prédiction', fontsize=12)
    plt.ylabel('Réalité', fontsize=12)
    plt.title(f'Matrice de Confusion - {model_name.replace("_", " ").title()}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    plot_base64 = get_plot_base64()
    
    # Rapport de classification
    report = classification_report(y_test, y_pred, output_dict=True)
    
    return {
        'plot': plot_base64,
        'matrix': cm.tolist(),
        'classes': classes.tolist() if hasattr(classes, 'tolist') else list(classes),
        'report': report,
        'dataset': dataset_name,
        'model': model_name
    }


def get_cross_validation(dataset_name, model_name='random_forest', cv=5):
    """Effectue une validation croisée K-Fold"""
    
    preprocessed_path = os.path.join(project_dir, 'python_scripts', f'preprocessed_{dataset_name}.csv')
    
    if not os.path.exists(preprocessed_path):
        return {'error': 'Dataset préprocessé non trouvé.'}
    
    df = pd.read_csv(preprocessed_path)
    
    if dataset_name == 'breast_cancer' or dataset_name == 'hybrid_cancer':
        target_column = 'Status'
    else:
        target_column = 'Cancer Prediction Level'
    
    X = df.drop(columns=[target_column])
    y = df[target_column]
    
    model = get_model(model_name, dataset_name)
    
    # Cross-validation pour différentes métriques
    scoring_metrics = ['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted']
    results = {}
    
    for metric in scoring_metrics:
        scores = cross_val_score(model, X, y, cv=cv, scoring=metric)
        results[metric] = {
            'scores': scores.tolist(),
            'mean': round(scores.mean() * 100, 2),
            'std': round(scores.std() * 100, 2)
        }
    
    # Graphique des scores par fold
    plt.figure(figsize=(12, 6))
    
    x = np.arange(cv)
    width = 0.2
    colors = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6']
    
    for i, (metric, data) in enumerate(results.items()):
        offset = (i - 1.5) * width
        bars = plt.bar(x + offset, [s * 100 for s in data['scores']], width, 
                      label=metric.replace('_', ' ').title(), color=colors[i], alpha=0.8)
    
    plt.xlabel('Fold', fontsize=12)
    plt.ylabel('Score (%)', fontsize=12)
    plt.title(f'Validation Croisée {cv}-Fold - {model_name.replace("_", " ").title()}', fontsize=14, fontweight='bold')
    plt.xticks(x, [f'Fold {i+1}' for i in range(cv)])
    plt.legend(loc='lower right')
    plt.ylim(0, 110)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    
    plot_base64 = get_plot_base64()
    
    return {
        'plot': plot_base64,
        'results': results,
        'cv': cv,
        'dataset': dataset_name,
        'model': model_name
    }


def get_learning_curves(dataset_name, model_name='random_forest'):
    """Génère les courbes d'apprentissage"""
    
    preprocessed_path = os.path.join(project_dir, 'python_scripts', f'preprocessed_{dataset_name}.csv')
    
    if not os.path.exists(preprocessed_path):
        return {'error': 'Dataset préprocessé non trouvé.'}
    
    df = pd.read_csv(preprocessed_path)
    
    if dataset_name == 'breast_cancer' or dataset_name == 'hybrid_cancer':
        target_column = 'Status'
    else:
        target_column = 'Cancer Prediction Level'
    
    X = df.drop(columns=[target_column])
    y = df[target_column]
    
    model = get_model(model_name, dataset_name)
    
    # Calculer les courbes d'apprentissage
    train_sizes, train_scores, test_scores = learning_curve(
        model, X, y, cv=5, n_jobs=-1,
        train_sizes=np.linspace(0.1, 1.0, 10),
        scoring='accuracy'
    )
    
    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    test_mean = np.mean(test_scores, axis=1)
    test_std = np.std(test_scores, axis=1)
    
    # Créer le graphique
    plt.figure(figsize=(10, 6))
    
    plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.1, color='#3498db')
    plt.fill_between(train_sizes, test_mean - test_std, test_mean + test_std, alpha=0.1, color='#e74c3c')
    
    plt.plot(train_sizes, train_mean, 'o-', color='#3498db', label='Score d\'entraînement')
    plt.plot(train_sizes, test_mean, 'o-', color='#e74c3c', label='Score de validation')
    
    plt.xlabel('Taille du jeu d\'entraînement', fontsize=12)
    plt.ylabel('Accuracy', fontsize=12)
    plt.title(f'Courbes d\'Apprentissage - {model_name.replace("_", " ").title()}', fontsize=14, fontweight='bold')
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plot_base64 = get_plot_base64()
    
    # Analyser le biais/variance
    final_train = train_mean[-1]
    final_test = test_mean[-1]
    gap = final_train - final_test
    
    if gap > 0.1:
        diagnosis = "High Variance (Overfitting)"
    elif final_test < 0.7:
        diagnosis = "High Bias (Underfitting)"
    else:
        diagnosis = "Good Fit"
    
    return {
        'plot': plot_base64,
        'train_sizes': train_sizes.tolist(),
        'train_scores': train_mean.tolist(),
        'test_scores': test_mean.tolist(),
        'final_train_score': round(final_train * 100, 2),
        'final_test_score': round(final_test * 100, 2),
        'diagnosis': diagnosis,
        'dataset': dataset_name,
        'model': model_name
    }


if __name__ == '__main__':
    if len(sys.argv) > 2:
        action = sys.argv[1]
        dataset_name = sys.argv[2]
        model_name = sys.argv[3] if len(sys.argv) > 3 else 'random_forest'
        
        if action == 'importance':
            result = get_feature_importance(dataset_name)
        elif action == 'roc':
            result = get_roc_curves(dataset_name, model_name)
        elif action == 'confusion':
            result = get_confusion_matrix(dataset_name, model_name)
        elif action == 'crossval':
            result = get_cross_validation(dataset_name, model_name)
        elif action == 'learning':
            result = get_learning_curves(dataset_name, model_name)
        else:
            result = {'error': 'Action non reconnue. Utilisez "importance", "roc", "confusion", "crossval" ou "learning".'}
        
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(json.dumps({'error': 'Arguments manquants. Usage: advanced_analysis.py <action> <dataset> [model]'}))
