#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour obtenir les informations sur les datasets
"""

import pandas as pd
import numpy as np
import json
import sys
import os
import io

# Force UTF-8 environment
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Définir le chemin du projet
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class NumpyEncoder(json.JSONEncoder):
    """Encodage JSON pour les types NumPy"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

def get_dataset_info():
    """Retourne les informations sur les datasets"""
    
    datasets_info = {}
    
    # Dataset Breast Cancer
    breast_cancer_path = os.path.join(project_dir, 'Breast_Cancer.csv')
    if os.path.exists(breast_cancer_path):
        df_breast = pd.read_csv(breast_cancer_path)
        datasets_info['breast_cancer'] = {
            'name': 'Breast Cancer Dataset',
            'file': 'Breast_Cancer.csv',
            'description': 'Dataset sur le cancer du sein avec caractéristiques cliniques et pathologiques',
            'instances': len(df_breast),
            'attributes': len(df_breast.columns),
            'columns': list(df_breast.columns),
            'target': 'Status',
            'numeric_columns': list(df_breast.select_dtypes(include=['int64', 'float64']).columns),
            'categorical_columns': list(df_breast.select_dtypes(include=['object']).columns)
        }
    
    # Dataset Cancer
    cancer_path = os.path.join(project_dir, 'Cancer_Dataset.csv')
    if os.path.exists(cancer_path):
        df_cancer = pd.read_csv(cancer_path)
        datasets_info['cancer'] = {
            'name': 'Cancer Dataset',
            'file': 'Cancer_Dataset.csv',
            'description': 'Dataset sur les patients avec facteurs de risque et niveau de prédiction',
            'instances': len(df_cancer),
            'attributes': len(df_cancer.columns),
            'columns': list(df_cancer.columns),
            'target': 'Cancer Prediction Level',
            'numeric_columns': list(df_cancer.select_dtypes(include=['int64', 'float64']).columns),
            'categorical_columns': list(df_cancer.select_dtypes(include=['object']).columns)
        }
    
    # Dataset Hybrid Cancer
    hybrid_path = os.path.join(project_dir, 'Hybrid_Cancer_Dataset.csv')
    if os.path.exists(hybrid_path):
        df_hybrid = pd.read_csv(hybrid_path)
        datasets_info['hybrid_cancer'] = {
            'name': 'Hybrid Dataset (Fusion)',
            'file': 'Hybrid_Cancer_Dataset.csv',
            'description': 'Dataset Clinique enrichi avec facteurs de risque (Obésité, Tabac, Génétique)',
            'instances': len(df_hybrid),
            'attributes': len(df_hybrid.columns),
            'columns': list(df_hybrid.columns),
            'target': 'Status',
            'numeric_columns': list(df_hybrid.select_dtypes(include=['int64', 'float64']).columns),
            'categorical_columns': list(df_hybrid.select_dtypes(include=['object']).columns)
        }
    
    return datasets_info


