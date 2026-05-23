#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prédiction évolué
"""

import pandas as pd
import numpy as np
import json
import sys
import os
import joblib

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def predict(model_name='random_forest', dataset_name='breast_cancer', input_data=None):
    """Effectue une prédiction avec traitement des entrées"""
    
    # 1. Charger les métadonnées et les objets
    objects_dir = os.path.join(project_dir, 'python_scripts', 'transform_objects', dataset_name)
    metadata_path = os.path.join(objects_dir, 'metadata.json')
    
    if not os.path.exists(metadata_path):
        return {'error': 'Métadonnées non trouvées. Veuillez ré-entraîner les modèles.'}
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    # Charger le modèle
    model_path = os.path.join(project_dir, 'python_scripts', f'model_{model_name}_{dataset_name}.joblib')
    if not os.path.exists(model_path):
        return {'error': f'Modèle {model_name} pour {dataset_name} non trouvé.'}
    
    model = joblib.load(model_path)
    
    # 2. Préparer les données d'entrée
    features = metadata['features']
    input_df = pd.DataFrame(columns=features)
    
    # Mapping des noms de champs du formulaire vers les colonnes du dataset (si différent)
    field_mapping = {
        'smoking': 'Smoking',
        'obesity': 'Obesity',
        'genetic_risk': 'Genetic Risk',
        'gender': 'gender',
        'age': 'Age',
        'tumor_size': 'Tumor Size',
        'grade': 'Grade',
        'estrogen_status': 'Estrogen Status'
    }
    
    # Créer une ligne de données
    row = {}
    for feat in features:
        # Chercher dans input_data via le mapping ou directement
        form_val = None
        for form_key, dataset_col in field_mapping.items():
            if dataset_col == feat:
                form_val = input_data.get(form_key)
                break
        
        if form_val is None:
            form_val = input_data.get(feat)
            
        row[feat] = form_val

    # 3. Appliquer les transformations
    for feat in metadata['categorical_features']:
        encoder_path = os.path.join(objects_dir, f'encoder_{feat}.joblib')
        if os.path.exists(encoder_path):
            le = joblib.load(encoder_path)
            val = str(row.get(feat, ''))
            # Gérer les valeurs inconnues
            if val not in le.classes_:
                val = le.classes_[0] # Fallback
            row[feat] = le.transform([val])[0]
            
    # Convertir en DataFrame
    df_pred = pd.DataFrame([row])[features]
    
    # Numérisation forcée pour les colonnes numériques avant scaling
    for col in df_pred.columns:
        if col not in metadata['categorical_features']:
            df_pred[col] = pd.to_numeric(df_pred[col], errors='coerce').fillna(0)

    # Scaling
    scaler_path = os.path.join(objects_dir, 'scaler.joblib')
    if os.path.exists(scaler_path) and metadata.get('normalized_features'):
        scaler = joblib.load(scaler_path)
        norm_feats = metadata['normalized_features']
        df_pred[norm_feats] = scaler.transform(df_pred[norm_feats])
        
    # 4. Prédiction
    prediction_idx = model.predict(df_pred)[0]
    probability = model.predict_proba(df_pred)[0]
    
    # Décoder le résultat
    target_le_path = os.path.join(objects_dir, 'encoder_target.joblib')
    if os.path.exists(target_le_path):
        target_le = joblib.load(target_le_path)
        prediction_label = target_le.inverse_transform([prediction_idx])[0]
    else:
        prediction_label = str(prediction_idx)
    
    # Générer une suggestion
    suggestion = get_suggestion(prediction_label, dataset_name, float(max(probability)))

    return {
        'prediction': prediction_label,
        'probability': float(max(probability)),
        'suggestion': suggestion,
        'all_probabilities': {target_le.classes_[i]: float(probability[i]) for i in range(len(probability))} if os.path.exists(target_le_path) else {}
    }

def get_suggestion(prediction, dataset_name, probability):
    """Génère une recommandation basée sur la prédiction et la probabilité"""
    
    # Déterminer le niveau de confiance
    confidence_text = ""
    if probability >= 0.85:
        confidence_text = " <strong>(Fiabilité: Haute)</strong>."
    elif probability >= 0.60:
        confidence_text = " <strong>(Fiabilité: Modérée)</strong>."
    else:
        confidence_text = " <strong>(Fiabilité: Faible - À confirmer)</strong>."

    # Nettoyage des entrées pour robustesse
    dataset_name = dataset_name.strip()
    prediction_clean = str(prediction).strip()
    
    if dataset_name == 'breast_cancer':
        if prediction_clean == 'Alive':
            return {
                'title': 'Prognostic Favorable',
                'bg_class': 'success',
                'icon': 'fa-check-circle',
                'text': f'Le modèle prédit une issue favorable avec une confiance de {int(probability*100)}%{confidence_text} Cependant, un suivi régulier reste indispensable. Continuez les contrôles de routine.'
            }
        else:
             return {
                'title': 'Attention Requise',
                'bg_class': 'danger',
                'icon': 'fa-exclamation-triangle',
                'text': f'Le modèle prédit un risque élevé avec une confiance de {int(probability*100)}%{confidence_text} Une consultation immédiate avec un oncologue est recommandée pour des examens approfondis.'
            }
    
    elif dataset_name in ['cancer', 'hybrid_cancer']:
        # Case insensitive matching
        pred_lower = prediction_clean.lower()
        
        if pred_lower == 'low':
            base_text = 'Continuez vos bonnes habitudes de vie (alimentation équilibrée, activité physique).'
            if probability < 0.6:
                base_text += ' Le résultat étant incertain, restez vigilant sur les symptômes.'
            else:
                base_text += ' Aucun changement majeur n\'est requis.'
                
            return {
                'title': 'Risque Faible',
                'bg_class': 'success',
                'icon': 'fa-shield-alt',
                'text': f'{base_text} (Confiance: {int(probability*100)}%)'
            }
        elif pred_lower == 'medium':
             advice = ""
             if probability > 0.8:
                 advice = "Les indicateurs sont clairs. "
             
             return {
                'title': 'Risque Modéré',
                'bg_class': 'warning',
                'icon': 'fa-exclamation-circle',
                'text': f'{advice}Certains facteurs de risque sont présents. Envisagez de réduire la consommation d\'alcool/tabac et d\'améliorer votre alimentation. (Confiance: {int(probability*100)}%)'
            }
        elif pred_lower == 'high':
             urgency = "Il est fortement conseillé"
             if probability > 0.9:
                 urgency = "URGENT : Il est impératif"
                 
             return {
                'title': 'Risque Élevé',
                'bg_class': 'danger',
                'icon': 'fa-procedures',
                'text': f'Facteurs de risque critiques détectés. {urgency} de consulter un médecin pour un bilan de santé complet. (Confiance: {int(probability*100)}%)'
            }
            
    return {
        'title': 'Analyse Terminée', 
        'bg_class': 'secondary', 
        'icon': 'fa-info-circle', 
        'text': f'Résultat: {prediction_clean} (Dataset: {dataset_name}). Confiance: {int(probability*100)}%.'
    }

if __name__ == '__main__':
    # Force UTF-8 output without BOM
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        if os.path.exists(input_file):
            with open(input_file, 'r') as f:
                input_data = json.load(f)
            
            model_name = input_data.get('model', 'random_forest')
            dataset_name = input_data.get('dataset', 'breast_cancer')
            
            result = predict(model_name, dataset_name, input_data)
            # Print JSON without BOM and with UTF-8 encoding
            json_output = json.dumps(result, indent=2, ensure_ascii=False)
            sys.stdout.write(json_output)
        else:
            sys.stdout.write(json.dumps({'error': 'Fichier d\'entrée non trouvé'}, indent=2))
    else:
        sys.stdout.write(json.dumps({'error': 'Arguments manquants'}, indent=2))


