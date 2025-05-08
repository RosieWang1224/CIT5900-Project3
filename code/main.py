import pandas as pd
from enrich_all_csv_files import enrich_csv
from build_metadata import build_project_metadata_dict
from filter_all_csv_files import filter_csv
from visualizations import visualize_csv
# Importing Section 2 scripts
from regression_model import main as run_regression
from PCA import main as run_pca
from clustering_techniques import main as run_clustering
from text_processing import main as run_text_processing

def load_and_normalize_title(filepath):
    df = pd.read_csv(filepath)
    for col in ["title", "Title", "OutputTitle"]:
        if col in df.columns:
            df["title"] = df[col]
            df["normalized_title"] = df[col].astype(str).str.lower().str.strip()
            return df
    raise ValueError(f"No title column found in {filepath}")

# List of files
files = [f"group{i}.csv" for i in range(1, 9)]

# Load and normalize "title" in files
all_dfs = [load_and_normalize_title(file) for file in files]

# Concatenate and remove duplicates
combined_df = pd.concat(all_dfs, ignore_index=True)
deduped_df = combined_df.drop_duplicates(subset="normalized_title").reset_index(drop=True)
deduped_df["title"] = deduped_df["normalized_title"]

enrich_csv(deduped_df, "Group4_Enriched.csv")
filter_csv("Group4_Enriched.csv", "ResearchOutputs_Group4.csv")
visualize_csv("ResearchOutputs_Group4.csv")

# Download NLTK resources for text processing
try:
    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('stopwords')
    print("NLTK resources downloaded successfully")
except Exception as e:
    print(f"Error downloading NLTK resources: {e}")

# Bullet Point 1: Regression Modeling
try:
    run_regression()
    print("Regression modeling completed. Figure saved as regression_plot.png")
except Exception as e:
    print(f"Error in regression modeling: {e}")

# Bullet Point 2: PCA Analysis
try:
    run_pca()
    print("PCA analysis completed. Figure saved as pca_plot.png")
except Exception as e:
    print(f"Error in PCA analysis: {e}")

# Bullet Point 3: Clustering Analysis
try:
    run_clustering()
    print("Clustering analysis completed. Figure saved as clustering_plot.png")
except Exception as e:
    print(f"Error in clustering analysis: {e}")

# Bullet Point 4: Text Processing
try:
    run_text_processing()
    print("Text processing completed. Figure saved as text_plot.png")
except Exception as e:
    print(f"Error in text processing: {e}")Outputs_Group4.csv")
visualize_csv("ResearchOutputs_Group4.csv")