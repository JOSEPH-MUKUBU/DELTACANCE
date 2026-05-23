#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'analyse des données
"""

import pandas as pd
import numpy as np
import json
import sys
import os
import matplotlib
matplotlib.use('Agg') # Optimisation pour environnement sans affichage
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def generate_plot_image(fig):
    """Convertit une figure matplotlib en image base64"""
    buffer = BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    buffer.close()
    plt.close(fig)
    return f"data:image/png;base64,{image_base64}"

def generate_plots(df, numeric_cols, categorical_cols, target_column, dataset_name):
    """Génère tous les plots et retourne un dictionnaire avec les images base64"""
    plots = {}
    
    # 1. Distribution de la variable cible
    if target_column in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        distribution = df[target_column].value_counts()
        colors = sns.color_palette("husl", len(distribution))
        bars = ax.bar(range(len(distribution)), distribution.values, color=colors)
        ax.set_xticks(range(len(distribution)))
        ax.set_xticklabels(distribution.index, rotation=45, ha='right')
        ax.set_ylabel('Nombre de cas', fontsize=12, fontweight='bold')
        ax.set_title(f'Distribution de la Variable Cible - {dataset_name}', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        # Ajouter les valeurs sur les barres
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontweight='bold')
        plt.tight_layout()
        plots['distribution'] = {
            'image': generate_plot_image(fig),
            'title': 'Distribution de la Variable Cible',
            'description': 'Répartition des classes dans le dataset (Variable Cible). Crucial pour détecter un déséquilibre de classe. Chaque barre représente le nombre de cas pour chaque classe.'
        }
    
    # 2. Histogrammes pour les colonnes numériques
    for col in numeric_cols[:4]:  # Limiter à 4 pour ne pas surcharger
        if col != target_column:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(df[col].dropna(), bins=20, color='steelblue', edgecolor='black', alpha=0.7)
            ax.set_xlabel(col, fontsize=12, fontweight='bold')
            ax.set_ylabel('Fréquence', fontsize=12, fontweight='bold')
            ax.set_title(f'Distribution - {col}', fontsize=14, fontweight='bold')
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            plt.tight_layout()
            plots[f'histogram_{col}'] = {
                'image': generate_plot_image(fig),
                'title': f'Histogramme - {col}',
                'description': f'Distribution des valeurs pour la variable {col}. Permet d\'observer la fréquence et l\'étalement des données.'
            }
    
    # 3. Matrice de corrélation
    if len(numeric_cols) > 1:
        corr_cols = [col for col in numeric_cols if col != target_column]
        if len(corr_cols) >= 2:
            fig, ax = plt.subplots(figsize=(12, 10))
            corr_matrix = df[corr_cols].corr()
            sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                       square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
            ax.set_title('Matrice de Corrélation', fontsize=14, fontweight='bold')
            plt.tight_layout()
            plots['correlation_matrix'] = {
                'image': generate_plot_image(fig),
                'title': 'Matrice de Corrélation',
                'description': 'Montre les relations linéaires entre les variables numériques. Les couleurs chaudes (rouges) indiquent une corrélation positive, les couleurs froides (bleues) une corrélation négative. Les valeurs proches de 1 ou -1 indiquent une forte dépendance.'
            }
    
    # 4. Boîtes à moustaches (Box plots) pour les variables numériques
    if len(numeric_cols) > 1:
        fig, ax = plt.subplots(figsize=(12, 6))
        box_cols = [col for col in numeric_cols[:5] if col != target_column]
        if box_cols:
            df[box_cols].boxplot(ax=ax)
            ax.set_ylabel('Valeurs', fontsize=12, fontweight='bold')
            ax.set_title('Boîtes à Moustaches - Variables Numériques', fontsize=14, fontweight='bold')
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plots['boxplot'] = {
                'image': generate_plot_image(fig),
                'title': 'Boîtes à Moustaches',
                'description': 'Visualise la distribution des variables numériques. La ligne au milieu est la médiane, les boîtes contiennent 50% des données. Les points isolés sont les valeurs aberrantes (outliers).'
            }
    
    # 5. Distribution des variables catégorielles
    cat_display = 0
    for col in categorical_cols:
        if col != target_column and cat_display < 2:  # Limiter à 2 graphes
            fig, ax = plt.subplots(figsize=(10, 6))
            value_counts = df[col].value_counts().head(10)
            colors = sns.color_palette("Set2", len(value_counts))
            bars = ax.barh(range(len(value_counts)), value_counts.values, color=colors)
            ax.set_yticks(range(len(value_counts)))
            ax.set_yticklabels(value_counts.index)
            ax.set_xlabel('Nombre de cas', fontsize=12, fontweight='bold')
            ax.set_title(f'Distribution - {col}', fontsize=14, fontweight='bold')
            ax.grid(axis='x', alpha=0.3, linestyle='--')
            # Ajouter les valeurs
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                       f' {int(width)}',
                       ha='left', va='center', fontweight='bold')
            plt.tight_layout()
            plots[f'categorical_{col}'] = {
                'image': generate_plot_image(fig),
                'title': f'Distribution - {col}',
                'description': f'Répartition des catégories pour {col}. Les barres les plus longues représentent les catégories les plus fréquentes.'
            }
            cat_display += 1
    
    return plots

def analyze_dataset(dataset_name):
    """Analyse un dataset et retourne les statistiques"""
    
    # Sélectionner le bon fichier
    if dataset_name == 'breast_cancer':
        file_path = os.path.join(project_dir, 'Breast_Cancer.csv')
        target_column = 'Status'
    elif dataset_name == 'cancer':
        file_path = os.path.join(project_dir, 'Cancer_Dataset.csv')
        target_column = 'Cancer Prediction Level'
    elif dataset_name == 'hybrid_cancer':
        file_path = os.path.join(project_dir, 'Hybrid_Cancer_Dataset.csv')
        target_column = 'Status'
    else:
        return {}
    
    if not os.path.exists(file_path):
        return {}
    
    # Charger le dataset
    df = pd.read_csv(file_path)
    
    # Statistiques descriptives
    statistics = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        statistics[col] = {
            'mean': float(df[col].mean()),
            'median': float(df[col].median()),
            'std': float(df[col].std()),
            'min': float(df[col].min()),
            'max': float(df[col].max()),
            'missing': int(df[col].isnull().sum())
        }
    
    # Distribution de la variable cible
    distribution = {}
    if target_column in df.columns:
        distribution = df[target_column].value_counts().to_dict()
        distribution = {str(k): int(v) for k, v in distribution.items()}
    
    # Corrélations (pour les colonnes numériques)
    correlations = []
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                correlations.append({
                    'var1': str(corr_matrix.columns[i]),
                    'var2': str(corr_matrix.columns[j]),
                    'value': float(corr_matrix.iloc[i, j])
                })
        # Trier par valeur absolue de corrélation
        correlations.sort(key=lambda x: abs(x['value']), reverse=True)
        correlations = correlations[:10]  # Top 10 corrélations
    
    # Histogrammes pour les colonnes numériques
    histograms = {}
    for col in numeric_cols:
        counts, bin_edges = np.histogram(df[col].dropna(), bins=10)
        histograms[col] = {
            'counts': counts.tolist(),
            'bins': bin_edges.tolist(),
            'description': f"Distribution des valeurs pour la variable {col}. Permet d'observer la fréquence et l'étalement des données."
        }
    
    # Informations générales
    general_info = {
        'shape': list(df.shape),
        'columns': list(df.columns),
        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'missing_values': {col: int(df[col].isnull().sum()) for col in df.columns},
        'duplicates': int(df.duplicated().sum())
    }
    
    # Générer les plots
    numeric_cols_list = list(df.select_dtypes(include=[np.number]).columns)
    categorical_cols_list = list(df.select_dtypes(include=['object']).columns)
    plots = generate_plots(df, numeric_cols_list, categorical_cols_list, target_column, dataset_name)
    
    return {
        'statistics': statistics,
        'distribution': distribution,
        'correlations': correlations,
        'histograms': histograms,
        'general_info': general_info,
        'plots': plots,
        'plot_descriptions': {
            'distribution': "Répartition des classes dans le dataset (Variable Cible). Crucial pour détecter un déséquilibre de classe.",
            'correlations': "Relations linéaires entre les variables numériques. Une valeur proche de 1 ou -1 indique une forte dépendance.",
            'histograms': "Visualisation de la forme de la distribution de chaque variable numérique."
        }
    }

if __name__ == '__main__':
    # Force UTF-8 output without BOM
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    if len(sys.argv) > 1:
        dataset_name = sys.argv[1]
        result = analyze_dataset(dataset_name)
        # Print JSON without BOM and with UTF-8 encoding
        json_output = json.dumps(result, indent=2, ensure_ascii=False)
        sys.stdout.write(json_output)
    else:
        sys.stdout.write(json.dumps({}, indent=2))


