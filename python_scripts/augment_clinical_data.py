#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour créer un dataset hybride en injectant des données de style de vie
dans le dataset clinique, avec des corrélations réalistes.
"""

import pandas as pd
import numpy as np
import os
import sys

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def generate_hybrid_dataset():
    """Génère le dataset hybride"""
    
    print("Chargement du dataset Breast Cancer...")
    base_path = os.path.join(project_dir, 'Breast_Cancer.csv')
    if not os.path.exists(base_path):
        print(f"Erreur: {base_path} non trouvé.")
        return False
        
    df = pd.read_csv(base_path)
    n_samples = len(df)
    
    print(f"Dataset chargé: {n_samples} lignes.")
    
    # Initialisation des nouvelles colonnes
    df['Obesity'] = 'No'
    df['Smoking'] = 'No'
    df['Genetic Risk'] = 'Low'
    
    # Génération probabiliste avec corrélations
    
    # 1. OBÉSITÉ
    # Corrélation avec l'âge : plus élevé après 50 ans
    # Corrélation avec le statut : un peu plus fréquent si décédé
    print("Génération des données 'Obesity'...")
    for idx, row in df.iterrows():
        age = row['Age']
        status = row['Status']
        
        prob_obesity = 0.2  # probabilité de base
        
        if age > 50:
            prob_obesity += 0.15
        
        if status == 'Dead':
            prob_obesity += 0.1
            
        if np.random.random() < prob_obesity:
            df.at[idx, 'Obesity'] = 'Yes'

    # 2. TABAGISME (Smoking)
    # Corrélation avec T Stage (taille tumeur) et Status
    print("Génération des données 'Smoking'...")
    for idx, row in df.iterrows():
        status = row['Status']
        tumor_size = row['Tumor Size']
        
        prob_smoking = 0.15 # probabilité de base (femmes en général moins fumeuses dans certaines stats, à ajuster)
        
        if status == 'Dead':
            prob_smoking += 0.2
            
        # Si tumeur > 30mm, probabilité augmentée
        if tumor_size > 30:
            prob_smoking += 0.15
            
        if np.random.random() < prob_smoking:
            df.at[idx, 'Smoking'] = 'Yes'
            
    # 3. RISQUE GÉNÉTIQUE
    # Corrélation avec Grade (agressivité) et Age (jeunes avec cancer = souvent génétique)
    print("Génération des données 'Genetic Risk'...")
    for idx, row in df.iterrows():
        age = row['Age']
        grade = str(row['Grade']).lower()
        
        # Base probabilities
        probs = {'Low': 0.7, 'Medium': 0.2, 'High': 0.1}
        
        # Ajustements
        if age < 40:
            # Cancer jeune = risque génétique plus probable
            probs['High'] += 0.3
            probs['Medium'] += 0.1
            probs['Low'] -= 0.4
            
        if '3' in grade or 'high' in grade: # Grade plus agressif
            probs['High'] += 0.2
            probs['Low'] -= 0.2
            
        # Normalisation des probabilités
        total = sum(probs.values())
        normalized_probs = [p/total for p in probs.values()]
        
        choice = np.random.choice(['Low', 'Medium', 'High'], p=normalized_probs)
        df.at[idx, 'Genetic Risk'] = choice

    # Sauvegarde
    output_path = os.path.join(project_dir, 'Hybrid_Cancer_Dataset.csv')
    df.to_csv(output_path, index=False)
    
    print(f"Dataset hybride généré avec succès: {output_path}")
    print("Aperçu des nouvelles colonnes:")
    print(df[['Status', 'Age', 'Obesity', 'Smoking', 'Genetic Risk']].head())
    
    return True

if __name__ == '__main__':
    generate_hybrid_dataset()
