#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour générer des rapports PDF de prédiction
"""

import json
import sys
import os
from datetime import datetime

# Check if reportlab is available
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def generate_pdf_report(prediction_data, output_path=None):
    """Génère un rapport PDF pour une prédiction"""
    
    if not REPORTLAB_AVAILABLE:
        return {'error': 'reportlab non installé. Exécutez: pip install reportlab'}
    
    if output_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(project_dir, 'var', 'reports', f'prediction_report_{timestamp}.pdf')
    
    # Créer le dossier si nécessaire
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Créer le document
    doc = SimpleDocTemplate(output_path, pagesize=A4, 
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    
    # Styles personnalisés
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=30,
        textColor=colors.HexColor('#2c3e50')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor('#7f8c8d')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#3498db')
    )
    
    # Contenu du document
    elements = []
    
    # Titre
    elements.append(Paragraph("Rapport de Diagnostic Médical", title_style))
    elements.append(Paragraph("Système d'Aide à la Décision - Cancer AI", subtitle_style))
    elements.append(Spacer(1, 20))
    
    # Date et heure
    date_str = datetime.now().strftime('%d/%m/%Y à %H:%M:%S')
    elements.append(Paragraph(f"<b>Date du rapport:</b> {date_str}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Résultat de la prédiction
    elements.append(Paragraph("Résultat de la Prédiction", heading_style))
    
    prediction = prediction_data.get('prediction', 'N/A')
    probability = prediction_data.get('probability', 0)
    
    # Tableau de résultat
    result_data = [
        ['Diagnostic', str(prediction)],
        ['Probabilité', f"{probability * 100:.1f}%"],
        ['Modèle utilisé', prediction_data.get('model', 'Random Forest')],
        ['Dataset', prediction_data.get('dataset', 'N/A').replace('_', ' ').title()]
    ]
    
    result_table = Table(result_data, colWidths=[6*cm, 10*cm])
    result_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#ecf0f1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
    ]))
    elements.append(result_table)
    elements.append(Spacer(1, 20))
    
    # Données d'entrée
    elements.append(Paragraph("Données du Patient", heading_style))
    
    input_data = prediction_data.get('input_data', {})
    if input_data:
        input_rows = [[k.replace('_', ' ').title(), str(v)] for k, v in input_data.items() 
                      if k not in ['model', 'dataset']]
        if input_rows:
            input_table = Table(input_rows, colWidths=[8*cm, 8*cm])
            input_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7'))
            ]))
            elements.append(input_table)
    
    elements.append(Spacer(1, 30))
    
    # Avertissement
    warning_style = ParagraphStyle(
        'Warning',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#e74c3c'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph(
        "<b>AVERTISSEMENT:</b> Ce rapport est généré par un système d'intelligence artificielle "
        "à des fins d'aide à la décision uniquement. Il ne remplace pas l'avis d'un professionnel de santé qualifié.",
        warning_style
    ))
    
    # Générer le PDF
    doc.build(elements)
    
    return {
        'success': True,
        'path': output_path,
        'filename': os.path.basename(output_path)
    }


def save_prediction_history(prediction_data):
    """Sauvegarde une prédiction dans l'historique"""
    
    history_file = os.path.join(project_dir, 'var', 'prediction_history.json')
    
    # Créer le dossier si nécessaire
    os.makedirs(os.path.dirname(history_file), exist_ok=True)
    
    # Charger l'historique existant
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
    
    # Ajouter la nouvelle prédiction
    entry = {
        'id': len(history) + 1,
        'timestamp': datetime.now().isoformat(),
        'prediction': prediction_data.get('prediction'),
        'probability': prediction_data.get('probability'),
        'model': prediction_data.get('model', 'random_forest'),
        'dataset': prediction_data.get('dataset', 'breast_cancer'),
        'input_data': prediction_data.get('input_data', {})
    }
    
    history.append(entry)
    
    # Garder les 100 dernières entrées
    history = history[-100:]
    
    # Sauvegarder
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    return {'success': True, 'id': entry['id']}


def get_prediction_history():
    """Récupère l'historique des prédictions"""
    
    history_file = os.path.join(project_dir, 'var', 'prediction_history.json')
    
    if not os.path.exists(history_file):
        return {'history': [], 'count': 0}
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        return {'history': list(reversed(history)), 'count': len(history)}
    except:
        return {'history': [], 'count': 0, 'error': 'Erreur de lecture'}


def clear_prediction_history():
    """Efface l'historique des prédictions"""
    
    history_file = os.path.join(project_dir, 'var', 'prediction_history.json')
    
    if os.path.exists(history_file):
        os.remove(history_file)
    
    return {'success': True}


if __name__ == '__main__':
    if len(sys.argv) > 1:
        action = sys.argv[1]
        
        if action == 'generate_pdf':
            if len(sys.argv) > 2:
                input_file = sys.argv[2]
                with open(input_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                result = generate_pdf_report(data)
            else:
                result = {'error': 'Fichier de données manquant'}
        
        elif action == 'save_history':
            if len(sys.argv) > 2:
                input_file = sys.argv[2]
                with open(input_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                result = save_prediction_history(data)
            else:
                result = {'error': 'Données manquantes'}
        
        elif action == 'get_history':
            result = get_prediction_history()
        
        elif action == 'clear_history':
            result = clear_prediction_history()
        
        else:
            result = {'error': 'Action non reconnue'}
        
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(json.dumps({'error': 'Action manquante'}))