def read_csv_robust(path, limit=None):
    """Lit un CSV avec plusieurs encodages possibles"""
    encodings = ['utf-8', 'latin1', 'cp1252', 'ISO-8859-1']
    
    for encoding in encodings:
        try:
            return pd.read_csv(path, nrows=limit, encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("Impossible de lire le fichier avec les encodages standards.")

def get_dataset_preview(dataset_name, limit=100):
    """Retourne un aperçu des données brutes avec une limite"""
    
    file_map = {
        'breast_cancer': 'Breast_Cancer.csv',
        'cancer': 'Cancer_Dataset.csv',
        'hybrid_cancer': 'Hybrid_Cancer_Dataset.csv'
    }
    
    if dataset_name not in file_map:
        return {'error': 'Dataset non trouvé'}
        
    file_path = os.path.join(project_dir, file_map[dataset_name])
    
    if not os.path.exists(file_path):
        return {'error': 'Fichier non trouvé'}
        
    try:
        # Lire avec Pandas avec limite et gestion encodage
        df = read_csv_robust(file_path, limit if limit > 0 else None)
        
        # Remplacer les NaN par null/None pour JSON
        df = df.where(pd.notnull(df), None)
        
        return {
            'columns': list(df.columns),
            'data': df.values.tolist(),
            'total_rows': len(df),
            'dataset': dataset_name
        }
    except Exception as e:
        return {'error': str(e)}

def get_dataset_operation(dataset_name, operation):
    """Effectue une opération spécifique sur le dataset"""
    
    file_map = {
        'breast_cancer': 'Breast_Cancer.csv',
        'cancer': 'Cancer_Dataset.csv',
        'hybrid_cancer': 'Hybrid_Cancer_Dataset.csv'
    }
    
    if dataset_name not in file_map:
        return {'error': 'Dataset non trouvé'}
        
    file_path = os.path.join(project_dir, file_map[dataset_name])
    
    if not os.path.exists(file_path):
        return {'error': 'Fichier non trouvé'}
        
    try:
        # Lire avec Pandas robustement
        df = read_csv_robust(file_path)
        
        result = {'type': operation}
        
        if operation == 'tail':
            # Dernières 10 lignes
            data = df.tail(10)
            data = data.where(pd.notnull(data), None)
            result['columns'] = list(data.columns)
            result['data'] = data.values.tolist()
            
        elif operation == 'sample':
            # 10 lignes aléatoires
            data = df.sample(n=min(10, len(df)))
            data = data.where(pd.notnull(data), None)
            result['columns'] = list(data.columns)
            result['data'] = data.values.tolist()
            
        elif operation == 'columns':
            result['data'] = list(df.columns)
            
        elif operation == 'info':
            # Info structurée
            memory_usage = df.memory_usage(deep=True).sum() / 1024 # KB
            
            summary = {
                'rows': len(df),
                'columns': len(df.columns),
                'memory_usage': f"{memory_usage:.2f} KB"
            }
            
            columns_info = []
            for col in df.columns:
                non_null = int(df[col].count())
                total = len(df)
                null_pct = round((total - non_null) / total * 100, 1)
                dtype = str(df[col].dtype)
                
                columns_info.append({
                    'column': col,
                    'non_null_count': non_null,
                    'null_percentage': null_pct,
                    'dtype': dtype
                })
                
            result['data'] = columns_info
            result['summary'] = summary
            result['structure'] = 'detailed_info'
            
        elif operation == 'describe':
            # Statistiques descriptives
            desc = df.describe(include='all')
            # Convertir en object pour permettre None
            desc = desc.astype(object)
            desc = desc.where(pd.notnull(desc), None)
            
            # Ajouter l'index (mean, std, min...) comme colonne
            desc['stat'] = desc.index
            cols = ['stat'] + [c for c in desc.columns if c != 'stat']
            desc = desc[cols]
            
            result['columns'] = list(desc.columns)
            result['data'] = desc.values.tolist()
            
        elif operation == 'dtypes':
            dtypes = df.dtypes.apply(lambda x: str(x)).to_dict()
            result['data'] = [{'column': k, 'type': v} for k, v in dtypes.items()]
            
        elif operation == 'isnull':
            nulls = df.isnull().sum().to_dict()
            result['data'] = [{'column': k, 'missing': int(v), 'percentage': round(v/len(df)*100, 2)} for k, v in nulls.items()]
            
        else:
            return {'error': 'Opération non reconnue'}
            
        return result
        
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'preview':
        dataset_name = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 100
        print(json.dumps(get_dataset_preview(dataset_name, limit), indent=2, ensure_ascii=False, cls=NumpyEncoder))
    elif len(sys.argv) > 2 and sys.argv[1] == 'operation':
        dataset_name = sys.argv[2]
        operation = sys.argv[3]
        print(json.dumps(get_dataset_operation(dataset_name, operation), indent=2, ensure_ascii=False, cls=NumpyEncoder))
    else:
        info = get_dataset_info()
        print(json.dumps(info, indent=2, ensure_ascii=False, cls=NumpyEncoder))


