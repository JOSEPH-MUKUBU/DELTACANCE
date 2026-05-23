#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour enrichir les datasets avec des données synthétiques
contenant des valeurs manquantes et aberrantes
"""

import pandas as pd
import numpy as np
import random
import os

project_dir = os.path.dirname(os.path.abspath(__file__))

def add_synthetic_breast_cancer_data(n_rows=50):
    """Ajoute des lignes synthétiques au dataset Breast Cancer"""
    file_path = os.path.join(project_dir, '..', 'Breast_Cancer.csv')
    df = pd.read_csv(file_path)
    
    # Valeurs possibles pour les colonnes catégorielles
    races = ['White', 'Black', 'Other', None]  # None = valeur manquante
    marital_statuses = ['Married', 'Single', 'Divorced', 'Widowed', None]
    t_stages = ['T1', 'T2', 'T3', 'T4', None]
    n_stages = ['N1', 'N2', 'N3', None]
    stages_6th = ['IIA', 'IIB', 'IIIA', 'IIIB', 'IIIC', None]
    differentiates = ['Well differentiated', 'Moderately differentiated', 'Poorly differentiated', 'Undifferentiated', None]
    grades = [' Grade I', ' Grade II', ' Grade III', None]
    a_stages = ['Regional', 'Distant', None]
    estrogen_statuses = ['Positive', 'Negative', None]
    progesterone_statuses = ['Positive', 'Negative', None]
    statuses = ['Alive', 'Dead']
    
    synthetic_rows = []
    for i in range(n_rows):
        row = {
            'Age': random.choice([random.randint(25, 90), None, 150, -5]),  # Inclut outliers et None
            'Race': random.choice(races),
            'Marital Status': random.choice(marital_statuses),
            'T Stage ': random.choice(t_stages),
            'N Stage': random.choice(n_stages),
            '6th Stage': random.choice(stages_6th),
            'differentiate': random.choice(differentiates),
            'Grade': random.choice(grades),
            'A Stage': random.choice(a_stages),
            'Tumor Size': random.choice([random.randint(1, 150), None, 500, -10]),  # Outliers
            'Estrogen Status': random.choice(estrogen_statuses),
            'Progesterone Status': random.choice(progesterone_statuses),
            'Regional Node Examined': random.choice([random.randint(1, 50), None, 200]),
            'Reginol Node Positive': random.choice([random.randint(0, 30), None, 100]),
            'Survival Months': random.choice([random.randint(1, 120), None, 300]),
            'Status': random.choice(statuses)
        }
        synthetic_rows.append(row)
    
    synthetic_df = pd.DataFrame(synthetic_rows)
    enriched_df = pd.concat([df, synthetic_df], ignore_index=True)
    
    # Sauvegarder
    enriched_df.to_csv(file_path, index=False)
    print(f"Breast Cancer Dataset enrichi: {len(df)} -> {len(enriched_df)} lignes")
    return len(enriched_df) - len(df)


def add_synthetic_cancer_data(n_rows=50):
    """Ajoute des lignes synthétiques au dataset Cancer"""
    file_path = os.path.join(project_dir, '..', 'Cancer_Dataset.csv')
    df = pd.read_csv(file_path)
    
    # Valeurs possibles
    genders = ['Male', 'Female', 'male', 'female', 'M', 'F', None]  # Incohérences volontaires
    obesities = ['Yes', 'No', None]
    smokings = ['Yes', 'No', None]
    genetic_risks = ['Low', 'Medium', 'High', None]
    cancer_levels = ['Low', 'Medium', 'High']
    
    # Générer des dates de naissance aléatoires (certaines invalides)
    def random_birthdate():
        if random.random() < 0.1:
            return None
        if random.random() < 0.05:
            return "invalid_date"
        year = random.randint(1940, 2010)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{year}-{month:02d}-{day:02d}"
    
    synthetic_rows = []
    max_id = df['PatientID'].max() if not df['PatientID'].isna().all() else 0
    
    for i in range(n_rows):
        row = {
            'PatientID': random.choice([max_id + i + 1, None, -1]),  # ID invalide possible
            'first_name': random.choice(['Jean', 'Marie', 'Pierre', 'Sophie', None, '']),
            'last_name': random.choice(['Dupont', 'Martin', 'Bernard', None, '']),
            'BirthDate': random_birthdate(),
            'gender': random.choice(genders),
            'Obesity': random.choice(obesities),
            'Smoking': random.choice(smokings),
            'Genetic Risk': random.choice(genetic_risks),
            'Cancer Prediction Level': random.choice(cancer_levels)
        }
        synthetic_rows.append(row)
    
    synthetic_df = pd.DataFrame(synthetic_rows)
    enriched_df = pd.concat([df, synthetic_df], ignore_index=True)
    
    # Sauvegarder
    enriched_df.to_csv(file_path, index=False)
    print(f"Cancer Dataset enrichi: {len(df)} -> {len(enriched_df)} lignes")
    return len(enriched_df) - len(df)


if __name__ == '__main__':
    print("=== Enrichissement des datasets ===")
    added_bc = add_synthetic_breast_cancer_data(50)
    added_c = add_synthetic_cancer_data(50)
    print(f"\nTotal: {added_bc + added_c} nouvelles lignes ajoutées")
    print("Les datasets contiennent maintenant des valeurs manquantes et aberrantes.")
