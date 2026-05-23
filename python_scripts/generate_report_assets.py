import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
images_dir = os.path.join(project_dir, 'images')

if not os.path.exists(images_dir):
    os.makedirs(images_dir)

def save_plot(fig, filename):
    path = os.path.join(images_dir, filename)
    fig.savefig(path, bbox_inches='tight', dpi=150)
    plt.close(fig)
    print(f"Saved: {path}")

def generate_assets(dataset_name):
    if dataset_name == 'breast_cancer':
        file_path = os.path.join(project_dir, 'Breast_Cancer.csv')
        target_col = 'Status'
    else:
        file_path = os.path.join(project_dir, 'Cancer_Dataset.csv')
        target_col = 'Cancer Prediction Level'

    df = pd.read_csv(file_path)
    
    # 1. Target Distribution
    fig, ax = plt.subplots(figsize=(8, 5))
    df[target_col].value_counts().plot(kind='bar', ax=ax, color=sns.color_palette("husl"))
    ax.set_title(f'Distribution de {target_col} ({dataset_name})')
    save_plot(fig, f'dist_{dataset_name}.png')

    # 2. Correlation Matrix
    numeric_df = df.select_dtypes(include=['number'])
    if not numeric_df.empty:
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', ax=ax)
        ax.set_title(f'Correlation Matrix ({dataset_name})')
        save_plot(fig, f'corr_{dataset_name}.png')

    # 3. Example Histograms
    if dataset_name == 'breast_cancer':
        cols = ['Age', 'Tumor Size']
    else:
        # Check available numeric cols for cancer dataset
        cols = [c for c in numeric_df.columns if c != 'PatientID'][:2]
    
    for col in cols:
        if col in df.columns:
            fig, ax = plt.subplots(figsize=(8, 5))
            df[col].hist(ax=ax, bins=20)
            ax.set_title(f'Distribution de {col} ({dataset_name})')
            save_plot(fig, f'hist_{dataset_name}_{col.replace(" ", "_")}.png')

if __name__ == "__main__":
    generate_assets('breast_cancer')
    generate_assets('cancer')
